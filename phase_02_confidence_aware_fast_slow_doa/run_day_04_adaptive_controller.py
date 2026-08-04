"""Run the mandatory adaptive fast-slow controller checkpoint.

Run from the repository root with:

    python -m phase_02_confidence_aware_fast_slow_doa.run_day_04_adaptive_controller
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
    generate_progressive_doa_dataset,
    normalize_progressive_train_test,
)


FAST_BUDGET = 32
FULL_BUDGET = 128
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
FINAL_ACCURACY_TOLERANCE = 0.01


def _write_rows(output_path: Path, rows: list[dict[str, float | int]]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Evaluate all gated operating points with the full-data fallback."""

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
    train_labels = progressive.labels[train_index]
    test_labels = progressive.labels[test_index]

    fast_centroids = fit_nearest_centroid(
        normalized.train_features_by_budget[FAST_BUDGET],
        train_labels,
        num_classes=config.num_classes,
    )
    fallback_centroids = fit_nearest_centroid(
        normalized.train_features_by_budget[FULL_BUDGET],
        train_labels,
        num_classes=config.num_classes,
    )
    fallback_predictions = predict_nearest_centroid(
        normalized.test_features_by_budget[FULL_BUDGET],
        fallback_centroids,
    )
    fallback_accuracy = accuracy_score(test_labels, fallback_predictions)

    weights, bias = fit_lif_prototype_weights(fast_centroids)
    spike_seed = config.random_seed + SPIKE_SEED_OFFSET
    shared_spikes = rate_encode_features(
        normalized.test_features_by_budget[FAST_BUDGET],
        num_time_steps=T_MAX,
        random_seed=spike_seed,
    )
    fast_lif = lif_classify(shared_spikes, weights, bias=bias, leak=LEAK)
    always_fast_accuracy = accuracy_score(test_labels, fast_lif.predicted_labels)

    operating_rows: list[dict[str, float | int]] = []
    for persistence in PERSISTENCE_VALUES:
        for threshold in THRESHOLDS:
            gate = causal_margin_persistence_gate(
                fast_lif.membrane_history,
                threshold=threshold,
                persistence=persistence,
            )
            decisions = compose_adaptive_decisions(
                gate,
                fallback_predictions,
                shared_spikes,
                initial_snapshot_budget=FAST_BUDGET,
                full_snapshot_budget=FULL_BUDGET,
            )
            row = {
                "threshold": float(threshold),
                "persistence": int(persistence),
                **adaptive_metrics(test_labels, gate, decisions),
            }
            operating_rows.append(row)

    target_accuracy = fallback_accuracy - FINAL_ACCURACY_TOLERANCE
    eligible_rows = [
        row
        for row in operating_rows
        if float(row["final_accuracy"]) >= target_accuracy
    ]
    if not eligible_rows:
        raise SystemExit("No operating point met the stated final-accuracy tolerance.")
    selected = min(
        eligible_rows,
        key=lambda row: (
            float(row["average_snapshots"]),
            -float(row["final_accuracy"]),
            -float(row["selective_accuracy"]),
        ),
    )

    selected_gate = causal_margin_persistence_gate(
        fast_lif.membrane_history,
        threshold=float(selected["threshold"]),
        persistence=int(selected["persistence"]),
    )
    selected_decisions = compose_adaptive_decisions(
        selected_gate,
        fallback_predictions,
        shared_spikes,
        initial_snapshot_budget=FAST_BUDGET,
        full_snapshot_budget=FULL_BUDGET,
    )

    phase_dir = Path(__file__).resolve().parent
    results_dir = phase_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    sweep_path = results_dir / "day_04_adaptive_operating_points.csv"
    summary_path = results_dir / "day_04_adaptive_controller_summary.json"
    decisions_path = results_dir / "day_04_selected_operating_point_decisions.csv"
    _write_rows(sweep_path, operating_rows)

    expected_average_snapshots = (
        FAST_BUDGET
        + float(selected["fallback_rate"]) * (FULL_BUDGET - FAST_BUDGET)
    )
    validation = {
        "average_snapshot_formula_matches": bool(
            np.isclose(
                float(selected["average_snapshots"]),
                expected_average_snapshots,
            )
        ),
        "fallback_baseline_reproduced": bool(
            np.isclose(fallback_accuracy, 0.8690476190476191)
        ),
        "selected_point_meets_accuracy_tolerance": bool(
            float(selected["final_accuracy"]) >= target_accuracy
        ),
    }
    summary = {
        "checkpoint": "day_04_adaptive_controller",
        "fast_budget": FAST_BUDGET,
        "full_budget": FULL_BUDGET,
        "t_max": T_MAX,
        "leak": LEAK,
        "spike_seed": spike_seed,
        "always_fast_accuracy": float(always_fast_accuracy),
        "always_continuous_accuracy": float(fallback_accuracy),
        "selection_rule": (
            "minimum average snapshots among operating points with final "
            "accuracy no more than 0.01 below always-continuous"
        ),
        "selected_operating_point": selected,
        "validation": validation,
        "all_checks_pass": bool(all(validation.values())),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    with decisions_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "sample_id",
            "true_sector",
            "theta_deg",
            "snr_db",
            "fast_t40_prediction",
            "accepted_fast_prediction",
            "confidence_at_decision",
            "final_t40_margin",
            "accepted",
            "fallback_prediction",
            "final_prediction",
            "snapshots_used",
            "lif_steps_used",
            "spike_count_used",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for local_index, dataset_index in enumerate(test_index):
            writer.writerow(
                {
                    "sample_id": int(progressive.sample_id[dataset_index]),
                    "true_sector": int(test_labels[local_index]),
                    "theta_deg": float(progressive.theta_deg[dataset_index]),
                    "snr_db": float(progressive.snr_db[dataset_index]),
                    "fast_t40_prediction": int(fast_lif.predicted_labels[local_index]),
                    "accepted_fast_prediction": int(
                        selected_gate.predicted_labels[local_index]
                    ),
                    "confidence_at_decision": float(
                        selected_gate.confidence_at_decision[local_index]
                    ),
                    "final_t40_margin": float(
                        selected_gate.normalized_margin_history[local_index, -1]
                    ),
                    "accepted": bool(selected_gate.accepted[local_index]),
                    "fallback_prediction": int(fallback_predictions[local_index]),
                    "final_prediction": int(
                        selected_decisions.final_predictions[local_index]
                    ),
                    "snapshots_used": int(
                        selected_decisions.snapshots_used[local_index]
                    ),
                    "lif_steps_used": int(
                        selected_decisions.lif_steps_used[local_index]
                    ),
                    "spike_count_used": int(
                        selected_decisions.spike_counts_used[local_index]
                    ),
                }
            )

    print(json.dumps(summary, indent=2))
    print(f"Saved adaptive operating points to: {sweep_path}")
    print(f"Saved selected per-sample decisions to: {decisions_path}")
    print(f"Saved validation record to: {summary_path}")
    if not summary["all_checks_pass"]:
        raise SystemExit("Adaptive-controller validation failed.")


if __name__ == "__main__":
    main()
