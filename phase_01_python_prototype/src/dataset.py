"""Physics-based ULA/DOA dataset utilities for Phase 1.

This module implements the first engineering data model for the project:

    x[m] = a(theta) s[m] + n[m]

where a(theta) is the steering vector of a uniform linear array (ULA),
s[m] is a complex narrowband source sample, and n[m] is complex Gaussian
noise. Compact beamspace features are extracted from the sample covariance
matrix and later used for spike-based DOA-sector inference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class DOAConfig:
    """Configuration for the Phase 1 DOA reference dataset."""

    num_elements: int = 8
    num_snapshots: int = 128
    spacing_wavelengths: float = 0.5
    doa_min_deg: float = -60.0
    doa_max_deg: float = 60.0
    sector_edges_deg: tuple[float, ...] = (-60.0, -30.0, 0.0, 30.0, 60.0)
    beam_grid_deg: tuple[float, ...] = (-60.0, -45.0, -30.0, -15.0, 0.0, 15.0, 30.0, 45.0, 60.0)
    snr_db_values: tuple[float, ...] = (-10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0)
    samples_per_class_per_snr: int = 100
    random_seed: int = 42

    @property
    def num_classes(self) -> int:
        return len(self.sector_edges_deg) - 1

    @property
    def num_features(self) -> int:
        return len(self.beam_grid_deg)


def steering_vector(
    theta_deg: float,
    num_elements: int = 8,
    spacing_wavelengths: float = 0.5,
) -> np.ndarray:
    """Return the complex ULA steering vector for angle ``theta_deg``.

    The element index starts at n = 0. The spacing is expressed in wavelengths,
    so d/lambda = spacing_wavelengths. For half-wavelength spacing this is 0.5.

    a_n(theta) = exp(-j 2 pi (d/lambda) n sin(theta))
    """

    theta_rad = np.deg2rad(theta_deg)
    element_index = np.arange(num_elements, dtype=float)
    phase = -2.0j * np.pi * spacing_wavelengths * element_index * np.sin(theta_rad)
    return np.exp(phase)


def complex_unit_power_source(num_snapshots: int, rng: np.random.Generator) -> np.ndarray:
    """Generate a complex narrowband source sequence with unit expected power."""

    real = rng.standard_normal(num_snapshots)
    imag = rng.standard_normal(num_snapshots)
    return (real + 1j * imag) / np.sqrt(2.0)


def complex_awgn(shape: tuple[int, ...], noise_power: float, rng: np.random.Generator) -> np.ndarray:
    """Generate circular complex AWGN with the requested total complex power."""

    sigma = np.sqrt(noise_power / 2.0)
    return sigma * (rng.standard_normal(shape) + 1j * rng.standard_normal(shape))


def simulate_snapshots(
    theta_deg: float,
    snr_db: float,
    config: DOAConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Simulate received ULA snapshots for one source and one SNR.

    Returns
    -------
    np.ndarray
        Complex array snapshot matrix with shape ``(N, M)``.
    """

    a_theta = steering_vector(
        theta_deg=theta_deg,
        num_elements=config.num_elements,
        spacing_wavelengths=config.spacing_wavelengths,
    )
    source = complex_unit_power_source(config.num_snapshots, rng)

    signal = a_theta[:, np.newaxis] * source[np.newaxis, :]
    signal_power = float(np.mean(np.abs(signal) ** 2))
    snr_linear = 10.0 ** (snr_db / 10.0)
    noise_power = signal_power / snr_linear
    noise = complex_awgn(signal.shape, noise_power, rng)

    return signal + noise


def sample_covariance(snapshot_matrix: np.ndarray) -> np.ndarray:
    """Compute the sample covariance matrix Rxx = (1/M) X X^H."""

    if snapshot_matrix.ndim != 2:
        raise ValueError("snapshot_matrix must be a 2D array with shape (N, M).")
    num_snapshots = snapshot_matrix.shape[1]
    return (snapshot_matrix @ snapshot_matrix.conj().T) / float(num_snapshots)


def beamspace_features(
    covariance: np.ndarray,
    beam_grid_deg: Iterable[float],
    spacing_wavelengths: float = 0.5,
) -> np.ndarray:
    """Extract compact beamspace energy features from a covariance matrix.

    E(theta_g) = |a(theta_g)^H Rxx a(theta_g)| / N^2

    The division by N^2 keeps the feature scale moderate and makes later
    normalization more stable.
    """

    num_elements = covariance.shape[0]
    energies: list[float] = []

    for theta_g in beam_grid_deg:
        a_grid = steering_vector(theta_g, num_elements, spacing_wavelengths)
        energy = np.abs(a_grid.conj().T @ covariance @ a_grid) / float(num_elements**2)
        energies.append(float(np.real(energy)))

    return np.asarray(energies, dtype=float)


def sector_label(theta_deg: float, sector_edges_deg: Iterable[float]) -> int:
    """Return the coarse DOA-sector label for ``theta_deg``."""

    edges = np.asarray(tuple(sector_edges_deg), dtype=float)
    if theta_deg < edges[0] or theta_deg > edges[-1]:
        raise ValueError(f"theta_deg={theta_deg} is outside the configured sector range.")

    label = int(np.searchsorted(edges, theta_deg, side="right") - 1)
    return int(np.clip(label, 0, len(edges) - 2))


def generate_doa_dataset(config: DOAConfig | None = None) -> dict[str, np.ndarray | DOAConfig]:
    """Generate the Phase 1 physics-based DOA dataset.

    The dataset is balanced by SNR and class. For each SNR and sector, true DOA
    angles are drawn uniformly inside the sector interval. Each angle produces a
    ULA snapshot matrix, a sample covariance matrix, and a compact beamspace
    feature vector.
    """

    if config is None:
        config = DOAConfig()

    rng = np.random.default_rng(config.random_seed)

    features: list[np.ndarray] = []
    labels: list[int] = []
    theta_values: list[float] = []
    snr_values: list[float] = []

    edges = np.asarray(config.sector_edges_deg, dtype=float)

    for snr_db in config.snr_db_values:
        for class_index in range(config.num_classes):
            low = edges[class_index]
            high = edges[class_index + 1]

            for _ in range(config.samples_per_class_per_snr):
                theta_deg = float(rng.uniform(low, high))
                snapshots = simulate_snapshots(theta_deg, snr_db, config, rng)
                covariance = sample_covariance(snapshots)
                feature_vector = beamspace_features(
                    covariance,
                    beam_grid_deg=config.beam_grid_deg,
                    spacing_wavelengths=config.spacing_wavelengths,
                )

                features.append(feature_vector)
                labels.append(sector_label(theta_deg, config.sector_edges_deg))
                theta_values.append(theta_deg)
                snr_values.append(float(snr_db))

    feature_array = np.vstack(features).astype(float)
    label_array = np.asarray(labels, dtype=int)
    theta_array = np.asarray(theta_values, dtype=float)
    snr_array = np.asarray(snr_values, dtype=float)

    permutation = rng.permutation(feature_array.shape[0])

    return {
        "features": feature_array[permutation],
        "labels": label_array[permutation],
        "theta_deg": theta_array[permutation],
        "snr_db": snr_array[permutation],
        "beam_grid_deg": np.asarray(config.beam_grid_deg, dtype=float),
        "config": config,
    }


def train_test_split_by_index(
    num_samples: int,
    train_fraction: float = 0.70,
    random_seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Return randomized train/test indices for a dataset."""

    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1.")

    rng = np.random.default_rng(random_seed)
    indices = rng.permutation(num_samples)
    num_train = int(round(train_fraction * num_samples))
    return indices[:num_train], indices[num_train:]


def minmax_normalize_train_test(
    train_features: np.ndarray,
    test_features: np.ndarray,
    eps: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Normalize train/test features using train-set min/max statistics."""

    feature_min = np.min(train_features, axis=0)
    feature_max = np.max(train_features, axis=0)
    scale = np.maximum(feature_max - feature_min, eps)

    train_norm = (train_features - feature_min) / scale
    test_norm = (test_features - feature_min) / scale

    return (
        np.clip(train_norm, 0.0, 1.0),
        np.clip(test_norm, 0.0, 1.0),
        feature_min,
        feature_max,
    )


def dataset_summary(dataset: dict[str, np.ndarray | DOAConfig]) -> str:
    """Create a human-readable summary of the generated DOA dataset."""

    features = np.asarray(dataset["features"])
    labels = np.asarray(dataset["labels"])
    snr_db = np.asarray(dataset["snr_db"])
    theta_deg = np.asarray(dataset["theta_deg"])
    config = dataset["config"]
    assert isinstance(config, DOAConfig)

    lines = [
        "Phase 1 DOA dataset summary",
        "===========================",
        f"num_samples: {features.shape[0]}",
        f"num_features: {features.shape[1]}",
        f"num_elements: {config.num_elements}",
        f"num_snapshots: {config.num_snapshots}",
        f"spacing_wavelengths: {config.spacing_wavelengths}",
        f"theta_range_deg: [{theta_deg.min():.2f}, {theta_deg.max():.2f}]",
        f"snr_values_db: {list(config.snr_db_values)}",
        f"beam_grid_deg: {list(config.beam_grid_deg)}",
        "",
        "class_counts:",
    ]

    for class_index in range(config.num_classes):
        count = int(np.sum(labels == class_index))
        lines.append(f"  class_{class_index}: {count}")

    lines.extend(["", "snr_counts:"])
    for snr_value in config.snr_db_values:
        count = int(np.sum(np.isclose(snr_db, snr_value)))
        lines.append(f"  {snr_value:>5.1f} dB: {count}")

    lines.extend(
        [
            "",
            "feature_range:",
            f"  min: {features.min():.6f}",
            f"  max: {features.max():.6f}",
            f"  mean: {features.mean():.6f}",
        ]
    )

    return "\n".join(lines)
