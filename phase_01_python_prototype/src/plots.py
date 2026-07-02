"""Plotting utilities for Phase 1 DOA experiments."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_accuracy_vs_snr(
    accuracy_rows: list[tuple[float, float, int]],
    output_path: Path,
    title: str = "DOA-Sector Accuracy vs SNR",
) -> None:
    """Save accuracy-versus-SNR plot."""

    snr_values = [row[0] for row in accuracy_rows]
    accuracies = [100.0 * row[1] for row in accuracy_rows]

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(snr_values, accuracies, marker="o")
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title(title)
    ax.grid(True)
    ax.set_ylim(0.0, 105.0)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_confusion_matrix(
    matrix: np.ndarray,
    output_path: Path,
    title: str,
) -> None:
    """Save a confusion-matrix figure."""

    fig, ax = plt.subplots(figsize=(5.5, 4.8))
    image = ax.imshow(matrix)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    num_classes = matrix.shape[0]
    ax.set_xticks(np.arange(num_classes))
    ax.set_yticks(np.arange(num_classes))
    ax.set_xlabel("Predicted sector")
    ax.set_ylabel("True sector")
    ax.set_title(title)

    for row in range(num_classes):
        for col in range(num_classes):
            ax.text(col, row, str(int(matrix[row, col])), ha="center", va="center")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_beamspace_response(
    beam_grid_deg: np.ndarray,
    feature_vector: np.ndarray,
    theta_deg: float,
    output_path: Path,
) -> None:
    """Save one example beamspace-response feature vector."""

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(beam_grid_deg, feature_vector, marker="o")
    ax.axvline(theta_deg, linestyle="--")
    ax.set_xlabel("Beam grid angle (deg)")
    ax.set_ylabel("Beamspace energy")
    ax.set_title(f"Example Beamspace Response, true DOA = {theta_deg:.2f} deg")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_spike_count_distribution(
    spike_counts: np.ndarray,
    output_path: Path,
    num_time_steps: int,
    num_features: int,
) -> None:
    """Save a histogram of total spike count per sample."""

    counts = np.asarray(spike_counts, dtype=float)
    if counts.ndim != 1:
        raise ValueError("spike_counts must be a one-dimensional array.")

    max_possible_spikes = num_time_steps * num_features

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.hist(counts, bins=30)
    ax.axvline(float(counts.mean()), linestyle="--")
    ax.set_xlabel("Spike count per sample")
    ax.set_ylabel("Number of samples")
    ax.set_title(
        "Rate-Encoded Spike-Count Distribution "
        f"(T={num_time_steps}, F={num_features})"
    )
    ax.set_xlim(0.0, float(max_possible_spikes))
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
