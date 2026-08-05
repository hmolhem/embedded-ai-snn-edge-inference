"""Run the Day 7 confidence-calibration analysis protocol.

Run from the repository root with:

    python -m phase_02_confidence_aware_fast_slow_doa.run_day_07_confidence_calibration

Day 7 uses only the registered calibration seeds. It exports descriptive
confidence diagnostics and the complete causal-gate grid but deliberately does
not select an operating point and does not evaluate the sealed holdout seeds.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
from phase_02_confidence_aware_fast_slow_doa.src.confidence_calibration import (
    binary_auroc,
    evaluate_causal_operating_point,
    expected_calibration_error,
    reliability_rows,
    risk_coverage_rows,
    sample_confidence_diagnostics,
    validate_seed_protocol,
)
from phase_02_confidence_aware_fast_slow_doa.src.progressive_dataset import (
    generate_progressive_doa_dataset,
    normalize_progressive_train_test,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "day_07_confidence_calibration_config.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _load_config(path: Path) -> tuple[dict[str, object], dict[str, bool]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if int(config["schema_version"]) != 1:
        raise ValueError("Unsupported Day 7 configuration schema.")
    seed_checks = validate_seed_protocol(config)
    if not 0.0 < float(config["train_fraction"]) < 1.0:
        raise ValueError("train_fraction must lie in (0, 1).")
    fast_budget = int(config["snapshot_budgets"]["fast"])
    full_budget = int(config["snapshot_budgets"]["full"])
    if fast_budget <= 0 or full_budget <= fast_budget:
        raise ValueError("snapshot_budgets must define 0 < fast < full.")
    if int(config["lif"]["t_max"]) <= 0:
        raise ValueError("lif.t_max must be positive.")
    if not 0.0 < float(config["lif"]["leak"]) <= 1.0:
        raise ValueError("lif.leak must lie in (0, 1].")

    thresholds = tuple(float(value) for value in config["analysis"]["thresholds"])
    persistence_values = tuple(
        int(value) for value in config["analysis"]["persistence_values"]
    )
    if not thresholds or any(value < 0.0 or value > 1.0 for value in thresholds):
        raise ValueError("analysis.thresholds must lie in [0, 1].")
    if any(thresholds[index + 1] <= thresholds[index] for index in range(len(thresholds) - 1)):
        raise ValueError("analysis.thresholds must be strictly increasing.")
    if not persistence_values or any(value <= 0 for value in persistence_values):
        raise ValueError("analysis.persistence_values must be positive.")
    return config, seed_checks


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError("Cannot write an empty table.")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _seed_pair(item: Mapping[str, object]) -> tuple[int, int]:
    return int(item["dataset_seed"]), int(item["spike_seed"])


def _run_calibration_pair(
    config: Mapping[str, object],
    dataset_seed: int,
    spike_seed: int,
) -> dict[str, object]:
    snr_values = tuple(float(value) for value in config["snr_db_values"])
    fast_budget = int(config["snapshot_budgets"]["fast"])
    full_budget = int(config["snapshot_budgets"]["full"])
    doa_config = replace(
        DOAConfig(),
        snr_db_values=snr_values,
        samples_per_class_per_snr=int(config["samples_per_class_per_snr"]),
        random_seed=dataset_seed,
    )
    progressive = generate_progressive_doa_dataset(
        doa_config,
        (fast_budget, full_budget),
    )
    train_index, calibration_index, _ = stratified_train_test_split_by_snr_and_class(
        labels=progressive.labels,
        snr_db=progressive.snr_db,
        snr_values=snr_values,
        num_classes=doa_config.num_classes,
        train_fraction=float(config["train_fraction"]),
        random_seed=dataset_seed,
    )
    normalized = normalize_progressive_train_test(
        progressive,
        train_index,
        calibration_index,
    )
    train_labels = progressive.labels[train_index]
    labels = progressive.labels[calibration_index]
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
    fallback_predictions = predict_nearest_centroid(
        normalized.test_features_by_budget[full_budget],
        full_centroids,
    )
    shared_spikes = rate_encode_features(
        normalized.test_features_by_budget[fast_budget],
        num_time_steps=int(config["lif"]["t_max"]),
        random_seed=spike_seed,
    )
    weights, bias = fit_lif_prototype_weights(fast_centroids)
    lif_result = lif_classify(
        shared_spikes,
        weights,
        bias=bias,
        leak=float(config["lif"]["leak"]),
    )
    diagnostics = sample_confidence_diagnostics(
        lif_result.membrane_history,
        shared_spikes,
        labels,
    )
    boundaries = np.asarray(doa_config.sector_edges_deg[1:-1], dtype=float)
    theta = progressive.theta_deg[calibration_index]
    distance_to_boundary = np.min(
        np.abs(theta[:, np.newaxis] - boundaries[np.newaxis, :]),
        axis=1,
    )

    sample_rows: list[dict[str, object]] = []
    for local_index, dataset_index in enumerate(calibration_index):
        sample_rows.append(
            {
                "dataset_seed": dataset_seed,
                "spike_seed": spike_seed,
                "sample_id": int(progressive.sample_id[dataset_index]),
                "true_sector": int(labels[local_index]),
                "theta_deg": float(theta[local_index]),
                "snr_db": float(progressive.snr_db[dataset_index]),
                "distance_to_nearest_boundary_deg": float(
                    distance_to_boundary[local_index]
                ),
                "fast_prediction": int(diagnostics["final_prediction"][local_index]),
                "fast_correct": bool(diagnostics["fast_correct"][local_index]),
                "fallback_prediction": int(fallback_predictions[local_index]),
                "fallback_correct": bool(fallback_predictions[local_index] == labels[local_index]),
                "final_margin": float(diagnostics["final_margin"][local_index]),
                "maximum_margin": float(diagnostics["maximum_margin"][local_index]),
                "final_winner_persistence": int(
                    diagnostics["final_winner_persistence"][local_index]
                ),
                "maximum_winner_persistence": int(
                    diagnostics["maximum_winner_persistence"][local_index]
                ),
                "stable_winner_step": int(
                    diagnostics["stable_winner_step"][local_index]
                ),
                "final_spike_count": int(
                    diagnostics["final_spike_count"][local_index]
                ),
                "mean_firing_rate": float(
                    diagnostics["mean_firing_rate"][local_index]
                ),
            }
        )
    return {
        "dataset_seed": dataset_seed,
        "spike_seed": spike_seed,
        "labels": labels,
        "fallback_predictions": fallback_predictions,
        "score_history": lif_result.membrane_history,
        "shared_spikes": shared_spikes,
        "diagnostics": diagnostics,
        "sample_rows": sample_rows,
    }


def _mean_std(values: Iterable[float]) -> tuple[float, float]:
    array = np.asarray(tuple(values), dtype=float)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return float("nan"), float("nan")
    return float(np.mean(finite)), float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0


def _operating_point_rows(
    config: Mapping[str, object],
    seed_outputs: list[dict[str, object]],
) -> list[dict[str, object]]:
    thresholds = tuple(float(value) for value in config["analysis"]["thresholds"])
    persistence_values = tuple(
        int(value) for value in config["analysis"]["persistence_values"]
    )
    fast_budget = int(config["snapshot_budgets"]["fast"])
    full_budget = int(config["snapshot_budgets"]["full"])
    labels = np.concatenate([item["labels"] for item in seed_outputs])
    fallback = np.concatenate(
        [item["fallback_predictions"] for item in seed_outputs]
    )
    scores = np.concatenate([item["score_history"] for item in seed_outputs])
    spikes = np.concatenate([item["shared_spikes"] for item in seed_outputs])
    continuous_accuracy = accuracy_score(labels, fallback)
    fast_predictions = np.argmax(scores[:, -1, :], axis=1)
    fast_accuracy = accuracy_score(labels, fast_predictions)
    tolerance = float(config["analysis"]["final_accuracy_tolerance"])

    rows: list[dict[str, object]] = []
    for persistence in persistence_values:
        for threshold in thresholds:
            pooled = evaluate_causal_operating_point(
                scores,
                spikes,
                labels,
                fallback,
                threshold,
                persistence,
                fast_budget,
                full_budget,
            )
            per_seed = [
                evaluate_causal_operating_point(
                    item["score_history"],
                    item["shared_spikes"],
                    item["labels"],
                    item["fallback_predictions"],
                    threshold,
                    persistence,
                    fast_budget,
                    full_budget,
                )
                for item in seed_outputs
            ]
            accuracy_mean, accuracy_std = _mean_std(
                float(item["final_accuracy"]) for item in per_seed
            )
            coverage_mean, coverage_std = _mean_std(
                float(item["coverage"]) for item in per_seed
            )
            snapshots_mean, snapshots_std = _mean_std(
                float(item["average_snapshots"]) for item in per_seed
            )
            rows.append(
                {
                    **pooled,
                    "always_fast_accuracy": fast_accuracy,
                    "always_continuous_accuracy": continuous_accuracy,
                    "accuracy_gap_vs_continuous": (
                        float(pooled["final_accuracy"]) - continuous_accuracy
                    ),
                    "snapshot_reduction_fraction": (
                        1.0 - float(pooled["average_snapshots"]) / full_budget
                    ),
                    "eligible_within_accuracy_tolerance": bool(
                        float(pooled["final_accuracy"])
                        >= continuous_accuracy - tolerance
                    ),
                    "final_accuracy_seed_mean": accuracy_mean,
                    "final_accuracy_seed_std": accuracy_std,
                    "coverage_seed_mean": coverage_mean,
                    "coverage_seed_std": coverage_std,
                    "average_snapshots_seed_mean": snapshots_mean,
                    "average_snapshots_seed_std": snapshots_std,
                }
            )
    return rows


def _save_figure(fig: plt.Figure, stem: Path) -> None:
    fig.savefig(stem.with_suffix(".png"), dpi=180, bbox_inches="tight")
    fig.savefig(
        stem.with_suffix(".pdf"),
        bbox_inches="tight",
        metadata={"CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def _plot_reliability(rows: list[dict[str, object]], figures_dir: Path) -> None:
    populated = [row for row in rows if int(row["count"]) > 0]
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.plot([0.0, 1.0], [0.0, 1.0], "--", color="0.5", label="Ideal")
    ax.plot(
        [float(row["mean_confidence"]) for row in populated],
        [float(row["observed_accuracy"]) for row in populated],
        marker="o",
        linewidth=2,
        label="Final normalized margin",
    )
    ax.set(xlabel="Mean confidence", ylabel="Observed fast accuracy", xlim=(0, 1), ylim=(0, 1))
    ax.grid(alpha=0.25)
    ax.legend()
    _save_figure(fig, figures_dir / "day_07_confidence_reliability")


def _plot_risk_coverage(rows: list[dict[str, object]], figures_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.plot(
        [float(row["realized_coverage"]) for row in rows],
        [float(row["selective_risk"]) for row in rows],
        marker="o",
        linewidth=2,
    )
    ax.set(xlabel="Coverage", ylabel="Selective risk (1 - accuracy)", xlim=(0, 1))
    ax.grid(alpha=0.25)
    _save_figure(fig, figures_dir / "day_07_risk_coverage")


def _plot_operating_points(
    rows: list[dict[str, object]],
    figures_dir: Path,
) -> None:
    persistence_values = sorted({int(row["persistence"]) for row in rows})
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    for persistence in persistence_values:
        selected = [row for row in rows if int(row["persistence"]) == persistence]
        ax.plot(
            [float(row["coverage"]) for row in selected],
            [100.0 * float(row["snapshot_reduction_fraction"]) for row in selected],
            marker="o",
            label=f"K={persistence}",
        )
    ax.set(xlabel="Causal gate coverage", ylabel="Snapshot reduction (%)", xlim=(0, 1))
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    _save_figure(fig, figures_dir / "day_07_coverage_snapshot_reduction")

    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    tolerance = -0.01
    ax.axhline(0.0, linestyle="--", color="0.4", linewidth=1.2, label="Continuous baseline")
    ax.axhline(tolerance, linestyle=":", color="tab:red", linewidth=1.5, label="-1 percentage point")
    for persistence in persistence_values:
        selected = [row for row in rows if int(row["persistence"]) == persistence]
        ax.plot(
            [float(row["coverage"]) for row in selected],
            [100.0 * float(row["accuracy_gap_vs_continuous"]) for row in selected],
            marker="o",
            label=f"K={persistence}",
        )
    ax.set(xlabel="Causal gate coverage", ylabel="Accuracy gap vs continuous (percentage points)", xlim=(0, 1))
    ax.grid(alpha=0.25)
    ax.legend(ncol=2)
    _save_figure(fig, figures_dir / "day_07_accuracy_gap")


def _coverage_is_monotonic(rows: list[dict[str, object]]) -> bool:
    for persistence in sorted({int(row["persistence"]) for row in rows}):
        selected = [row for row in rows if int(row["persistence"]) == persistence]
        selected.sort(key=lambda row: float(row["threshold"]))
        coverage = [float(row["coverage"]) for row in selected]
        if any(coverage[index + 1] > coverage[index] + 1e-15 for index in range(len(coverage) - 1)):
            return False
    return True


def _run(config: Mapping[str, object]) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    dict[str, object],
]:
    calibration_pairs = [
        _seed_pair(item) for item in config["calibration_seed_pairs"]
    ]
    seed_outputs = [
        _run_calibration_pair(config, dataset_seed, spike_seed)
        for dataset_seed, spike_seed in calibration_pairs
    ]
    sample_rows = [
        row for item in seed_outputs for row in item["sample_rows"]
    ]
    confidence = np.asarray([float(row["final_margin"]) for row in sample_rows])
    correct = np.asarray([bool(row["fast_correct"]) for row in sample_rows])
    reliability = reliability_rows(
        confidence,
        correct,
        config["analysis"]["reliability_bin_edges"],
    )
    risk_coverage = risk_coverage_rows(
        confidence,
        correct,
        config["analysis"]["risk_coverage_grid"],
    )
    operating_points = _operating_point_rows(config, seed_outputs)
    continuous_accuracy = float(operating_points[0]["always_continuous_accuracy"])
    fast_accuracy = float(operating_points[0]["always_fast_accuracy"])
    reference = next(
        row
        for row in operating_points
        if np.isclose(float(row["threshold"]), 0.8)
        and int(row["persistence"]) == 5
    )
    correct_margin = confidence[correct]
    incorrect_margin = confidence[~correct]
    analysis = {
        "num_calibration_samples": len(sample_rows),
        "always_fast_accuracy": fast_accuracy,
        "always_continuous_accuracy": continuous_accuracy,
        "final_margin_auroc_for_fast_correctness": binary_auroc(confidence, correct),
        "final_margin_expected_calibration_error": expected_calibration_error(reliability),
        "mean_margin_correct_fast_decisions": float(np.mean(correct_margin)),
        "mean_margin_incorrect_fast_decisions": float(np.mean(incorrect_margin)),
        "mean_margin_separation": float(np.mean(correct_margin) - np.mean(incorrect_margin)),
        "reference_gate_tau_0_8_k_5": {
            key: reference[key]
            for key in (
                "final_accuracy",
                "coverage",
                "selective_accuracy",
                "false_confidence_rate",
                "fallback_rate",
                "average_snapshots",
                "average_lif_steps",
                "snapshot_reduction_fraction",
                "accuracy_gap_vs_continuous",
            )
        },
        "eligible_operating_point_count_without_selection": int(
            sum(bool(row["eligible_within_accuracy_tolerance"]) for row in operating_points)
        ),
    }
    return sample_rows, operating_points, reliability, risk_coverage, analysis


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()
    config, seed_checks = _load_config(args.config)
    sample_rows, operating_points, reliability, risk_coverage, analysis = _run(config)

    results_dir = PACKAGE_ROOT / "results"
    figures_dir = PACKAGE_ROOT / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    samples_path = results_dir / "day_07_calibration_samples.csv"
    operating_path = results_dir / "day_07_operating_points.csv"
    reliability_path = results_dir / "day_07_confidence_reliability.csv"
    risk_path = results_dir / "day_07_risk_coverage.csv"
    summary_path = results_dir / "day_07_confidence_calibration_summary.json"
    _write_csv(samples_path, sample_rows)
    _write_csv(operating_path, operating_points)
    _write_csv(reliability_path, reliability)
    _write_csv(risk_path, risk_coverage)
    _plot_reliability(reliability, figures_dir)
    _plot_risk_coverage(risk_coverage, figures_dir)
    _plot_operating_points(operating_points, figures_dir)

    fast_budget = int(config["snapshot_budgets"]["fast"])
    full_budget = int(config["snapshot_budgets"]["full"])
    snapshot_formula_ok = all(
        np.isclose(
            float(row["average_snapshots"]),
            fast_budget + float(row["fallback_rate"]) * (full_budget - fast_budget),
        )
        for row in operating_points
    )
    calibration_dataset_seeds = {
        int(item["dataset_seed"]) for item in config["calibration_seed_pairs"]
    }
    observed_dataset_seeds = {int(row["dataset_seed"]) for row in sample_rows}
    expected_ops = len(config["analysis"]["thresholds"]) * len(
        config["analysis"]["persistence_values"]
    )
    validation = {
        **seed_checks,
        "only_registered_calibration_seeds_evaluated": (
            observed_dataset_seeds == calibration_dataset_seeds
        ),
        "holdout_not_evaluated": True,
        "all_calibration_pairs_completed": (
            len({(int(row["dataset_seed"]), int(row["spike_seed"])) for row in sample_rows}) == 5
        ),
        "complete_operating_point_grid": len(operating_points) == expected_ops,
        "coverage_monotonic_with_threshold": _coverage_is_monotonic(operating_points),
        "snapshot_accounting_matches_formula": snapshot_formula_ok,
        "reliability_bins_account_for_all_samples": (
            sum(int(row["count"]) for row in reliability) == len(sample_rows)
        ),
        "risk_coverage_grid_complete": (
            len(risk_coverage) == len(config["analysis"]["risk_coverage_grid"])
        ),
        "no_operating_point_selected_on_day_07": True,
        "selection_reserved_for_day_08": (
            str(config["analysis"]["selection_policy"])
            == "reserved_for_day_08_after_review_of_day_07_outputs"
        ),
    }
    validation["all_checks_pass"] = bool(all(validation.values()))
    holdout_manifest = config["holdout_seed_pairs"]
    summary = {
        "checkpoint": "day_07_confidence_calibration_protocol",
        "config_sha256": _sha256(args.config),
        "calibration_seed_pairs": config["calibration_seed_pairs"],
        "holdout_seed_manifest_sha256": _canonical_sha256(holdout_manifest),
        "holdout_policy": config["holdout_policy"],
        "holdout_evaluated": False,
        "selection_performed": False,
        "analysis": analysis,
        "validation": validation,
        "all_checks_pass": bool(validation["all_checks_pass"]),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Saved calibration samples to: {samples_path}")
    print(f"Saved operating points to: {operating_path}")
    print(f"Saved reliability table to: {reliability_path}")
    print(f"Saved risk-coverage table to: {risk_path}")
    print(f"Saved summary to: {summary_path}")
    if not summary["all_checks_pass"]:
        raise SystemExit("Day 7 confidence-calibration validation failed.")


if __name__ == "__main__":
    main()
