"""Unit tests for the causal normalized-margin confidence gate."""

from __future__ import annotations

import unittest

import numpy as np

from phase_02_confidence_aware_fast_slow_doa.src.confidence_gate import (
    causal_margin_persistence_gate,
    normalized_top_two_margin,
)


class ConfidenceGateTests(unittest.TestCase):
    """Check causality, persistence, reset behavior, and abstention."""

    def test_accepts_at_first_causal_persistent_step(self) -> None:
        history = np.asarray(
            [[[0.55, 0.45], [0.80, 0.20], [0.85, 0.15], [0.90, 0.10]]],
            dtype=float,
        )
        gate = causal_margin_persistence_gate(history, threshold=0.50, persistence=2)

        self.assertTrue(gate.accepted[0])
        self.assertEqual(gate.predicted_labels[0], 0)
        self.assertEqual(gate.decision_steps[0], 3)

    def test_winner_change_resets_persistence(self) -> None:
        history = np.asarray(
            [[[0.90, 0.10], [0.10, 0.90], [0.05, 0.95]]],
            dtype=float,
        )
        gate = causal_margin_persistence_gate(history, threshold=0.50, persistence=2)

        self.assertTrue(gate.accepted[0])
        self.assertEqual(gate.predicted_labels[0], 1)
        self.assertEqual(gate.decision_steps[0], 3)

    def test_abstains_when_margin_never_passes(self) -> None:
        history = np.asarray(
            [[[0.51, 0.49], [0.52, 0.48], [0.53, 0.47]]],
            dtype=float,
        )
        gate = causal_margin_persistence_gate(history, threshold=0.20, persistence=1)

        self.assertFalse(gate.accepted[0])
        self.assertEqual(gate.predicted_labels[0], -1)
        self.assertEqual(gate.decision_steps[0], -1)
        self.assertTrue(np.isnan(gate.confidence_at_decision[0]))

    def test_margin_shape_and_bounds(self) -> None:
        history = np.asarray(
            [
                [[1.0, -1.0, 0.0], [3.0, 2.0, 1.0]],
                [[-1.0, -2.0, -3.0], [0.0, 0.0, 0.0]],
            ]
        )
        margin = normalized_top_two_margin(history)

        self.assertEqual(margin.shape, (2, 2))
        self.assertTrue(np.all(margin >= 0.0))
        self.assertTrue(np.all(margin <= 1.0))

    def test_invalid_gate_configuration_is_rejected(self) -> None:
        history = np.zeros((1, 2, 2), dtype=float)
        for threshold, persistence in ((-0.1, 1), (1.1, 1), (0.2, 0)):
            with self.subTest(threshold=threshold, persistence=persistence):
                with self.assertRaises((TypeError, ValueError)):
                    causal_margin_persistence_gate(history, threshold, persistence)


if __name__ == "__main__":
    unittest.main()

