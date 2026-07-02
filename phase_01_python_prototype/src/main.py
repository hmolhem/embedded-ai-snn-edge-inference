"""Phase 1 DOA Python reference-model runner.

Run from the repository root with:

    python phase_01_python_prototype/run_phase_01.py

This run generates a physics-based ULA/DOA dataset, extracts beamspace
features, normalizes them, and evaluates a nearest-centroid DOA-sector
baseline. The train/test split is stratified by both SNR and DOA sector so that
accuracy-versus-SNR results are not distorted by sampling imbalance.
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
from .metrics import (
    accuracy_by_snr,
    accuracy_score,
    confusion_matrix,
    fit_nearest_centroid,
    format_confusion_matrix,
    predict_nearest_centroid,
)
from .plots import (
    plot_accuracy_vs_snr,
    plot_beamspace_response,
    plot_confusion_matrix,
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


def main() -> None:
    """Run the Phase 1 DOA reference baseline."""

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

    centroids = fit_nearest_centroid(
        train_features,
        train_labels,
        num_classes=config.num_classes,
    )
    predicted_labels = predict_nearest_centroid(test_features, centroids)

    overall_accuracy = accuracy_score(test_labels, predicted_labels)
    accuracy_rows = accuracy_by_snr(
        test_labels,
        predicted_labels,
        test_snr_db,
        config.snr_db_values,
    )

    selected_snr = 10.0
    selected_mask = np.isclose(test_snr_db, selected_snr)
    selected_confusion = confusion_matrix(
        test_labels[selected_mask],
        predicted_labels[selected_mask],
        num_classes=config.num_classes,
    )

    dataset_summary_path = results_dir / "run_001_dataset_summary.txt"
    metrics_path = results_dir / "run_001_metrics.txt"
    accuracy_csv_path = results_dir / "run_001_accuracy_vs_snr.csv"

    dataset_summary_path.write_text(summary + "\n", encoding="utf-8")
    _write_accuracy_csv(accuracy_csv_path, accuracy_rows)

    metrics_lines = [
        summary,
        "",
        split_summary,
        "",
        "Run 001 nearest-centroid baseline",
        "=================================",
        f"train_samples: {train_features.shape[0]}",
        f"test_samples: {test_features.shape[0]}",
        f"overall_accuracy: {overall_accuracy:.6f}",
        "",
        "accuracy_vs_snr:",
    ]
    for snr_value, accuracy, count in accuracy_rows:
        metrics_lines.append(
            f"  {snr_value:>5.1f} dB: accuracy={accuracy:.6f}, num_test_samples={count}"
        )
    metrics_lines.extend(["", f"confusion_matrix_at_{selected_snr:.1f}_dB:"])
    metrics_lines.append(format_confusion_matrix(selected_confusion))

    metrics_path.write_text("\n".join(metrics_lines) + "\n", encoding="utf-8")

    plot_accuracy_vs_snr(
        accuracy_rows,
        figures_dir / "run_001_accuracy_vs_snr.png",
    )
    plot_confusion_matrix(
        selected_confusion,
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

    print(summary)
    print("")
    print(split_summary)
    print("")
    print("Run 001 nearest-centroid baseline")
    print("=================================")
    print(f"train_samples: {train_features.shape[0]}")
    print(f"test_samples: {test_features.shape[0]}")
    print(f"overall_accuracy: {overall_accuracy:.4f}")
    print("")
    print("accuracy_vs_snr:")
    for snr_value, accuracy, count in accuracy_rows:
        print(f"  {snr_value:>5.1f} dB: accuracy={accuracy:.4f}, num_test_samples={count}")
    print("")
    print(format_confusion_matrix(selected_confusion))
    print("")
    print(f"Saved dataset summary to: {dataset_summary_path}")
    print(f"Saved metrics to: {metrics_path}")
    print(f"Saved accuracy CSV to: {accuracy_csv_path}")
    print(f"Saved figures to: {figures_dir}")
    print("")
    print("Step 2B complete: stratified nearest-centroid DOA-sector baseline is working.")
    print("Next step: implement spike encoding and LIF-inspired inference.")


if __name__ == "__main__":
    main()
