"""Unit tests for Day 7 confidence-calibration diagnostics."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import numpy as np

from phase_02_confidence_aware_fast_slow_doa.src.confidence_calibration import (
    binary_auroc,
    evaluate_causal_operating_point,
    expected_calibration_error,
    reliability_rows,
    risk_coverage_rows,
    sample_confidence_diagnostics,
    validate_seed_protocol,
    winner_run_lengths,
)


CONFIG_PATH = (
    Path(__file__).resolve().parents[1]
    / "day_07_confidence_calibration_config.json"
)


class ConfidenceCalibrationTests(unittest.TestCase):
    """Verify diagnostic math, causal accounting, and split isolation."""

    def test_winner_run_lengths_reset_on_change(self) -> None:
        winners = np.asarray([[0, 0, 1, 1, 1], [2, 1, 1, 2, 2]])
        expected = np.asarray([[1, 2, 1, 2, 3], [1, 1, 2, 1, 2]])
        self.assertTrue(np.array_equal(winner_run_lengths(winners), expected))

    def test_sample_diagnostics_align_margin_persistence_and_activity(self) -> None:
        scores = np.asarray(
            [
                [[0.8, 0.2], [0.9, 0.1]],
                [[0.4, 0.6], [0.7, 0.3]],
            ]
        )
        spikes = np.asarray(
            [
                [[1, 0], [1, 1]],
                [[0, 1], [1, 0]],
            ],
            dtype=np.uint8,
        )
        diagnostics = sample_confidence_diagnostics(
            scores,
            spikes,
            np.asarray([0, 1]),
        )

        self.assertTrue(np.array_equal(diagnostics["final_prediction"], [0, 0]))
        self.assertTrue(np.array_equal(diagnostics["fast_correct"], [True, False]))
        self.assertTrue(
            np.array_equal(diagnostics["final_winner_persistence"], [2, 1])
        )
        self.assertTrue(np.array_equal(diagnostics["final_spike_count"], [3, 2]))

    def test_reliability_rows_account_for_edge_values(self) -> None:
        confidence = np.asarray([0.0, 0.1, 0.9, 1.0])
        correct = np.asarray([False, True, True, True])
        rows = reliability_rows(confidence, correct, [0.0, 0.5, 1.0])

        self.assertEqual([int(row["count"]) for row in rows], [2, 2])
        self.assertAlmostEqual(expected_calibration_error(rows), 0.25)

    def test_risk_coverage_is_deterministic_and_complete(self) -> None:
        rows = risk_coverage_rows(
            np.asarray([0.9, 0.8, 0.2, 0.1]),
            np.asarray([True, True, False, False]),
            [0.25, 0.5, 1.0],
        )

        self.assertEqual([int(row["selected_count"]) for row in rows], [1, 2, 4])
        self.assertEqual(float(rows[0]["selective_risk"]), 0.0)
        self.assertEqual(float(rows[-1]["selective_risk"]), 0.5)

    def test_binary_auroc_handles_perfect_inverse_and_ties(self) -> None:
        correct = np.asarray([False, False, True, True])
        self.assertEqual(binary_auroc(np.asarray([0.1, 0.2, 0.8, 0.9]), correct), 1.0)
        self.assertEqual(binary_auroc(np.asarray([0.9, 0.8, 0.2, 0.1]), correct), 0.0)
        self.assertEqual(binary_auroc(np.ones(4), correct), 0.5)

    def test_causal_operating_point_preserves_snapshot_formula(self) -> None:
        scores = np.asarray(
            [
                [[0.9, 0.1], [0.95, 0.05]],
                [[0.1, 0.9], [0.05, 0.95]],
                [[0.51, 0.49], [0.52, 0.48]],
            ]
        )
        spikes = np.ones((3, 2, 2), dtype=np.uint8)
        row = evaluate_causal_operating_point(
            scores,
            spikes,
            np.asarray([0, 0, 0]),
            np.asarray([1, 1, 0]),
            threshold=0.5,
            persistence=1,
            fast_budget=32,
            full_budget=128,
        )

        expected = 32.0 + float(row["fallback_rate"]) * 96.0
        self.assertAlmostEqual(float(row["average_snapshots"]), expected)
        self.assertAlmostEqual(float(row["final_accuracy"]), 2.0 / 3.0)

    def test_registered_seed_protocol_is_disjoint(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        checks = validate_seed_protocol(config)
        self.assertTrue(all(checks.values()))

    def test_seed_overlap_is_rejected(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(config)
        changed["holdout_seed_pairs"][0] = dict(
            changed["calibration_seed_pairs"][0]
        )
        with self.assertRaisesRegex(ValueError, "calibration_holdout_disjoint"):
            validate_seed_protocol(changed)

    def test_day_05_seed_reuse_is_rejected(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(config)
        changed["calibration_seed_pairs"][0] = dict(
            changed["frozen_day_05_seed_pairs"][0]
        )
        with self.assertRaisesRegex(ValueError, "day_05_seeds_not_reused"):
            validate_seed_protocol(changed)


if __name__ == "__main__":
    unittest.main()
