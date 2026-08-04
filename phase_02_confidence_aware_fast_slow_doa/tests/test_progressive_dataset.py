"""Tests for aligned progressive-snapshot feature generation."""

from __future__ import annotations

import unittest
from dataclasses import replace

import numpy as np

from phase_01_python_prototype.src.dataset import (
    DOAConfig,
    generate_doa_dataset,
    stratified_train_test_split_by_snr_and_class,
)
from phase_02_confidence_aware_fast_slow_doa.src.progressive_dataset import (
    ArrayElementErrors,
    generate_progressive_doa_dataset,
    generate_progressive_evaluation_dataset,
    normalize_progressive_train_test,
    normalize_progressive_with_reference,
)


def _small_config() -> DOAConfig:
    return replace(
        DOAConfig(),
        snr_db_values=(-5.0, 5.0),
        samples_per_class_per_snr=4,
        random_seed=17,
    )


class ProgressiveDatasetTests(unittest.TestCase):
    """Determinism, compatibility, normalization, and validation tests."""

    def test_progressive_dataset_is_exactly_repeatable(self) -> None:
        config = _small_config()
        first = generate_progressive_doa_dataset(config, (32, 64, 128))
        second = generate_progressive_doa_dataset(config, (32, 64, 128))

        self.assertTrue(np.array_equal(first.labels, second.labels))
        self.assertTrue(np.array_equal(first.theta_deg, second.theta_deg))
        self.assertTrue(np.array_equal(first.snr_db, second.snr_db))
        self.assertTrue(np.array_equal(first.sample_id, second.sample_id))
        for budget in first.snapshot_budgets:
            self.assertTrue(
                np.array_equal(
                    first.features_by_budget[budget],
                    second.features_by_budget[budget],
                )
            )

    def test_full_budget_matches_phase_1_generator(self) -> None:
        config = _small_config()
        progressive = generate_progressive_doa_dataset(config, (32, 64, 128))
        phase_1 = generate_doa_dataset(config)

        self.assertTrue(np.array_equal(progressive.labels, phase_1["labels"]))
        self.assertTrue(np.array_equal(progressive.theta_deg, phase_1["theta_deg"]))
        self.assertTrue(np.array_equal(progressive.snr_db, phase_1["snr_db"]))
        self.assertTrue(
            np.allclose(
                progressive.features_by_budget[128],
                phase_1["features"],
                rtol=0.0,
                atol=1e-12,
            )
        )

    def test_normalization_uses_common_split_and_valid_shapes(self) -> None:
        config = _small_config()
        progressive = generate_progressive_doa_dataset(config, (32, 64, 128))
        train_index, test_index, _ = stratified_train_test_split_by_snr_and_class(
            labels=progressive.labels,
            snr_db=progressive.snr_db,
            snr_values=config.snr_db_values,
            num_classes=config.num_classes,
            train_fraction=0.75,
            random_seed=config.random_seed,
        )
        normalized = normalize_progressive_train_test(progressive, train_index, test_index)

        for budget in progressive.snapshot_budgets:
            self.assertEqual(
                normalized.train_features_by_budget[budget].shape,
                (train_index.size, config.num_features),
            )
            self.assertEqual(
                normalized.test_features_by_budget[budget].shape,
                (test_index.size, config.num_features),
            )
            self.assertTrue(np.all(normalized.train_features_by_budget[budget] >= 0.0))
            self.assertTrue(np.all(normalized.train_features_by_budget[budget] <= 1.0))
            self.assertTrue(np.all(normalized.test_features_by_budget[budget] >= 0.0))
            self.assertTrue(np.all(normalized.test_features_by_budget[budget] <= 1.0))

    def test_invalid_snapshot_budgets_are_rejected(self) -> None:
        for budgets in ((), (0, 128), (32, 64), (32, 256)):
            with self.subTest(budgets=budgets):
                with self.assertRaises((TypeError, ValueError)):
                    generate_progressive_doa_dataset(_small_config(), budgets)

    def test_ideal_error_object_preserves_phase_1_compatibility(self) -> None:
        config = _small_config()
        default = generate_progressive_doa_dataset(config, (32, 128))
        explicit_ideal = generate_progressive_doa_dataset(
            config,
            (32, 128),
            array_errors=ArrayElementErrors.ideal(config.num_elements),
        )

        for budget in default.snapshot_budgets:
            self.assertTrue(
                np.array_equal(
                    default.features_by_budget[budget],
                    explicit_ideal.features_by_budget[budget],
                )
            )

    def test_fixed_mismatch_preserves_paired_metadata_but_changes_features(self) -> None:
        config = _small_config()
        ideal = generate_progressive_doa_dataset(config, (32, 128))
        mismatch = ArrayElementErrors(
            gain_db=(0.5, -0.5, 0.25, -0.25, 0.4, -0.4, 0.1, -0.1),
            phase_deg=(5.0, -5.0, 2.0, -2.0, 4.0, -4.0, 1.0, -1.0),
        )
        impaired = generate_progressive_doa_dataset(
            config,
            (32, 128),
            array_errors=mismatch,
        )

        self.assertTrue(np.array_equal(ideal.sample_id, impaired.sample_id))
        self.assertTrue(np.array_equal(ideal.labels, impaired.labels))
        self.assertTrue(np.array_equal(ideal.theta_deg, impaired.theta_deg))
        self.assertTrue(np.array_equal(ideal.snr_db, impaired.snr_db))
        self.assertFalse(
            np.array_equal(
                ideal.features_by_budget[128],
                impaired.features_by_budget[128],
            )
        )

    def test_explicit_evaluation_and_reference_normalization(self) -> None:
        config = _small_config()
        training = generate_progressive_doa_dataset(config, (32, 128))
        train_index, test_index, _ = stratified_train_test_split_by_snr_and_class(
            labels=training.labels,
            snr_db=training.snr_db,
            snr_values=config.snr_db_values,
            num_classes=config.num_classes,
            train_fraction=0.75,
            random_seed=config.random_seed,
        )
        normalized = normalize_progressive_train_test(
            training,
            train_index,
            test_index,
        )
        evaluation = generate_progressive_evaluation_dataset(
            theta_deg=(-30.5, -29.5, -0.5, 0.5, 29.5, 30.5),
            snr_db=(5.0,) * 6,
            config=config,
            snapshot_budgets=(32, 128),
        )
        transformed = normalize_progressive_with_reference(
            evaluation,
            normalized.feature_min_by_budget,
            normalized.feature_max_by_budget,
        )

        self.assertEqual(evaluation.num_samples, 6)
        self.assertTrue(np.array_equal(evaluation.labels, [0, 1, 1, 2, 2, 3]))
        for budget in (32, 128):
            self.assertEqual(transformed[budget].shape, (6, config.num_features))
            self.assertTrue(np.all(transformed[budget] >= 0.0))
            self.assertTrue(np.all(transformed[budget] <= 1.0))

    def test_invalid_array_error_length_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            generate_progressive_doa_dataset(
                _small_config(),
                (32, 128),
                array_errors=ArrayElementErrors(
                    gain_db=(0.0, 0.0),
                    phase_deg=(0.0, 0.0),
                ),
            )


if __name__ == "__main__":
    unittest.main()
