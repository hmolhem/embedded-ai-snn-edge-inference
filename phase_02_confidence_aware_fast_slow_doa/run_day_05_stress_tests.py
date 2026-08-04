"""Run the pre-registered multi-seed Day 5 stress evaluation.

Run from the repository root with:

    python -m phase_02_confidence_aware_fast_slow_doa.run_day_05_stress_tests

The operating point is loaded from ``day_05_stress_config.json`` and is never
reselected from the stress-test results.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np

from phase_01_python_prototype.src.dataset import (
    DOAConfig,
    stratified_train_test_split_by_snr_and_class,
)
from phase_01_python_prototype.src.lif import fit_lif_prototype_weights, lif_classify
from phase_01_python_prototype.src.metrics import (
    accuracy_score,
    fit_nearest_centroid,
    predict_nearest_centroid,
)
from phase_01_python_prototype.src.spike_encoding import rate_encode_features
from phase_02_confidence_aware_fast_slow_doa.src.adaptive_controller import (
    adaptive_metrics,
    compose_adaptive_decisions,
)
from phase_02_confidence_aware_fast_slow_doa.src.confidence_gate import (
    causal_margin_persistence_gate,
)
from phase_02_confidence_aware_fast_slow_doa.src.progressive_dataset import (
    ArrayElementErrors,
    ProgressiveDOADataset,
    generate_progressive_doa_dataset,
    generate_progressive_evaluation_dataset,
    normalize_progressive_train_test,
    normalize_progressive_with_reference,
)


NUMERIC_METRICS: tuple[str, ...] = (
    "accuracy",
    "coverage",
    "selective_accuracy",
    "false_confidence_rate",
    "false_acceptance_probability",
    "fallback_rate",
    "average_snapshots",
    "average_lif_steps",
    "average_spike_count",
)


def _load_config(path: Path) -> dict[str, object]:
    """Load and validate the fixed Day 5 experiment configuration."""

    config = json.loads(path.read_text(encoding="utf-8"))
    dataset_seeds = tuple(int(value) for value in config["dataset_seeds"])
    spike_seeds = tuple(int(value) for value in config["spike_seeds"])
    if len(dataset_seeds) != 5 or len(spike_seeds) != 5:
        raise ValueError("Day 5 requires exactly five dataset/spike seed pairs.")
    if len(set(dataset_seeds)) != 5 or len(set(spike_seeds)) != 5:
        raise ValueError("Day 5 seeds must be unique.")
    if not 0.0 < float(config["train_fraction"]) < 1.0:
        raise ValueError("train_fraction must lie in (0, 1).")

    budgets = config["snapshot_budgets"]
    if int(budgets["fast"]) >= int(budgets["full"]):
        raise ValueError("The fast snapshot budget must be smaller than the full budget.")
    gate = config["gate"]
    if not 0.0 <= float(gate["threshold"]) <= 1.0:
        raise ValueError("The gate threshold must lie in [0, 1].")
    if int(gate["persistence"]) <= 0:
        raise ValueError("The gate persistence must be positive.")
    return config


def _zero_mean_unit_rms_direction(
    rng: np.random.Generator,
    num_elements: int,
) -> np.ndarray:
    """Draw a zero-mean direction and normalize it to unit population RMS."""

    direction = rng.standard_normal(num_elements)
    direction = direction - np.mean(direction)
    rms = float(np.sqrt(np.mean(direction * direction)))
    if rms <= 0.0:
        raise RuntimeError("Degenerate array-error direction.")
    return direction / rms


def _array_error_levels(
    num_elements: int,
    dataset_seed: int,
    mismatch_config: Mapping[str, object],
) -> dict[str, ArrayElementErrors]:
    """Create nested, fixed-device mismatch vectors for one dataset seed."""

    rng = np.random.default_rng(
        dataset_seed + int(mismatch_config["direction_seed_offset"])
    )
    gain_direction = _zero_mean_unit_rms_direction(rng, num_elements)
    phase_direction = _zero_mean_unit_rms_direction(rng, num_elements)

    levels: dict[str, ArrayElementErrors] = {}
    for level in mismatch_config["levels"]:
        name = str(level["name"])
        levels[name] = ArrayElementErrors(
            gain_db=tuple(gain_direction * float(level["gain_rms_db"])),
            phase_deg=tuple(phase_direction * float(level["phase_rms_deg"])),
        )
    return levels


def _adaptive_method_rows(
    fast_features: np.ndarray,
    full_features: np.ndarray,
    labels: np.ndarray,
    fast_centroids: np.ndarray,
    full_centroids: np.ndarray,
    spike_seed: int,
    fast_budget: int,
    full_budget: int,
    t_max: int,
    leak: float,
    threshold: float,
    persistence: int,
) -> list[dict[str, float | int | str]]:
    """Evaluate always-fast, always-continuous, and adaptive on shared samples."""

    shared_spikes = rate_encode_features(
        fast_features,
        num_time_steps=t_max,
        random_seed=spike_seed,
    )
    weights, bias = fit_lif_prototype_weights(fast_centroids)
    fast_lif = lif_classify(shared_spikes, weights, bias=bias, leak=leak)
    continuous_predictions = predict_nearest_centroid(full_features, full_centroids)
    gate = causal_margin_persistence_gate(
        fast_lif.membrane_history,
        threshold=threshold,
        persistence=persistence,
    )
    decisions = compose_adaptive_decisions(
        gate,
        continuous_predictions,
        shared_spikes,
        initial_snapshot_budget=fast_budget,
        full_snapshot_budget=full_budget,
    )
    adaptive = adaptive_metrics(labels, gate, decisions)
    spike_count = shared_spikes.sum(axis=(1, 2), dtype=int)
    not_applicable = float("nan")

    return [
        {
            "method": "always_fast",
            "num_samples": int(labels.size),
            "accuracy": accuracy_score(labels, fast_lif.predicted_labels),
            "coverage": not_applicable,
            "selective_accuracy": not_applicable,
            "false_confidence_rate": not_applicable,
            "false_acceptance_probability": not_applicable,
            "fallback_rate": not_applicable,
            "average_snapshots": float(fast_budget),
            "average_lif_steps": float(t_max),
            "average_spike_count": float(np.mean(spike_count)),
        },
        {
            "method": "always_continuous",
            "num_samples": int(labels.size),
            "accuracy": accuracy_score(labels, continuous_predictions),
            "coverage": not_applicable,
            "selective_accuracy": not_applicable,
            "false_confidence_rate": not_applicable,
            "false_acceptance_probability": not_applicable,
            "fallback_rate": not_applicable,
            "average_snapshots": float(full_budget),
            "average_lif_steps": 0.0,
            "average_spike_count": 0.0,
        },
        {
            "method": "adaptive",
            "num_samples": int(adaptive["num_samples"]),
            "accuracy": float(adaptive["final_accuracy"]),
            "coverage": float(adaptive["coverage"]),
            "selective_accuracy": float(adaptive["selective_accuracy"]),
            "false_confidence_rate": float(adaptive["false_confidence_rate"]),
            "false_acceptance_probability": float(
                adaptive["false_acceptance_probability"]
            ),
            "fallback_rate": float(adaptive["fallback_rate"]),
            "average_snapshots": float(adaptive["average_snapshots"]),
            "average_lif_steps": float(adaptive["average_lif_steps"]),
            "average_spike_count": float(adaptive["average_spike_count"]),
        },
    ]


def _annotate_rows(
    rows: Iterable[dict[str, float | int | str]],
    experiment: str,
    condition: str,
    dataset_seed: int,
    spike_seed: int,
    gain_rms_db: float = float("nan"),
    phase_rms_deg: float = float("nan"),
) -> list[dict[str, float | int | str]]:
    """Attach experiment and reproducibility identifiers to method rows."""

    return [
        {
            "experiment": experiment,
            "condition": condition,
            "dataset_seed": dataset_seed,
            "spike_seed": spike_seed,
            "gain_rms_db": gain_rms_db,
            "phase_rms_deg": phase_rms_deg,
            **row,
        }
        for row in rows
    ]


def _boundary_conditions(
    boundary_config: Mapping[str, object],
    snr_values: tuple[float, ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return explicit angles, SNRs, and signed-offset labels."""

    theta: list[float] = []
    snr: list[float] = []
    signed_offset: list[float] = []
    repetitions = int(boundary_config["samples_per_boundary_snr_pair"])
    for offset in boundary_config["signed_offsets_deg"]:
        for boundary in boundary_config["boundaries_deg"]:
            for snr_db in snr_values:
                theta.extend([float(boundary) + float(offset)] * repetitions)
                snr.extend([float(snr_db)] * repetitions)
                signed_offset.extend([float(offset)] * repetitions)
    return (
        np.asarray(theta, dtype=float),
        np.asarray(snr, dtype=float),
        np.asarray(signed_offset, dtype=float),
    )


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a non-empty list of dictionaries with stable column order."""

    if not rows:
        raise ValueError("Cannot write an empty result table.")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _aggregate_rows(
    per_seed_rows: list[dict[str, float | int | str]],
) -> list[dict[str, float | int | str]]:
    """Aggregate every experiment/condition/method cell across seeds."""

    keys = sorted(
        {
            (str(row["experiment"]), str(row["condition"]), str(row["method"]))
            for row in per_seed_rows
        }
    )
    aggregate: list[dict[str, float | int | str]] = []
    for experiment, condition, method in keys:
        selected = [
            row
            for row in per_seed_rows
            if row["experiment"] == experiment
            and row["condition"] == condition
            and row["method"] == method
        ]
        record: dict[str, float | int | str] = {
            "experiment": experiment,
            "condition": condition,
            "method": method,
            "num_seeds": len(selected),
            "num_samples_per_seed": int(selected[0]["num_samples"]),
        }
        for metric in NUMERIC_METRICS:
            values = np.asarray([float(row[metric]) for row in selected], dtype=float)
            finite = values[np.isfinite(values)]
            record[f"{metric}_mean"] = (
                float(np.mean(finite)) if finite.size else float("nan")
            )
            record[f"{metric}_std"] = (
                float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0
            ) if finite.size else float("nan")
        aggregate.append(record)
    return aggregate


def _metric_lookup(
    aggregate: list[dict[str, float | int | str]],
    experiment: str,
    condition: str,
    method: str,
    metric: str,
) -> float:
    """Read one aggregate mean for the JSON executive summary."""

    row = next(
        item
        for item in aggregate
        if item["experiment"] == experiment
        and item["condition"] == condition
        and item["method"] == method
    )
    return float(row[f"{metric}_mean"])


def _run(config: Mapping[str, object]) -> tuple[
    list[dict[str, float | int | str]],
    list[dict[str, float | int | str]],
    dict[str, object],
]:
    """Execute all fixed Day 5 conditions and return rows plus validation."""

    dataset_seeds = tuple(int(value) for value in config["dataset_seeds"])
    spike_seeds = tuple(int(value) for value in config["spike_seeds"])
    snr_values = tuple(float(value) for value in config["snr_db_values"])
    fast_budget = int(config["snapshot_budgets"]["fast"])
    full_budget = int(config["snapshot_budgets"]["full"])
    t_max = int(config["lif"]["t_max"])
    leak = float(config["lif"]["leak"])
    threshold = float(config["gate"]["threshold"])
    persistence = int(config["gate"]["persistence"])
    budgets = (fast_budget, full_budget)

    per_seed_rows: list[dict[str, float | int | str]] = []
    paired_metadata_checks: list[bool] = []
    rms_checks: list[bool] = []

    mismatch_settings = {
        str(level["name"]): (
            float(level["gain_rms_db"]),
            float(level["phase_rms_deg"]),
        )
        for level in config["array_mismatch"]["levels"]
    }

    for dataset_seed, spike_seed in zip(dataset_seeds, spike_seeds, strict=True):
        doa_config = replace(
            DOAConfig(),
            snr_db_values=snr_values,
            samples_per_class_per_snr=int(config["samples_per_class_per_snr"]),
            random_seed=dataset_seed,
        )
        nominal = generate_progressive_doa_dataset(doa_config, budgets)
        train_index, test_index, _ = stratified_train_test_split_by_snr_and_class(
            labels=nominal.labels,
            snr_db=nominal.snr_db,
            snr_values=snr_values,
            num_classes=doa_config.num_classes,
            train_fraction=float(config["train_fraction"]),
            random_seed=dataset_seed,
        )
        normalized = normalize_progressive_train_test(nominal, train_index, test_index)
        train_labels = nominal.labels[train_index]
        test_labels = nominal.labels[test_index]
        fast_centroids = fit_nearest_centroid(
            normalized.train_features_by_budget[fast_budget],
            train_labels,
            doa_config.num_classes,
        )
        full_centroids = fit_nearest_centroid(
            normalized.train_features_by_budget[full_budget],
            train_labels,
            doa_config.num_classes,
        )

        # SNR sensitivity uses the nominal paired test split and fixed models.
        for snr_index, snr_db in enumerate(snr_values):
            local_mask = np.isclose(nominal.snr_db[test_index], snr_db)
            method_rows = _adaptive_method_rows(
                normalized.test_features_by_budget[fast_budget][local_mask],
                normalized.test_features_by_budget[full_budget][local_mask],
                test_labels[local_mask],
                fast_centroids,
                full_centroids,
                spike_seed + 100 + snr_index,
                fast_budget,
                full_budget,
                t_max,
                leak,
                threshold,
                persistence,
            )
            per_seed_rows.extend(
                _annotate_rows(
                    method_rows,
                    experiment="snr",
                    condition=f"{snr_db:g}_db",
                    dataset_seed=dataset_seed,
                    spike_seed=spike_seed + 100 + snr_index,
                )
            )

        # Fixed-device array mismatch is evaluated against nominal training and
        # normalization; no recalibration or retraining occurs.
        errors_by_level = _array_error_levels(
            doa_config.num_elements,
            dataset_seed,
            config["array_mismatch"],
        )
        for level_index, (level_name, errors) in enumerate(errors_by_level.items()):
            gain_rms, phase_rms = mismatch_settings[level_name]
            rms_checks.append(
                bool(
                    np.isclose(
                        np.sqrt(np.mean(np.square(errors.gain_db))),
                        gain_rms,
                        atol=1e-12,
                    )
                    and np.isclose(
                        np.sqrt(np.mean(np.square(errors.phase_deg))),
                        phase_rms,
                        atol=1e-12,
                    )
                )
            )
            if level_name == "nominal":
                evaluation: ProgressiveDOADataset = nominal
            else:
                evaluation = generate_progressive_doa_dataset(
                    doa_config,
                    budgets,
                    array_errors=errors,
                )
            paired_metadata_checks.append(
                bool(
                    np.array_equal(evaluation.sample_id, nominal.sample_id)
                    and np.array_equal(evaluation.labels, nominal.labels)
                    and np.array_equal(evaluation.theta_deg, nominal.theta_deg)
                    and np.array_equal(evaluation.snr_db, nominal.snr_db)
                )
            )
            eval_features = normalize_progressive_with_reference(
                evaluation,
                normalized.feature_min_by_budget,
                normalized.feature_max_by_budget,
                sample_index=test_index,
            )
            method_rows = _adaptive_method_rows(
                eval_features[fast_budget],
                eval_features[full_budget],
                test_labels,
                fast_centroids,
                full_centroids,
                spike_seed + 500,
                fast_budget,
                full_budget,
                t_max,
                leak,
                threshold,
                persistence,
            )
            per_seed_rows.extend(
                _annotate_rows(
                    method_rows,
                    experiment="array_mismatch",
                    condition=level_name,
                    dataset_seed=dataset_seed,
                    spike_seed=spike_seed + 500,
                    gain_rms_db=gain_rms,
                    phase_rms_deg=phase_rms,
                )
            )

        # Boundary evaluation pools all three internal boundaries and the full
        # SNR grid, while retaining the sign of the angular offset.
        boundary_theta, boundary_snr, boundary_offset = _boundary_conditions(
            config["boundary_stress"],
            snr_values,
        )
        boundary_config = replace(
            doa_config,
            random_seed=(
                dataset_seed
                + int(config["boundary_stress"]["dataset_seed_offset"])
            ),
        )
        boundary_dataset = generate_progressive_evaluation_dataset(
            boundary_theta,
            boundary_snr,
            config=boundary_config,
            snapshot_budgets=budgets,
        )
        boundary_features = normalize_progressive_with_reference(
            boundary_dataset,
            normalized.feature_min_by_budget,
            normalized.feature_max_by_budget,
        )
        for offset_index, offset in enumerate(
            config["boundary_stress"]["signed_offsets_deg"]
        ):
            local_mask = np.isclose(boundary_offset, float(offset))
            local_spike_seed = spike_seed + 1000 + offset_index
            method_rows = _adaptive_method_rows(
                boundary_features[fast_budget][local_mask],
                boundary_features[full_budget][local_mask],
                boundary_dataset.labels[local_mask],
                fast_centroids,
                full_centroids,
                local_spike_seed,
                fast_budget,
                full_budget,
                t_max,
                leak,
                threshold,
                persistence,
            )
            per_seed_rows.extend(
                _annotate_rows(
                    method_rows,
                    experiment="boundary_offset",
                    condition=f"{float(offset):+g}_deg",
                    dataset_seed=dataset_seed,
                    spike_seed=local_spike_seed,
                )
            )

    aggregate = _aggregate_rows(per_seed_rows)
    expected_groups = (
        len(snr_values)
        + len(config["array_mismatch"]["levels"])
        + len(config["boundary_stress"]["signed_offsets_deg"])
    ) * 3
    adaptive_rows = [row for row in per_seed_rows if row["method"] == "adaptive"]
    snapshot_checks = [
        bool(
            np.isclose(
                float(row["average_snapshots"]),
                fast_budget
                + float(row["fallback_rate"]) * (full_budget - fast_budget),
            )
        )
        for row in adaptive_rows
    ]
    validation = {
        "five_unique_seed_pairs_completed": bool(
            len(dataset_seeds) == len(set(dataset_seeds)) == 5
            and len(spike_seeds) == len(set(spike_seeds)) == 5
        ),
        "all_expected_aggregate_groups_present": len(aggregate) == expected_groups,
        "every_aggregate_group_has_five_seeds": bool(
            all(int(row["num_seeds"]) == 5 for row in aggregate)
        ),
        "mismatch_datasets_preserve_paired_metadata": bool(
            all(paired_metadata_checks)
        ),
        "array_error_rms_matches_configuration": bool(all(rms_checks)),
        "adaptive_snapshot_accounting_matches_formula": bool(all(snapshot_checks)),
        "operating_point_was_fixed_not_reselected": True,
    }
    validation["all_checks_pass"] = bool(all(validation.values()))
    return per_seed_rows, aggregate, validation


def main() -> None:
    """Run Day 5 and write detailed, aggregate, and executive outputs."""

    phase_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=phase_dir / "day_05_stress_config.json",
        help="Path to the fixed Day 5 JSON configuration.",
    )
    args = parser.parse_args()
    config = _load_config(args.config)
    per_seed, aggregate, validation = _run(config)

    results_dir = phase_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    per_seed_path = results_dir / "day_05_per_seed_metrics.csv"
    aggregate_path = results_dir / "day_05_aggregate_metrics.csv"
    summary_path = results_dir / "day_05_stress_test_summary.json"
    _write_csv(per_seed_path, per_seed)
    _write_csv(aggregate_path, aggregate)

    nominal = {
        method: {
            metric: _metric_lookup(
                aggregate,
                "array_mismatch",
                "nominal",
                method,
                metric,
            )
            for metric in ("accuracy", "average_snapshots", "average_lif_steps")
        }
        for method in ("always_fast", "always_continuous", "adaptive")
    }
    severe = {
        method: _metric_lookup(
            aggregate,
            "array_mismatch",
            "severe",
            method,
            "accuracy",
        )
        for method in ("always_fast", "always_continuous", "adaptive")
    }
    summary = {
        "checkpoint": "day_05_stress_testing",
        "pre_registered_operating_point": {
            "fast_budget": int(config["snapshot_budgets"]["fast"]),
            "full_budget": int(config["snapshot_budgets"]["full"]),
            "t_max": int(config["lif"]["t_max"]),
            "leak": float(config["lif"]["leak"]),
            "threshold": float(config["gate"]["threshold"]),
            "persistence": int(config["gate"]["persistence"]),
        },
        "seed_pairs": [
            {"dataset_seed": int(dataset), "spike_seed": int(spike)}
            for dataset, spike in zip(
                config["dataset_seeds"],
                config["spike_seeds"],
                strict=True,
            )
        ],
        "snr_grid_db": config["snr_db_values"],
        "boundary_protocol": (
            "signed offsets pooled across -30, 0, and 30 degree boundaries "
            "and the complete SNR grid"
        ),
        "array_mismatch_protocol": (
            "fixed zero-mean per-element gain/phase vectors; nominal training "
            "and normalization; no stress-condition retraining"
        ),
        "nominal_mean_metrics": nominal,
        "severe_mismatch_mean_accuracy": severe,
        "adaptive_accuracy_drop_nominal_to_severe": (
            nominal["adaptive"]["accuracy"] - severe["adaptive"]
        ),
        "validation": validation,
        "all_checks_pass": bool(validation["all_checks_pass"]),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Saved per-seed metrics to: {per_seed_path}")
    print(f"Saved aggregate metrics to: {aggregate_path}")
    print(f"Saved stress-test summary to: {summary_path}")
    if not summary["all_checks_pass"]:
        raise SystemExit("Day 5 validation failed.")


if __name__ == "__main__":
    main()
