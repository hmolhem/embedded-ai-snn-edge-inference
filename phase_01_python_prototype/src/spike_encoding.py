"""Rate-based spike encoding utilities for Phase 1 DOA experiments.

The Phase 1 encoder is intentionally hardware-facing and simple. Each
normalized beamspace feature value is interpreted as a Bernoulli firing
probability at each discrete time step. This maps one static feature vector
with shape ``(num_features,)`` into a binary spike train with shape
``(num_time_steps, num_features)``.

This is not intended to be a full biological neuron model. It is a compact
rate-coding stage that prepares normalized DOA features for the later
LIF-inspired class accumulator.
"""

from __future__ import annotations

import numpy as np


def _as_2d_float_array(features: np.ndarray) -> np.ndarray:
    """Return features as a finite two-dimensional floating-point array."""

    feature_array = np.asarray(features, dtype=float)
    if feature_array.ndim != 2:
        raise ValueError(
            "features must be a 2-D array with shape "
            "(num_samples, num_features)."
        )
    if not np.all(np.isfinite(feature_array)):
        raise ValueError("features must contain only finite values.")
    return feature_array


def rate_encode_features(
    features: np.ndarray,
    num_time_steps: int = 20,
    random_seed: int = 42,
    clip: bool = True,
) -> np.ndarray:
    """Convert normalized features into Bernoulli spike trains.

    Parameters
    ----------
    features:
        Two-dimensional normalized feature matrix with shape
        ``(num_samples, num_features)``. Values are expected to lie in
        ``[0, 1]``.
    num_time_steps:
        Number of discrete encoding time steps.
    random_seed:
        Seed used by NumPy's default random generator for reproducibility.
    clip:
        If ``True``, features are clipped to ``[0, 1]`` before encoding. If
        ``False``, the function raises an error when values fall outside the
        valid probability range.

    Returns
    -------
    np.ndarray
        Binary spike tensor with shape
        ``(num_samples, num_time_steps, num_features)`` and dtype ``uint8``.
    """

    if num_time_steps <= 0:
        raise ValueError("num_time_steps must be positive.")

    feature_array = _as_2d_float_array(features)

    if clip:
        probabilities = np.clip(feature_array, 0.0, 1.0)
    else:
        if np.any((feature_array < 0.0) | (feature_array > 1.0)):
            raise ValueError("features must lie in [0, 1] when clip=False.")
        probabilities = feature_array

    rng = np.random.default_rng(random_seed)
    random_values = rng.random(
        size=(feature_array.shape[0], num_time_steps, feature_array.shape[1])
    )
    spikes = random_values < probabilities[:, np.newaxis, :]
    return spikes.astype(np.uint8)


def spike_count_per_sample(spikes: np.ndarray) -> np.ndarray:
    """Return total spike count for each sample."""

    spike_array = np.asarray(spikes)
    if spike_array.ndim != 3:
        raise ValueError(
            "spikes must be a 3-D tensor with shape "
            "(num_samples, num_time_steps, num_features)."
        )
    return spike_array.sum(axis=(1, 2))


def mean_firing_rate(spikes: np.ndarray) -> float:
    """Return the mean firing probability across all samples, times, and features."""

    spike_array = np.asarray(spikes)
    if spike_array.ndim != 3:
        raise ValueError(
            "spikes must be a 3-D tensor with shape "
            "(num_samples, num_time_steps, num_features)."
        )
    return float(spike_array.mean())


def spike_count_summary(spikes: np.ndarray, label: str) -> str:
    """Format a compact text summary of a spike tensor."""

    spike_array = np.asarray(spikes)
    if spike_array.ndim != 3:
        raise ValueError(
            "spikes must be a 3-D tensor with shape "
            "(num_samples, num_time_steps, num_features)."
        )

    counts = spike_count_per_sample(spike_array)
    num_samples, num_time_steps, num_features = spike_array.shape
    max_possible_spikes = num_time_steps * num_features

    lines = [
        f"{label} spike-encoding summary",
        "=" * (len(label) + len(" spike-encoding summary")),
        f"num_samples: {num_samples}",
        f"num_time_steps: {num_time_steps}",
        f"num_features: {num_features}",
        f"max_possible_spikes_per_sample: {max_possible_spikes}",
        f"mean_firing_rate: {mean_firing_rate(spike_array):.6f}",
        f"mean_spike_count_per_sample: {counts.mean():.6f}",
        f"std_spike_count_per_sample: {counts.std(ddof=0):.6f}",
        f"min_spike_count_per_sample: {int(counts.min())}",
        f"max_spike_count_per_sample: {int(counts.max())}",
    ]
    return "\n".join(lines)
