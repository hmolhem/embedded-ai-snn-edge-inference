"""Run 005 LIF parameter sweep for Phase 1 DOA experiments."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .dataset import (
    DOAConfig,
    generate_doa_dataset,
    minmax_normalize_train_test,
    stratified_train_test_split_by_snr_and_class,
)
from .lif import fit_lif_prototype_weights, lif_classify
from .metrics import accuracy_score, fit_nearest_centroid, predict_nearest_centroid
from .plots import plot_lif_parameter_sweep_tradeoff
from .spike_encoding import rate_encode_features, spike_count_per_sample


SWEEP_TIME_STEPS: tuple[int, ...] = (10, 20, 30, 40)
SWEEP_LEAK_VALUES: tuple[float, ...] = (0.90, 0.95, 0.97, 0.99)


def _write_sweep_csv(output_path: Path, rows: list[dict[str, float]]) -> None:
    """Write Run 005 LIF parameter-sweep rows to CSV."""

    fieldnames = [
        "num_time_steps",
        "leak",
        "overall_accuracy",
        "mean_latency_steps",
        "std_latency_steps",
        "min_latency_steps",
        "max_latency_steps",
        "mean_spike_count_per_sample",
        "max_possible_spikes_per_sample",
        "test_samples",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "num_time_steps": int(row["num_time_steps"]),
                    "leak": f"{float(row['leak']):.2f}",
                    "overall_accuracy": f"{float(row['overall_accuracy']):.6f}",
                    "mean_latency_steps": f"{float(row['mean_latency_steps']):.6f}",
                    "std_latency_steps": f"{float(row['std_latency_steps']):.6f}",
                    "min_latency_steps": int(row["min_latency_steps"]),
                    "max_latency_steps": int(row["max_latency_steps"]),
                    "mean_spike_count_per_sample": f"{float(row['mean_spike_count_per_sample']):.6f}",
                    "max_possible_spikes_per_sample": int(row["max_possible_spikes_per_sample"]),
                    "test_samples": int(row["test_samples"]),
                }
            )


def _format_sweep_summary(
    rows: list[dict[str, float]],
    baseline_accuracy: float,
) -> str:
    """Return a compact text summary for Run 005."""

    best_accuracy_row = max(rows, key=lambda row: float(row["overall_accuracy"]))
    lowest_latency_row = min(rows, key=lambda row: float(row["mean_latency_steps"]))

    lines = [
        "Run 005 LIF parameter sweep",
        "===========================",
        f"baseline_nearest_centroid_accuracy: {baseline_accuracy:.6f}",
        "",
        "sweep_grid:",
        f"  num_time_steps: {list(SWEEP_TIME_STEPS)}",
        f"  leak_values: {[round(value, 2) for value in SWEEP_LEAK_VALUES]}",
        f"  total_configurations: {len(rows)}",
        "",
        "best_accuracy_configuration:",
        f"  num_time_steps: {int(best_accuracy_row['num_time_steps'])}",
        f"  leak: {float(best_accuracy_row['leak']):.2f}",
        f"  overall_accuracy: {float(best_accuracy_row['overall_accuracy']):.6f}",
        f"  mean_latency_steps: {float(best_accuracy_row['mean_latency_steps']):.6f}",
        "",
        "lowest_latency_configuration:",
        f"  num_time_steps: {int(lowest_latency_row['num_time_steps'])}",
        f"  leak: {float(lowest_latency_row['leak']):.2f}",
        f"  overall_accuracy: {float(lowest_latency_row['overall_accuracy']):.6f}",
        f"  mean_latency_steps: {float(lowest_latency_row['mean_latency_steps']):.6f}",
        "",
        "all_configurations:",
    ]

    for row in sorted(rows, key=lambda item: (int(item["num_time_steps"]), float(item["leak"]))):
        lines.append(
            "  "
            f"T={int(row['num_time_steps']):>2d}, "
            f"leak={float(row['leak']):.2f}, "
            f"accuracy={float(row['overall_accuracy']):.6f}, "
            f"mean_latency={float(row['mean_latency_steps']):.6f}"
        )

    return "\n".join(lines)


def run_lif_parameter_sweep() -> tuple[list[dict[str, float]], float]:
    """Run the Run 005 LIF time-step/leak sweep and return result rows."""

    config = DOAConfig()
    dataset = generate_doa_dataset(config)

    features = np.asarray(dataset["features"], dtype=float)
    labels = np.asarray(dataset["labels"], dtype=int)
    snr_db = np.asarray(dataset["snr_db"], dtype=float)

    train_index, test_index, _ = stratified_train_test_split_by_snr_and_class(
        labels=labels,
        snr_db=snr_db,
        snr_values=config.snr_db_values,
        num_classes=config.num_classes,
        train_fraction=0.70,
        random_seed=config.random_seed,
    )

    train_features_raw = features[train_index]
    test_features_raw = features[test_index]
    train_labels = labels[train_index]
    test_labels = labels[test_index]

    train_features, test_features, _, _ = minmax_normalize_train_test(
        train_features_raw,
        test_features_raw,
    )

    centroids = fit_nearest_centroid(
        train_features,
        train_labels,
        num_classes=config.num_classes,
    )
    baseline_predictions = predict_nearest_centroid(test_features, centroids)
    baseline_accuracy = accuracy_score(test_labels, baseline_predictions)

    lif_weights, lif_bias = fit_lif_prototype_weights(centroids)

    sweep_rows: list[dict[str, float]] = []
    for num_time_steps in SWEEP_TIME_STEPS:
        test_spikes = rate_encode_features(
            test_features,
            num_time_steps=num_time_steps,
            random_seed=config.random_seed + 500 + num_time_steps,
        )
        spike_counts = spike_count_per_sample(test_spikes)

        for leak in SWEEP_LEAK_VALUES:
            lif_result = lif_classify(
                test_spikes,
                weights=lif_weights,
                bias=lif_bias,
                leak=leak,
            )
            accuracy = accuracy_score(test_labels, lif_result.predicted_labels)
            latency_steps = np.asarray(lif_result.latency_steps, dtype=float)

            sweep_rows.append(
                {
                    "num_time_steps": float(num_time_steps),
                    "leak": float(leak),
                    "overall_accuracy": float(accuracy),
                    "mean_latency_steps": float(np.mean(latency_steps)),
                    "std_latency_steps": float(np.std(latency_steps, ddof=0)),
                    "min_latency_steps": float(np.min(latency_steps)),
                    "max_latency_steps": float(np.max(latency_steps)),
                    "mean_spike_count_per_sample": float(np.mean(spike_counts)),
                    "max_possible_spikes_per_sample": float(num_time_steps * test_features.shape[1]),
                    "test_samples": float(test_features.shape[0]),
                }
            )

    return sweep_rows, baseline_accuracy


def main() -> None:
    """Execute Run 005 and save CSV, summary, and trade-off plot."""

    phase_dir = Path(__file__).resolve().parents[1]
    results_dir = phase_dir / "results"
    figures_dir = phase_dir / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    sweep_rows, baseline_accuracy = run_lif_parameter_sweep()

    csv_path = results_dir / "run_005_lif_parameter_sweep.csv"
    summary_path = results_dir / "run_005_lif_parameter_sweep_summary.txt"
    figure_path = figures_dir / "run_005_lif_accuracy_latency_tradeoff.png"

    _write_sweep_csv(csv_path, sweep_rows)
    summary_text = _format_sweep_summary(sweep_rows, baseline_accuracy)
    summary_path.write_text(summary_text + "\n", encoding="utf-8")
    plot_lif_parameter_sweep_tradeoff(sweep_rows, figure_path)

    print(summary_text)
    print("")
    print(f"Saved LIF parameter sweep CSV to: {csv_path}")
    print(f"Saved LIF parameter sweep summary to: {summary_path}")
    print(f"Saved LIF accuracy-latency trade-off figure to: {figure_path}")
    print("")
    print("Run 005 complete: LIF time-step/leak parameter sweep is generated.")
    print("Next step: inspect Run 005 CSV/figure, then commit generated artifacts and documentation.")


if __name__ == "__main__":
    main()
