"""Select and freeze one Day 9 gate from byte-verified Day 7 outputs.

Run from the repository root with:

    python -m phase_02_confidence_aware_fast_slow_doa.run_day_08_gate_selection

This runner performs no training, simulation, spike generation, or holdout
evaluation. It reads only the three frozen Day 7 inputs in the manifest.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from phase_02_confidence_aware_fast_slow_doa.src.gate_selection import (
    read_operating_points,
    select_operating_point,
    sha256_file,
    validate_grid,
    validate_source_protocol,
    verify_frozen_inputs,
)


PACKAGE_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = PACKAGE_ROOT / "day_08_gate_selection_config.json"
DEFAULT_RESULT_PATH = PACKAGE_ROOT / "results" / "day_08_selected_operating_point.json"
DEFAULT_REPORT_PATH = PACKAGE_ROOT / "results" / "day_08_gate_selection_report.md"


def _load_config(path: Path) -> dict[str, object]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if int(config["schema_version"]) != 1:
        raise ValueError("Unsupported Day 8 configuration schema.")
    if config["holdout"]["evaluation_allowed"] is not False:
        raise ValueError("Day 8 must prohibit holdout evaluation.")
    rule = config["selection_rule"]
    if float(rule["accuracy_tolerance"]) != 0.01:
        raise ValueError("Day 8 accuracy tolerance must remain 0.01.")
    if rule["objective"] != {
        "field": "snapshot_reduction_fraction",
        "direction": "maximize",
    }:
        raise ValueError("Day 8 objective must maximize snapshot reduction.")
    return config


def _selected_metrics(row: Mapping[str, object]) -> dict[str, object]:
    fields = (
        "num_samples",
        "accepted_count",
        "coverage",
        "selective_accuracy",
        "false_confidence_rate",
        "false_acceptance_probability",
        "fallback_rate",
        "final_accuracy",
        "average_snapshots",
        "average_lif_steps",
        "average_spike_count",
        "always_fast_accuracy",
        "always_continuous_accuracy",
        "accuracy_gap_vs_continuous",
        "snapshot_reduction_fraction",
        "final_accuracy_seed_mean",
        "final_accuracy_seed_std",
        "coverage_seed_mean",
        "coverage_seed_std",
        "average_snapshots_seed_mean",
        "average_snapshots_seed_std",
    )
    return {field: row[field] for field in fields}


def _report(result: Mapping[str, object]) -> str:
    gate = result["selected_gate"]
    metrics = result["calibration_metrics"]
    reference = result["reference_gate_tau_0_8_k_5"]
    delta = result["delta_vs_reference_gate"]
    return f"""# Day 8 Frozen Gate Selection

Day 8 applied the declared rule to the byte-verified Day 7 calibration grid.
No holdout data were generated or evaluated.

## Selected gate

| Metric | Value |
|---|---:|
| Threshold (tau) | {gate['threshold']:.2f} |
| Persistence (K) | {gate['persistence']} |
| Adaptive accuracy | {100.0 * metrics['final_accuracy']:.3f}% |
| Continuous accuracy | {100.0 * metrics['always_continuous_accuracy']:.3f}% |
| Accuracy gap | {100.0 * metrics['accuracy_gap_vs_continuous']:.3f} pp |
| Coverage | {100.0 * metrics['coverage']:.3f}% |
| Selective accuracy | {100.0 * metrics['selective_accuracy']:.3f}% |
| Fallback rate | {100.0 * metrics['fallback_rate']:.3f}% |
| Average snapshots | {metrics['average_snapshots']:.2f} |
| Snapshot reduction | {100.0 * metrics['snapshot_reduction_fraction']:.3f}% |

## Comparison with the previous reference gate

The prior `tau={reference['threshold']:.1f}, K={reference['persistence']}` gate reduced
snapshots by {100.0 * reference['snapshot_reduction_fraction']:.3f}%. The selected
gate improves calibration-set snapshot reduction by
{100.0 * delta['snapshot_reduction_fraction']:.3f} percentage points while using
{100.0 * delta['coverage']:.3f} percentage points more fast-path coverage.

## Frozen boundary

The Day 9 holdout manifest remains `{result['holdout_manifest_sha256']}` with
policy `sealed_until_day_09`. Day 9 may evaluate exactly this one gate once.
"""


def run(
    config_path: Path = DEFAULT_CONFIG_PATH,
    result_path: Path = DEFAULT_RESULT_PATH,
    report_path: Path = DEFAULT_REPORT_PATH,
) -> dict[str, object]:
    config = _load_config(config_path)
    input_paths, input_hashes = verify_frozen_inputs(PACKAGE_ROOT, config["inputs"])
    day_07_config = json.loads(input_paths["day_07_config"].read_text(encoding="utf-8"))
    day_07_summary = json.loads(input_paths["day_07_summary"].read_text(encoding="utf-8"))
    rows = read_operating_points(input_paths["day_07_operating_points"])

    source_checks = validate_source_protocol(config, day_07_config, day_07_summary)
    grid_checks = validate_grid(rows, day_07_config, config["selection_rule"])
    selected, eligible_count = select_operating_point(rows, config["selection_rule"])
    reference = next(
        row for row in rows
        if float(row["threshold"]) == 0.8 and int(row["persistence"]) == 5
    )
    selection_checks = {
        "exactly_one_gate_selected": True,
        "selected_gate_is_source_row": any(selected == row for row in rows),
        "selected_gate_meets_accuracy_tolerance": (
            float(selected["accuracy_gap_vs_continuous"])
            >= -float(config["selection_rule"]["accuracy_tolerance"])
        ),
        "selected_gate_maximizes_snapshot_reduction": (
            float(selected["snapshot_reduction_fraction"])
            == max(
                float(row["snapshot_reduction_fraction"])
                for row in rows
                if float(row["accuracy_gap_vs_continuous"])
                >= -float(config["selection_rule"]["accuracy_tolerance"])
            )
        ),
        "holdout_not_evaluated_on_day_08": True,
    }
    if not all(selection_checks.values()):
        failed = ", ".join(key for key, passed in selection_checks.items() if not passed)
        raise RuntimeError(f"Day 8 selection validation failed: {failed}")

    result = {
        "checkpoint": "day_08_gate_selection_freeze",
        "source_revision": config["source_revision"],
        "config_sha256": sha256_file(config_path),
        "frozen_input_sha256": input_hashes,
        "holdout_manifest_sha256": config["holdout"]["manifest_sha256"],
        "holdout_policy": config["holdout"]["policy"],
        "holdout_evaluated": False,
        "selection_locked_for_day_09": True,
        "selection_rule": config["selection_rule"],
        "grid_size": len(rows),
        "eligible_operating_point_count": eligible_count,
        "selected_gate": {
            "threshold": selected["threshold"],
            "persistence": selected["persistence"],
        },
        "calibration_metrics": _selected_metrics(selected),
        "reference_gate_tau_0_8_k_5": {
            "threshold": reference["threshold"],
            "persistence": reference["persistence"],
            **_selected_metrics(reference),
        },
        "delta_vs_reference_gate": {
            "coverage": float(selected["coverage"]) - float(reference["coverage"]),
            "final_accuracy": (
                float(selected["final_accuracy"]) - float(reference["final_accuracy"])
            ),
            "snapshot_reduction_fraction": (
                float(selected["snapshot_reduction_fraction"])
                - float(reference["snapshot_reduction_fraction"])
            ),
        },
        "validation": {**source_checks, **grid_checks, **selection_checks},
        "all_checks_pass": True,
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_report(result), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()
    result = run(args.config, args.result, args.report)
    gate = result["selected_gate"]
    print(f"Selected frozen Day 9 gate: tau={gate['threshold']}, K={gate['persistence']}")
    print("All Day 8 checks passed; holdout remains sealed.")


if __name__ == "__main__":
    main()
