"""Metrics and baseline classifiers for Phase 1 DOA experiments."""

from __future__ import annotations

import numpy as np


def fit_nearest_centroid(
    features: np.ndarray,
    labels: np.ndarray,
    num_classes: int,
) -> np.ndarray:
    """Estimate one centroid per class from feature vectors."""

    centroids: list[np.ndarray] = []
    for class_index in range(num_classes):
        class_features = features[labels == class_index]
        if class_features.size == 0:
            raise ValueError(f"No training samples found for class {class_index}.")
        centroids.append(np.mean(class_features, axis=0))

    return np.vstack(centroids)


def predict_nearest_centroid(features: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """Predict labels using squared Euclidean distance to class centroids."""

    diff = features[:, np.newaxis, :] - centroids[np.newaxis, :, :]
    distances = np.sum(diff * diff, axis=2)
    return np.argmin(distances, axis=1).astype(int)


def accuracy_score(labels_true: np.ndarray, labels_pred: np.ndarray) -> float:
    """Return classification accuracy as a floating-point fraction."""

    if labels_true.shape[0] == 0:
        raise ValueError("Cannot compute accuracy for an empty label array.")
    return float(np.mean(labels_true == labels_pred))


def confusion_matrix(
    labels_true: np.ndarray,
    labels_pred: np.ndarray,
    num_classes: int,
) -> np.ndarray:
    """Compute a row-normal count confusion matrix."""

    matrix = np.zeros((num_classes, num_classes), dtype=int)
    for true_label, pred_label in zip(labels_true, labels_pred, strict=True):
        matrix[int(true_label), int(pred_label)] += 1
    return matrix


def accuracy_by_snr(
    labels_true: np.ndarray,
    labels_pred: np.ndarray,
    snr_db: np.ndarray,
    snr_values: tuple[float, ...],
) -> list[tuple[float, float, int]]:
    """Return accuracy for each SNR value.

    Returns a list of tuples:

        (snr_db_value, accuracy, sample_count)
    """

    rows: list[tuple[float, float, int]] = []
    for value in snr_values:
        mask = np.isclose(snr_db, value)
        count = int(np.sum(mask))
        if count == 0:
            rows.append((float(value), float("nan"), 0))
            continue
        rows.append((float(value), accuracy_score(labels_true[mask], labels_pred[mask]), count))
    return rows


def format_confusion_matrix(matrix: np.ndarray) -> str:
    """Format a confusion matrix for text reports."""

    lines = ["Confusion matrix (rows=true, columns=predicted):"]
    for row in matrix:
        lines.append("  " + " ".join(f"{int(value):5d}" for value in row))
    return "\n".join(lines)
