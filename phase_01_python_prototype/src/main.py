"""Phase 1 DOA Python reference-model runner.

Run from the repository root with:

    python phase_01_python_prototype/run_phase_01.py

This run generates a physics-based ULA/DOA dataset, extracts beamspace
features, normalizes them, evaluates a nearest-centroid DOA-sector baseline,
validates a rate-based spike encoder, and evaluates a lightweight LIF-inspired
class accumulator on the encoded spike trains. The train/test split is
stratified by both SNR and DOA sector so that accuracy-versus-SNR results are
not distorted by sampling imbalance.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .dataset import (
    DOAConfig,
    dataset_summary,
    generate_doa_dataset,
    minmax_normalize_train_test,
    stratified_train_test_split_by_snr_and_class,
)
from .lif import (
    fit_lif_prototype_weights,
    lif_classify,
    lif_inference_summary,
)
from .metrics import (
    accuracy_by_snr,
    accuracy_score,
    confusion_matrix,
    fit_nearest_centroid,
    format_confusion_matrix,
    predict_nearest_centroid,
)
from .plots import (
    plot_accuracy_comparison_vs_snr,
    plot_accuracy_vs_snr,
    plot_beamspace_response,
    plot_confusion_matrix,
    plot_latency_vs_snr,
    plot_spike_count_distribution,
)
from .spike_encoding import (
    rate_encode_features,
    spike_count_per_sample,
    spike_count_summary,
)


def _write_accuracy_csv(
    output_path: Path,
    rows: list[tuple[float, float, int]],
) -> None:
    """Write SNR accuracy rows to CSV."""

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["snr_db", "accuracy", "num_test_samples"])
        for snr_db, accuracy, count in rows:
            writer.writerow([f"{snr_db:.1f}", f"{accuracy:.6f}", count])


def _latency_by_snr(
    latency_steps: np.ndarray,
    snr_db: np.ndarray,
    snr_values: tuple[float, ...],
) -> list[tuple[float, float, int]]:
    """Return mean stable-decision latency for each SNR value."""

    rows: list[tuple[float, float, int]] = []
    for value in snr_values:
        mask = np.isclose(snr_db, value)
        count = int(np.sum(mask))
        if count == 0:
            rows.append((float(value), float("nan"), 0))
            continue
        rows.append((float(value), float(np.mean(latency_steps[mask])), count))
    return rows


def _write_latency_csv(
    output_path: Path,
    rows: list[tuple[float, float, int]],
) -> None:
    """Write SNR latency rows to CSV."""

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["snr_db", "mean_latency_steps", "num_test_samples"])
        for snr_db, mean_latency, count in rows:
            writer.writerow([f"{snr_db:.1f}", f"{mean_latency:.6f}", count])


def _format_accuracy_rows(rows: list[tuple[float, float, int]]) -> list[str]:
    """Format accuracy-versus-SNR rows for text reports."""

    return [
        f"  {snr_value:>5.1f} dB: accuracy={accuracy:.6f}, num_test_samples={count}"
        for snr_value, accuracy, count in rows
    ]


def _format_latency_rows(rows: list[tuple[float, float, int]]) -> list[str]:
    """Format latency-versus-SNR rows for text reports."""

    return [
        f"  {snr_value:>5.1f} dB: mean_latency_steps={latency:.6f}, "
        f"num_test_samples={count}"
        for snr_value, latency, count in rows
    ]


def main() -> None:
    """Run the Phase 1 DOA reference baseline, spike encoder, and LIF model."""

    phase_dir = Path(__file__).resolve().parents[1]
    results_dir = phase_dir / "results"
    figures_dir = phase_dir / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    config = DOAConfig()
    dataset = generate_doa_dataset(config)
    summary = dataset_summary(dataset)

    features = np.asarray(dataset["features"], dtype=float)
    labels = np.asarray(dataset["labels"], dtype=int)
    snr_db = np.asarray(dataset["snr_db"], dtype=float)
    theta_deg = np.asarray(dataset["theta_deg"], dtype=float)
    beam_grid_deg = np.asarray(dataset["beam_grid_deg"], dtype=float)

    train_index, test_index, split_summary = stratified_train_test_split_by_snr_and_class(
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
    test_snr_db = snr_db[test_index]

    train_features, test_features, _, _ = minmax_normalize_train_test(
        train_features_raw,
        test_features_raw,
    )

    # Run 001: non-spiking nearest-centroid baseline on normalized features.
    centroids = fit_nearest_centroid(
        train_features,
        train_labels,
        num_classes=config.num_classes,
    )
    baseline_predicted_labels = predict_nearest_centroid(test_features, centroids)
    baseline_overall_accuracy = accuracy_score(test_labels, baseline_predicted_labels)
    baseline_accuracy_rows = accuracy_by_snr(
        test_labels,
        baseline_predicted_labels,
        test_snr_db,
        config.snr_db_values,
    )

    selected_snr = 10.0
    selected_mask = np.isclose(test_snr_db, selected_snr)
    baseline_confusion = confusion_matrix(
        test_labels[selected_mask],
        baseline_predicted_labels[selected_mask],
        num_classes=config.num_classes,
    )

    # Run 002: rate-based spike encoding of the normalized features.
    num_spike_time_steps = 20
    train_spikes = rate_encode_features(
        train_features,
        num_time_steps=num_spike_time_steps,
        random_seed=config.random_seed + 101,
    )
    test_spikes = rate_encode_features(
        test_features,
        num_time_steps=num_spike_time_steps,
        random_seed=config.random_seed + 102,
    )
    test_spike_counts = spike_count_per_sample(test_spikes)

    spike_summary = "\n\n".join(
        [
            spike_count_summary(train_spikes, label="Train"),
            spike_count_summary(test_spikes, label="Test"),
        ]
    )

    # Run 003: LIF-inspired class-level inference on spike trains.
    lif_weights, lif_bias = fit_lif_prototype_weights(centroids)
    lif_result = lif_classify(
        test_spikes,
        weights=lif_weights,
        bias=lif_bias,
        leak=0.97,
    )
    lif_predicted_labels = lif_result.predicted_labels
    lif_overall_accuracy = accuracy_score(test_labels, lif_predicted_labels)
    lif_accuracy_rows = accuracy_by_snr(
        test_labels,
        lif_predicted_labels,
        test_snr_db,
        config.snr_db_values,
    )
    lif_latency_rows = _latency_by_snr(
        lif_result.latency_steps,
        test_snr_db,
        config.snr_db_values,
    )
    lif_confusion = confusion_matrix(
        test_labels[selected_mask],
        lif_predicted_labels[selected_mask],
        num_classes=config.num_classes,
    )
    lif_summary = lif_inference_summary(lif_result)

    dataset_summary_path = results_dir / "run_001_dataset_summary.txt"
    metrics_path = results_dir / "run_001_metrics.txt"
    baseline_accuracy_csv_path = results_dir / "run_001_accuracy_vs_snr.csv"
    spike_summary_path = results_dir / "run_002_spike_encoding_summary.txt"
    lif_metrics_path = results_dir / "run_003_lif_metrics.txt"
    lif_accuracy_csv_path = results_dir / "run_003_lif_accuracy_vs_snr.csv"
    lif_latency_csv_path = results_dir / "run_003_lif_latency_vs_snr.csv"

    dataset_summary_path.write_text(summary + "\n", encoding="utf-8")
    _write_accuracy_csv(baseline_accuracy_csv_path, baseline_accuracy_rows)
    spike_summary_path.write_text(spike_summary + "\n", encoding="utf-8")
    _write_accuracy_csv(lif_accuracy_csv_path, lif_accuracy_rows)
    _write_latency_csv(lif_latency_csv_path, lif_latency_rows)

    metrics_lines = [
        summary,
        "",
        split_summary,
        "",
        "Run 001 nearest-centroid baseline",
        "=================================",
        f"train_samples: {train_features.shape[0]}",
        f"test_samples: {test_features.shape[0]}",
        f"overall_accuracy: {baseline_overall_accuracy:.6f}",
        "",
        "accuracy_vs_snr:",
        *_format_accuracy_rows(baseline_accuracy_rows),
        "",
        f"confusion_matrix_at_{selected_snr:.1f}_dB:",
        format_confusion_matrix(baseline_confusion),
        "",
        "Run 002 rate-based spike encoding",
        "=================================",
        spike_summary,
        "",
        "Run 003 LIF-inspired spike classifier",
        "====================================",
        f"overall_accuracy: {lif_overall_accuracy:.6f}",
        f"leak: {0.97:.2f}",
        f"num_time_steps: {num_spike_time_steps}",
        "",
        lif_summary,
        "",
        "accuracy_vs_snr:",
        *_format_accuracy_rows(lif_accuracy_rows),
        "",
        "mean_latency_vs_snr:",
        *_format_latency_rows(lif_latency_rows),
        "",
        f"confusion_matrix_at_{selected_snr:.1f}_dB:",
        format_confusion_matrix(lif_confusion),
    ]

    metrics_text = "\n".join(metrics_lines) + "\n"
    metrics_path.write_text(metrics_text, encoding="utf-8")
    lif_metrics_path.write_text(
        "\n".join(
            [
                "Run 003 LIF-inspired spike classifier",
                "====================================",
                f"overall_accuracy: {lif_overall_accuracy:.6f}",
                f"leak: {0.97:.2f}",
                f"num_time_steps: {num_spike_time_steps}",
                "",
                lif_summary,
                "",
                "accuracy_vs_snr:",
                *_format_accuracy_rows(lif_accuracy_rows),
                "",
                "mean_latency_vs_snr:",
                *_format_latency_rows(lif_latency_rows),
                "",
                f"confusion_matrix_at_{selected_snr:.1f}_dB:",
                format_confusion_matrix(lif_confusion),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    plot_accuracy_vs_snr(
        baseline_accuracy_rows,
        figures_dir / "run_001_accuracy_vs_snr.png",
        title="Nearest-Centroid DOA-Sector Accuracy vs SNR",
    )
    plot_confusion_matrix(
        baseline_confusion,
        figures_dir / "run_001_confusion_matrix_snr_10db.png",
        title="Nearest-Centroid Confusion Matrix at 10 dB",
    )

    example_candidates = np.where(np.isclose(snr_db, 20.0))[0]
    example_index = int(example_candidates[0]) if example_candidates.size else 0
    plot_beamspace_response(
        beam_grid_deg,
        features[example_index],
        theta_deg=float(theta_deg[example_index]),
        output_path=figures_dir / "run_001_example_beamspace_response.png",
    )
    plot_spike_count_distribution(
        test_spike_counts,
        figures_dir / "run_002_spike_count_distribution.png",
        num_time_steps=num_spike_time_steps,
        num_features=test_features.shape[1],
    )
    plot_accuracy_vs_snr(
        lif_accuracy_rows,
        figures_dir / "run_003_lif_accuracy_vs_snr.png",
        title="LIF-Inspired Spike Classifier Accuracy vs SNR",
    )
    plot_confusion_matrix(
        lif_confusion,
        figures_dir / "run_003_lif_confusion_matrix_snr_10db.png",
        title="LIF-Inspired Confusion Matrix at 10 dB",
    )

    plot_accuracy_comparison_vs_snr(
        baseline_accuracy_rows,
        lif_accuracy_rows,
        figures_dir / "run_004_accuracy_comparison_vs_snr.png",
        title="Nearest-Centroid vs LIF-Inspired Accuracy vs SNR",
    )
    plot_latency_vs_snr(
        lif_latency_rows,
        figures_dir / "run_004_lif_latency_vs_snr.png",
        num_time_steps=num_spike_time_steps,
        title="LIF Stable-Decision Latency vs SNR",
    )

    print(metrics_text)
    print(f"Saved dataset summary to: {dataset_summary_path}")
    print(f"Saved combined metrics to: {metrics_path}")
    print(f"Saved baseline accuracy CSV to: {baseline_accuracy_csv_path}")
    print(f"Saved spike-encoding summary to: {spike_summary_path}")
    print(f"Saved LIF metrics to: {lif_metrics_path}")
    print(f"Saved LIF accuracy CSV to: {lif_accuracy_csv_path}")
    print(f"Saved LIF latency CSV to: {lif_latency_csv_path}")
    print(f"Saved accuracy comparison figure to: {figures_dir / 'run_004_accuracy_comparison_vs_snr.png'}")
    print(f"Saved LIF latency figure to: {figures_dir / 'run_004_lif_latency_vs_snr.png'}")
    print(f"Saved figures to: {figures_dir}")
    print("")
    print("Step 3B complete: LIF-inspired spike classifier is implemented.")
    print("Next step: run locally, inspect accuracy/latency, then create the next handoff.")


if __name__ == "__main__":
    main()
