"""Tests for frozen-input Day 6 result visualization."""

from __future__ import annotations

import copy
import json
import unittest

from phase_02_confidence_aware_fast_slow_doa.run_day_06_results_visualization import (
    AGGREGATE_PATH,
    DAY_05_CONFIG_PATH,
    DAY_05_SUMMARY_PATH,
    PER_SEED_PATH,
    _parse_condition,
    _read_csv,
    _validate_inputs,
)


class Day06VisualizationTests(unittest.TestCase):
    """Ensure Day 6 remains descriptive and tied to frozen Day 5 data."""

    def setUp(self) -> None:
        self.per_seed = _read_csv(PER_SEED_PATH)
        self.aggregate = _read_csv(AGGREGATE_PATH)
        self.config = json.loads(DAY_05_CONFIG_PATH.read_text(encoding="utf-8"))
        self.summary = json.loads(DAY_05_SUMMARY_PATH.read_text(encoding="utf-8"))

    def test_frozen_day_05_inputs_validate(self) -> None:
        checks = _validate_inputs(
            self.per_seed,
            self.aggregate,
            self.config,
            self.summary,
        )
        self.assertTrue(all(checks.values()))

    def test_changed_gate_is_rejected(self) -> None:
        changed = copy.deepcopy(self.config)
        changed["gate"]["threshold"] = 0.7
        with self.assertRaisesRegex(RuntimeError, "operating_point"):
            _validate_inputs(
                self.per_seed,
                self.aggregate,
                changed,
                self.summary,
            )

    def test_condition_ordering_is_numeric_and_explicit(self) -> None:
        self.assertEqual(_parse_condition("-0.5_deg"), -0.5)
        self.assertEqual(_parse_condition("20_db"), 20.0)
        self.assertLess(_parse_condition("mild"), _parse_condition("severe"))


if __name__ == "__main__":
    unittest.main()
