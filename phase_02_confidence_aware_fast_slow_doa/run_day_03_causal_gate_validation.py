"""Validate shared spike prefixes and the causal confidence gate.

Run from the repository root with:

    python -m phase_02_confidence_aware_fast_slow_doa.run_day_03_causal_gate_validation
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from phase_01_python_prototype.src.dataset import (
    DOAConfig,
    stratified_train_test_split_by_snr_and_class,
)
from phase_01_python_prototype.src.lif import fit_lif_prototype_weights, lif_classify
from phase_01_python_prototype.src.metrics import accuracy_score, fit_nearest_centroid
from phase_01_python_prototype.src.spike_encoding import rate_encode_features
from phase_02_confidence_aware_fast_slow_doa.src.confidence_gate import (
    causal_margin_persistence_gate,
)
from phase_02_confidence_aware_fast_slow_doa.src.progressive_dataset import (
    generate_progressive_doa_dataset,
    normalize_progressive_train_test,
)


T_MAX = 40
LEAK = 0.99
SPIKE_SEED_OFFSET = 700
THRESHOLDS: tuple[float, ...] = (
    0.00,
    0.02,
    0.05,
    0.10,
    0.15,
    0.20,
    0.30,
    0.40,
    0.50,
    0.60,
    0.70,
    0.80,
    0.90,
    0.95,
)
PERSISTENCE_VALUES: tuple[int, ...] = (1, 2, 3, 4, 5)


def _sweep_rows(
    membrane_history: np.ndarray,
    true_labels: np.ndarray,
) -> list[dict[str, float | int]]:
    """Evaluate the selective-decision trade-off grid."""

    rows: list[dict[str, float | int]] = []
    num_samples = int(true_labels.size)

    for persistence in PERSISTENCE_VALUES:
        for threshold in THRESHOLDS:
            gate = causal_margin_persistence_gate(
                membrane_history,
                threshold=threshold,
                persistence=persistence,
            )
            accepted_count = int(np.sum(gate.accepted))
            correct_accepted = int(
                np.sum(gate.accepted & (gate.predicted_labels == true_labels))
            )
            incorrect_accepted = accepted_count - correct_accepted
            coverage = accepted_count / num_samples
            selective_accuracy = (
                correct_accepted / accepted_count if accepted_count else float("nan")
            )
            false_confidence_rate = (
                incorrect_accepted / accepted_count if accepted_count else float("nan")
            )
            mean_decision_steps = (
                float(np.mean(gate.decision_steps[gate.accepted]))
                if accepted_count
                else float("nan")
            )

            rows.append(
                {
                    "threshold": float(threshold),
                    "persistence": int(persistence),
                    "accepted_count": accepted_count,
                    "coverage": float(coverage),
                    "selective_accuracy": float(selective_accuracy),
                    "false_confidence_rate": float(false_confidence_rate),
                    "false_acceptance_probability": float(
                        incorrect_accepted / num_samples
                    ),
                    "mean_decision_steps": mean_decision_steps,
                }
            )

    return rows


def _write_csv(output_path: Path, rows: list[dict[str, float | int]]) -> None:
    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Run the Day 3 causal-gate checkpoint."""

    config = DOAConfig()
    progressive = generate_progressive_doa_dataset(config, (32, 64, 128))
    train_index, test_index, _ = stratified_train_test_split_by_snr_and_class(
        labels=progressive.labels,
        snr_db=progressive.snr_db,
        snr_values=config.snr_db_values,
        num_classes=config.num_classes,
        train_fraction=0.70,
        random_seed=config.random_seed,
    )
    normalized = normalize_progressive_train_test(progressive, train_index, test_index)

    fast_budget = 32
    train_features = normalized.train_features_by_budget[fast_budget]
    test_features = normalized.test_features_by_budget[fast_budget]
    train_labels = progressive.labels[train_index]
    test_labels = progressive.labels[test_index]

    centroids = fit_nearest_centroid(
        train_features,
        train_labels,
        num_classes=config.num_classes,
    )
    weights, bias = fit_lif_prototype_weights(centroids)
    spike_seed = config.random_seed + SPIKE_SEED_OFFSET
    shared_spikes = rate_encode_features(
        test_features,
        num_time_steps=T_MAX,
        random_seed=spike_seed,
    )
    full_lif = lif_classify(shared_spikes, weights, bias=bias, leak=LEAK)

    prefix_exact_match: dict[str, bool] = {}
    for prefix_length in (10, 20, 40):
        prefix_lif = lif_classify(
            shared_spikes[:, :prefix_length, :],
            weights,
            bias=bias,
            leak=LEAK,
        )
        prefix_exact_match[str(prefix_length)] = bool(
            np.array_equal(
                prefix_lif.membrane_history,
                full_lif.membrane_history[:, :prefix_length, :],
            )
        )

    rows = _sweep_rows(full_lif.membrane_history, test_labels)
    monotonic_coverage_by_persistence: dict[str, bool] = {}
    for persistence in PERSISTENCE_VALUES:
        coverage = [
            float(row["coverage"])
            for row in rows
            if int(row["persistence"]) == persistence
        ]
        monotonic_coverage_by_persistence[str(persistence)] = bool(
            all(
                coverage[index + 1] <= coverage[index] + 1e-15
                for index in range(len(coverage) - 1)
            )
        )

    zero_threshold_k1 = next(
        row
        for row in rows
        if float(row["threshold"]) == 0.0 and int(row["persistence"]) == 1
    )
    all_checks_pass = (
        all(prefix_exact_match.values())
        and all(monotonic_coverage_by_persistence.values())
        and np.isclose(float(zero_threshold_k1["coverage"]), 1.0)
    )

    summary = {
        "checkpoint": "day_03_causal_gate_validation",
        "fast_snapshot_budget": fast_budget,
        "t_max": T_MAX,
        "leak": LEAK,
        "spike_seed": spike_seed,
        "test_samples": int(test_labels.size),
        "always_fast_m32_t40_accuracy": float(
            accuracy_score(test_labels, full_lif.predicted_labels)
        ),
        "shared_prefix_exact_match": prefix_exact_match,
        "coverage_monotonic_with_threshold": monotonic_coverage_by_persistence,
        "thresholds": list(THRESHOLDS),
        "persistence_values": list(PERSISTENCE_VALUES),
        "all_checks_pass": bool(all_checks_pass),
    }

    phase_dir = Path(__file__).resolve().parent
    results_dir = phase_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "day_03_causal_gate_sweep.csv"
    json_path = results_dir / "day_03_causal_gate_validation.json"
    _write_csv(csv_path, rows)
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"Saved confidence sweep to: {csv_path}")
    print(f"Saved validation record to: {json_path}")
    if not all_checks_pass:
        raise SystemExit("Causal-gate validation failed.")


if __name__ == "__main__":
    main()
