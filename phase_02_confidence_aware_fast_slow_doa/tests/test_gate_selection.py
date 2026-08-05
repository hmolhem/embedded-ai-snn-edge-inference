"""Regression tests for the leakage-controlled Day 8 gate freeze."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from phase_02_confidence_aware_fast_slow_doa.run_day_08_gate_selection import (
    DEFAULT_CONFIG_PATH,
    run,
)
from phase_02_confidence_aware_fast_slow_doa.src.gate_selection import (
    read_operating_points,
    select_operating_point,
    validate_grid,
    validate_source_protocol,
    verify_frozen_inputs,
)


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class GateSelectionTests(unittest.TestCase):
    """Verify source immutability, deterministic selection, and holdout sealing."""

    def setUp(self) -> None:
        self.config = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
        self.paths, _ = verify_frozen_inputs(PACKAGE_ROOT, self.config["inputs"])
        self.day_07_config = json.loads(
            self.paths["day_07_config"].read_text(encoding="utf-8")
        )
        self.day_07_summary = json.loads(
            self.paths["day_07_summary"].read_text(encoding="utf-8")
        )
        self.rows = read_operating_points(self.paths["day_07_operating_points"])

    def test_frozen_grid_selects_tau_0_2_k_5(self) -> None:
        validate_grid(self.rows, self.day_07_config, self.config["selection_rule"])
        selected, eligible_count = select_operating_point(
            self.rows, self.config["selection_rule"]
        )
        self.assertEqual(eligible_count, 27)
        self.assertEqual(float(selected["threshold"]), 0.2)
        self.assertEqual(int(selected["persistence"]), 5)
        self.assertAlmostEqual(float(selected["snapshot_reduction_fraction"]), 0.1821875)

    def test_source_eligibility_flag_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.rows)
        changed[0]["eligible_within_accuracy_tolerance"] = not bool(
            changed[0]["eligible_within_accuracy_tolerance"]
        )
        with self.assertRaisesRegex(RuntimeError, "source_eligibility_flags_reproduced"):
            validate_grid(changed, self.day_07_config, self.config["selection_rule"])

    def test_duplicate_grid_key_is_rejected(self) -> None:
        changed = copy.deepcopy(self.rows)
        changed[-1]["threshold"] = changed[0]["threshold"]
        changed[-1]["persistence"] = changed[0]["persistence"]
        with self.assertRaisesRegex(RuntimeError, "complete_unique_grid"):
            validate_grid(changed, self.day_07_config, self.config["selection_rule"])

    def test_tie_breaker_prefers_higher_final_accuracy(self) -> None:
        first = copy.deepcopy(self.rows[0])
        second = copy.deepcopy(self.rows[0])
        first["accuracy_gap_vs_continuous"] = -0.005
        second["accuracy_gap_vs_continuous"] = -0.004
        first["snapshot_reduction_fraction"] = 0.1
        second["snapshot_reduction_fraction"] = 0.1
        first["final_accuracy"] = 0.77
        second["final_accuracy"] = 0.78
        selected, count = select_operating_point(
            [first, second], self.config["selection_rule"]
        )
        self.assertEqual(count, 2)
        self.assertEqual(float(selected["final_accuracy"]), 0.78)

    def test_changed_frozen_hash_is_rejected(self) -> None:
        changed = copy.deepcopy(self.config["inputs"])
        changed["day_07_operating_points"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(RuntimeError, "Frozen input hash mismatch"):
            verify_frozen_inputs(PACKAGE_ROOT, changed)

    def test_unsealed_holdout_policy_is_rejected(self) -> None:
        changed = copy.deepcopy(self.config)
        changed["holdout"]["evaluation_allowed"] = True
        with self.assertRaisesRegex(RuntimeError, "holdout_policy_remains_sealed"):
            validate_source_protocol(changed, self.day_07_config, self.day_07_summary)

    def test_runner_writes_one_locked_gate_without_holdout_evaluation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run(
                DEFAULT_CONFIG_PATH,
                root / "selection.json",
                root / "selection.md",
            )
            self.assertEqual(result["selected_gate"], {"threshold": 0.2, "persistence": 5})
            self.assertTrue(result["selection_locked_for_day_09"])
            self.assertFalse(result["holdout_evaluated"])
            self.assertTrue(result["all_checks_pass"])
            self.assertTrue((root / "selection.md").is_file())


if __name__ == "__main__":
    unittest.main()
