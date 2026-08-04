"""Deterministic progressive-snapshot dataset construction.

Every sensing budget for one example is derived from a prefix of the same
128-snapshot observation. This preserves the true angle, source realization,
noise realization, class label, and SNR across M=32, 64, and 128.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np

from phase_01_python_prototype.src.dataset import (
    DOAConfig,
    beamspace_features,
    complex_awgn,
    complex_unit_power_source,
    minmax_normalize_train_test,
    sample_covariance,
    sector_label,
    simulate_snapshots,
    steering_vector,
)


DEFAULT_SNAPSHOT_BUDGETS: tuple[int, ...] = (32, 64, 128)


@dataclass(frozen=True)
class ProgressiveDOADataset:
    """Aligned feature views of the same DOA observations."""

    features_by_budget: Mapping[int, np.ndarray]
    labels: np.ndarray
    theta_deg: np.ndarray
    snr_db: np.ndarray
    beam_grid_deg: np.ndarray
    sample_id: np.ndarray
    config: DOAConfig
    snapshot_budgets: tuple[int, ...]

    @property
    def num_samples(self) -> int:
        """Number of aligned observations."""

        return int(self.labels.shape[0])


@dataclass(frozen=True)
class ProgressiveNormalizedSplit:
    """Train/test feature views normalized separately at each budget."""

    train_features_by_budget: Mapping[int, np.ndarray]
    test_features_by_budget: Mapping[int, np.ndarray]
    feature_min_by_budget: Mapping[int, np.ndarray]
    feature_max_by_budget: Mapping[int, np.ndarray]


@dataclass(frozen=True)
class ArrayElementErrors:
    """Fixed per-element gain and phase errors for one virtual device.

    Gain values are amplitude errors in decibels. Phase values are in degrees.
    The errors multiply the ideal receive steering vector and remain fixed for
    every sample in one generated dataset, which models an uncalibrated but
    time-invariant array rather than independent noise on every observation.
    """

    gain_db: tuple[float, ...]
    phase_deg: tuple[float, ...]

    @classmethod
    def ideal(cls, num_elements: int) -> "ArrayElementErrors":
        """Return an ideal array response with no element errors."""

        if num_elements <= 0:
            raise ValueError("num_elements must be positive.")
        zeros = (0.0,) * num_elements
        return cls(gain_db=zeros, phase_deg=zeros)

    def complex_response(self, num_elements: int) -> np.ndarray:
        """Return the validated complex element-response vector."""

        gain = np.asarray(self.gain_db, dtype=float)
        phase = np.asarray(self.phase_deg, dtype=float)
        if gain.shape != (num_elements,) or phase.shape != (num_elements,):
            raise ValueError(
                "gain_db and phase_deg must each contain one value per array "
                "element."
            )
        if not np.all(np.isfinite(gain)) or not np.all(np.isfinite(phase)):
            raise ValueError("Array element errors must contain only finite values.")
        return (10.0 ** (gain / 20.0)) * np.exp(1j * np.deg2rad(phase))


def _validate_snapshot_budgets(
    snapshot_budgets: Iterable[int],
    full_budget: int,
) -> tuple[int, ...]:
    """Return sorted unique budgets and enforce a full-data endpoint."""

    raw_budgets = tuple(snapshot_budgets)
    if not raw_budgets:
        raise ValueError("snapshot_budgets must not be empty.")
    if any(isinstance(value, bool) or not isinstance(value, (int, np.integer)) for value in raw_budgets):
        raise TypeError("Every snapshot budget must be an integer.")

    budgets = tuple(sorted({int(value) for value in raw_budgets}))
    if budgets[0] <= 0:
        raise ValueError("Snapshot budgets must be positive.")
    if budgets[-1] > full_budget:
        raise ValueError("A snapshot budget cannot exceed config.num_snapshots.")
    if budgets[-1] != full_budget:
        raise ValueError(
            "The largest snapshot budget must equal config.num_snapshots so the "
            "full-data fallback remains available."
        )
    return budgets


def _simulate_progressive_snapshots(
    theta_deg: float,
    snr_db: float,
    config: DOAConfig,
    rng: np.random.Generator,
    array_errors: ArrayElementErrors | None,
) -> np.ndarray:
    """Simulate an ideal or fixed-mismatch observation.

    The ideal path delegates to the unchanged Phase 1 implementation so the
    archived M=128 reference remains bit-for-bit reproducible. The mismatch
    path preserves the same source/noise random-number ordering and applies a
    fixed complex response to the receive steering vector.
    """

    if array_errors is None:
        return simulate_snapshots(theta_deg, snr_db, config, rng)

    element_response = array_errors.complex_response(config.num_elements)
    if np.array_equal(element_response, np.ones(config.num_elements, dtype=complex)):
        return simulate_snapshots(theta_deg, snr_db, config, rng)

    ideal_steering = steering_vector(
        theta_deg=theta_deg,
        num_elements=config.num_elements,
        spacing_wavelengths=config.spacing_wavelengths,
    )
    impaired_steering = ideal_steering * element_response
    source = complex_unit_power_source(config.num_snapshots, rng)
    signal = impaired_steering[:, np.newaxis] * source[np.newaxis, :]
    signal_power = float(np.mean(np.abs(signal) ** 2))
    snr_linear = 10.0 ** (snr_db / 10.0)
    noise = complex_awgn(signal.shape, signal_power / snr_linear, rng)
    return signal + noise


def _features_from_conditions(
    config: DOAConfig,
    budgets: tuple[int, ...],
    theta_conditions: np.ndarray,
    snr_conditions: np.ndarray,
    array_errors: ArrayElementErrors | None,
) -> ProgressiveDOADataset:
    """Generate aligned progressive features for explicit angle/SNR pairs."""

    theta = np.asarray(theta_conditions, dtype=float)
    snr = np.asarray(snr_conditions, dtype=float)
    if theta.ndim != 1 or snr.ndim != 1 or theta.shape != snr.shape:
        raise ValueError("theta_conditions and snr_conditions must be aligned 1-D arrays.")
    if theta.size == 0:
        raise ValueError("At least one evaluation condition is required.")
    if not np.all(np.isfinite(theta)) or not np.all(np.isfinite(snr)):
        raise ValueError("Evaluation conditions must contain only finite values.")

    rng = np.random.default_rng(config.random_seed)
    features: dict[int, list[np.ndarray]] = {budget: [] for budget in budgets}
    labels: list[int] = []

    for theta_deg, snr_db in zip(theta, snr, strict=True):
        snapshots = _simulate_progressive_snapshots(
            float(theta_deg),
            float(snr_db),
            config,
            rng,
            array_errors,
        )
        for budget in budgets:
            covariance = sample_covariance(snapshots[:, :budget])
            features[budget].append(
                beamspace_features(
                    covariance,
                    beam_grid_deg=config.beam_grid_deg,
                    spacing_wavelengths=config.spacing_wavelengths,
                )
            )
        labels.append(sector_label(float(theta_deg), config.sector_edges_deg))

    return ProgressiveDOADataset(
        features_by_budget={
            budget: np.vstack(feature_rows).astype(float)
            for budget, feature_rows in features.items()
        },
        labels=np.asarray(labels, dtype=int),
        theta_deg=theta.copy(),
        snr_db=snr.copy(),
        beam_grid_deg=np.asarray(config.beam_grid_deg, dtype=float),
        sample_id=np.arange(theta.size, dtype=int),
        config=config,
        snapshot_budgets=budgets,
    )


def generate_progressive_doa_dataset(
    config: DOAConfig | None = None,
    snapshot_budgets: Iterable[int] = DEFAULT_SNAPSHOT_BUDGETS,
    array_errors: ArrayElementErrors | None = None,
) -> ProgressiveDOADataset:
    """Generate aligned beamspace features from shared snapshot prefixes.

    The loop and random-number ordering intentionally match the Phase 1
    generator. Consequently, the M=128 view is directly comparable with the
    archived Phase 1 feature matrix for the same configuration and seed.
    """

    if config is None:
        config = DOAConfig()
    budgets = _validate_snapshot_budgets(snapshot_budgets, config.num_snapshots)
    rng = np.random.default_rng(config.random_seed)

    features: dict[int, list[np.ndarray]] = {budget: [] for budget in budgets}
    labels: list[int] = []
    theta_values: list[float] = []
    snr_values: list[float] = []
    sample_ids: list[int] = []
    edges = np.asarray(config.sector_edges_deg, dtype=float)

    sample_id = 0
    for snr_db in config.snr_db_values:
        for class_index in range(config.num_classes):
            low = edges[class_index]
            high = edges[class_index + 1]

            for _ in range(config.samples_per_class_per_snr):
                theta_deg = float(rng.uniform(low, high))
                snapshots = _simulate_progressive_snapshots(
                    theta_deg,
                    snr_db,
                    config,
                    rng,
                    array_errors,
                )

                for budget in budgets:
                    covariance = sample_covariance(snapshots[:, :budget])
                    features[budget].append(
                        beamspace_features(
                            covariance,
                            beam_grid_deg=config.beam_grid_deg,
                            spacing_wavelengths=config.spacing_wavelengths,
                        )
                    )

                labels.append(sector_label(theta_deg, config.sector_edges_deg))
                theta_values.append(theta_deg)
                snr_values.append(float(snr_db))
                sample_ids.append(sample_id)
                sample_id += 1

    label_array = np.asarray(labels, dtype=int)
    permutation = rng.permutation(label_array.shape[0])

    return ProgressiveDOADataset(
        features_by_budget={
            budget: np.vstack(feature_rows).astype(float)[permutation]
            for budget, feature_rows in features.items()
        },
        labels=label_array[permutation],
        theta_deg=np.asarray(theta_values, dtype=float)[permutation],
        snr_db=np.asarray(snr_values, dtype=float)[permutation],
        beam_grid_deg=np.asarray(config.beam_grid_deg, dtype=float),
        sample_id=np.asarray(sample_ids, dtype=int)[permutation],
        config=config,
        snapshot_budgets=budgets,
    )


def generate_progressive_evaluation_dataset(
    theta_deg: Iterable[float],
    snr_db: Iterable[float],
    config: DOAConfig | None = None,
    snapshot_budgets: Iterable[int] = DEFAULT_SNAPSHOT_BUDGETS,
    array_errors: ArrayElementErrors | None = None,
) -> ProgressiveDOADataset:
    """Generate aligned features for an explicit evaluation condition list."""

    if config is None:
        config = DOAConfig()
    budgets = _validate_snapshot_budgets(snapshot_budgets, config.num_snapshots)
    return _features_from_conditions(
        config=config,
        budgets=budgets,
        theta_conditions=np.asarray(tuple(theta_deg), dtype=float),
        snr_conditions=np.asarray(tuple(snr_db), dtype=float),
        array_errors=array_errors,
    )


def normalize_progressive_train_test(
    dataset: ProgressiveDOADataset,
    train_index: np.ndarray,
    test_index: np.ndarray,
) -> ProgressiveNormalizedSplit:
    """Normalize every budget using only its corresponding training view.

    Separate train-only statistics are used because the finite-snapshot feature
    distributions differ with M. The sample indices remain identical across
    all budgets.
    """

    train_index = np.asarray(train_index, dtype=int)
    test_index = np.asarray(test_index, dtype=int)
    if train_index.ndim != 1 or test_index.ndim != 1:
        raise ValueError("train_index and test_index must be one-dimensional.")
    if np.intersect1d(train_index, test_index).size:
        raise ValueError("train_index and test_index must not overlap.")

    train_features: dict[int, np.ndarray] = {}
    test_features: dict[int, np.ndarray] = {}
    feature_min: dict[int, np.ndarray] = {}
    feature_max: dict[int, np.ndarray] = {}

    for budget in dataset.snapshot_budgets:
        raw_features = np.asarray(dataset.features_by_budget[budget], dtype=float)
        train_norm, test_norm, train_min, train_max = minmax_normalize_train_test(
            raw_features[train_index],
            raw_features[test_index],
        )
        train_features[budget] = train_norm
        test_features[budget] = test_norm
        feature_min[budget] = train_min
        feature_max[budget] = train_max

    return ProgressiveNormalizedSplit(
        train_features_by_budget=train_features,
        test_features_by_budget=test_features,
        feature_min_by_budget=feature_min,
        feature_max_by_budget=feature_max,
    )


def normalize_progressive_with_reference(
    dataset: ProgressiveDOADataset,
    feature_min_by_budget: Mapping[int, np.ndarray],
    feature_max_by_budget: Mapping[int, np.ndarray],
    sample_index: np.ndarray | None = None,
    eps: float = 1e-12,
) -> dict[int, np.ndarray]:
    """Apply previously fitted train-only normalization to another dataset."""

    if eps <= 0.0:
        raise ValueError("eps must be positive.")
    if sample_index is None:
        indices = np.arange(dataset.num_samples, dtype=int)
    else:
        indices = np.asarray(sample_index, dtype=int)
        if indices.ndim != 1:
            raise ValueError("sample_index must be one-dimensional.")

    normalized: dict[int, np.ndarray] = {}
    for budget in dataset.snapshot_budgets:
        if budget not in feature_min_by_budget or budget not in feature_max_by_budget:
            raise ValueError(f"Missing normalization reference for budget M={budget}.")
        minimum = np.asarray(feature_min_by_budget[budget], dtype=float)
        maximum = np.asarray(feature_max_by_budget[budget], dtype=float)
        raw = np.asarray(dataset.features_by_budget[budget], dtype=float)[indices]
        if minimum.shape != (raw.shape[1],) or maximum.shape != (raw.shape[1],):
            raise ValueError("Normalization reference has an incompatible feature shape.")
        scale = np.maximum(maximum - minimum, eps)
        normalized[budget] = np.clip((raw - minimum) / scale, 0.0, 1.0)
    return normalized
