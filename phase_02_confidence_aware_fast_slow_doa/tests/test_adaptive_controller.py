"""Tests for adaptive fast-slow decision composition."""

from __future__ import annotations

import unittest

import numpy as np

from phase_02_confidence_aware_fast_slow_doa.src.adaptive_controller import (
    adaptive_metrics,
    compose_adaptive_decisions,
)
from phase_02_confidence_aware_fast_slow_doa.src.confidence_gate import (
    causal_margin_persistence_gate,
)


class AdaptiveControllerTests(unittest.TestCase):
    """Verify accepted/fallback routing and realized cost accounting."""

    def test_composes_fast_and_fallback_predictions(self) -> None:
        history = np.asarray(
            [
                [[0.9, 0.1], [0.95, 0.05]],
                [[0.51, 0.49], [0.52, 0.48]],
            ]
        )
        gate = causal_margin_persistence_gate(history, threshold=0.5, persistence=1)
        fallback = np.asarray([1, 1])
        spikes = np.asarray(
            [
                [[1, 0], [1, 1]],
                [[0, 1], [1, 1]],
            ],
            dtype=np.uint8,
        )

        result = compose_adaptive_decisions(gate, fallback, spikes)

        self.assertTrue(np.array_equal(result.final_predictions, [0, 1]))
        self.assertTrue(np.array_equal(result.used_fallback, [False, True]))
        self.assertTrue(np.array_equal(result.snapshots_used, [32, 128]))
        self.assertTrue(np.array_equal(result.lif_steps_used, [1, 2]))
        self.assertTrue(np.array_equal(result.spike_counts_used, [1, 3]))

    def test_metrics_use_correct_denominators(self) -> None:
        history = np.asarray(
            [
                [[0.9, 0.1]],
                [[0.1, 0.9]],
                [[0.51, 0.49]],
            ]
        )
        gate = causal_margin_persistence_gate(history, threshold=0.5, persistence=1)
        fallback = np.asarray([1, 1, 0])
        spikes = np.ones((3, 1, 2), dtype=np.uint8)
        decisions = compose_adaptive_decisions(gate, fallback, spikes)
        metrics = adaptive_metrics(np.asarray([0, 0, 0]), gate, decisions)

        self.assertAlmostEqual(float(metrics["coverage"]), 2.0 / 3.0)
        self.assertAlmostEqual(float(metrics["selective_accuracy"]), 0.5)
        self.assertAlmostEqual(float(metrics["false_confidence_rate"]), 0.5)
        self.assertAlmostEqual(float(metrics["fallback_rate"]), 1.0 / 3.0)
        self.assertAlmostEqual(float(metrics["final_accuracy"]), 2.0 / 3.0)
        self.assertAlmostEqual(float(metrics["average_snapshots"]), 64.0)

    def test_zero_time_step_spike_sequence_is_rejected(self) -> None:
        history = np.zeros((1, 1, 2), dtype=float)
        gate = causal_margin_persistence_gate(
            history,
            threshold=0.5,
            persistence=1,
        )

        with self.assertRaisesRegex(ValueError, "at least one time step"):
            compose_adaptive_decisions(
                gate,
                fallback_predictions=np.asarray([0]),
                shared_spikes=np.empty((1, 0, 2), dtype=np.uint8),
            )

    def test_empty_metrics_input_is_rejected(self) -> None:
        history = np.empty((0, 1, 2), dtype=float)
        gate = causal_margin_persistence_gate(
            history,
            threshold=0.5,
            persistence=1,
        )
        decisions = compose_adaptive_decisions(
            gate,
            fallback_predictions=np.empty(0, dtype=int),
            shared_spikes=np.empty((0, 1, 2), dtype=np.uint8),
        )

        with self.assertRaisesRegex(ValueError, "at least one sample"):
            adaptive_metrics(np.empty(0, dtype=int), gate, decisions)


if __name__ == "__main__":
    unittest.main()

