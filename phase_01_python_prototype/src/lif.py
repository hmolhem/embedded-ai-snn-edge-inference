"""Lightweight LIF-inspired classifier utilities for Phase 1 DOA experiments.

The functions in this module intentionally remain small and hardware-facing.
The classifier is not a full biologically detailed SNN. It is a class-level
leaky membrane accumulator that consumes rate-encoded spike trains and makes a
sector decision from the final membrane potentials.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LIFInferenceResult:
    """Container for LIF-inspired inference outputs."""

    predicted_labels: np.ndarray
    membrane_history: np.ndarray
    final_membrane: np.ndarray
    latency_steps: np.ndarray


def _as_2d_float_array(values: np.ndarray, name: str) -> np.ndarray:
    """Return a finite 2-D floating-point array."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a 2-D array.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values.")
    return array


def _as_3d_spike_array(spikes: np.ndarray) -> np.ndarray:
    """Return a validated binary spike tensor."""

    spike_array = np.asarray(spikes)
    if spike_array.ndim != 3:
        raise ValueError(
            "spikes must be a 3-D tensor with shape "
            "(num_samples, num_time_steps, num_features)."
        )
    if not np.all((spike_array == 0) | (spike_array == 1)):
        raise ValueError("spikes must be binary with values 0 or 1.")
    return spike_array.astype(float, copy=False)


def fit_lif_prototype_weights(centroids: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Create class-template weights and biases from normalized centroids.

    The nearest-centroid decision for a feature vector x can be written as

        argmin_c ||x - c||^2 = argmax_c (2 x^T c - ||c||^2).

    This identity gives a hardware-friendly prototype template: each class has
    a positive weight vector ``2c`` and a class bias ``-||c||^2``. During LIF
    inference, spikes provide a temporal estimate of ``x`` through rate coding.
    """

    centroid_array = _as_2d_float_array(centroids, "centroids")
    weights = 2.0 * centroid_array
    bias = -np.sum(centroid_array * centroid_array, axis=1)
    return weights, bias


def stable_latency_from_history(
    membrane_history: np.ndarray,
    predicted_labels: np.ndarray,
) -> np.ndarray:
    """Return the first time step after which the final decision stays stable.

    The latency proxy is one-indexed: a value of 1 means the winning class after
    the first time step already remains the final winning class. A value equal
    to ``num_time_steps`` means the decision only becomes stable at the end.
    """

    history = np.asarray(membrane_history, dtype=float)
    predictions = np.asarray(predicted_labels, dtype=int)
    if history.ndim != 3:
        raise ValueError(
            "membrane_history must have shape "
            "(num_samples, num_time_steps, num_classes)."
        )
    if predictions.shape != (history.shape[0],):
        raise ValueError("predicted_labels must have shape (num_samples,).")

    winner_history = np.argmax(history, axis=2)
    num_samples, num_time_steps, _ = history.shape
    latency = np.full(num_samples, num_time_steps, dtype=int)

    for sample_index in range(num_samples):
        matches_final = winner_history[sample_index] == predictions[sample_index]
        for time_index in range(num_time_steps):
            if np.all(matches_final[time_index:]):
                latency[sample_index] = time_index + 1
                break

    return latency


def lif_classify(
    spikes: np.ndarray,
    weights: np.ndarray,
    bias: np.ndarray | None = None,
    leak: float = 0.97,
) -> LIFInferenceResult:
    """Classify spike trains using a leaky class-level membrane accumulator.

    Parameters
    ----------
    spikes:
        Binary spike tensor with shape ``(num_samples, num_time_steps,
        num_features)``.
    weights:
        Class-template weight matrix with shape ``(num_classes, num_features)``.
    bias:
        Optional class bias vector with shape ``(num_classes,)``. The prototype
        bias from ``fit_lif_prototype_weights`` makes the LIF score approximate
        the nearest-centroid decision rule in expectation.
    leak:
        Membrane-retention factor. Values near 1 preserve most accumulated
        evidence; smaller values emphasize recent spikes.
    """

    if not 0.0 < leak <= 1.0:
        raise ValueError("leak must be in the interval (0, 1].")

    spike_array = _as_3d_spike_array(spikes)
    weight_array = _as_2d_float_array(weights, "weights")

    num_samples, num_time_steps, num_features = spike_array.shape
    num_classes, weight_features = weight_array.shape
    if weight_features != num_features:
        raise ValueError(
            "weights feature dimension must match spike feature dimension: "
            f"{weight_features} != {num_features}."
        )

    if bias is None:
        bias_array = np.zeros(num_classes, dtype=float)
    else:
        bias_array = np.asarray(bias, dtype=float)
        if bias_array.shape != (num_classes,):
            raise ValueError("bias must have shape (num_classes,).")
        if not np.all(np.isfinite(bias_array)):
            raise ValueError("bias must contain only finite values.")

    membrane = np.zeros((num_samples, num_classes), dtype=float)
    membrane_history = np.zeros((num_samples, num_time_steps, num_classes), dtype=float)

    for time_index in range(num_time_steps):
        input_current = spike_array[:, time_index, :] @ weight_array.T
        input_current = input_current + bias_array[np.newaxis, :]
        membrane = leak * membrane + input_current
        membrane_history[:, time_index, :] = membrane

    final_membrane = membrane_history[:, -1, :]
    predicted_labels = np.argmax(final_membrane, axis=1).astype(int)
    latency_steps = stable_latency_from_history(membrane_history, predicted_labels)

    return LIFInferenceResult(
        predicted_labels=predicted_labels,
        membrane_history=membrane_history,
        final_membrane=final_membrane,
        latency_steps=latency_steps,
    )


def lif_inference_summary(
    result: LIFInferenceResult,
    label: str = "LIF-inspired inference",
) -> str:
    """Format a compact text summary for LIF-inspired inference."""

    final_membrane = np.asarray(result.final_membrane, dtype=float)
    latency_steps = np.asarray(result.latency_steps, dtype=float)

    lines = [
        label,
        "=" * len(label),
        f"num_samples: {final_membrane.shape[0]}",
        f"num_classes: {final_membrane.shape[1]}",
        f"mean_latency_steps: {latency_steps.mean():.6f}",
        f"std_latency_steps: {latency_steps.std(ddof=0):.6f}",
        f"min_latency_steps: {int(latency_steps.min())}",
        f"max_latency_steps: {int(latency_steps.max())}",
        f"mean_final_membrane: {final_membrane.mean():.6f}",
        f"std_final_membrane: {final_membrane.std(ddof=0):.6f}",
    ]
    return "\n".join(lines)
