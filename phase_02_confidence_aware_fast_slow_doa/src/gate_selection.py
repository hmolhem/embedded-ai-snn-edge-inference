"""Deterministic, leakage-controlled selection from frozen Day 7 outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Mapping, Sequence


FLOAT_FIELDS = (
    "threshold",
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
INT_FIELDS = ("persistence", "num_samples", "accepted_count")
BOOL_FIELD = "eligible_within_accuracy_tolerance"
REQUIRED_FIELDS = frozenset((*FLOAT_FIELDS, *INT_FIELDS, BOOL_FIELD))


def sha256_file(path: Path) -> str:
    """Return the byte-exact SHA-256 of one frozen input."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    """Hash a JSON-compatible value with stable key and separator rules."""

    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"Expected literal True or False, received {value!r}.")


def read_operating_points(path: Path) -> list[dict[str, float | int | bool]]:
    """Read the frozen Day 7 grid with strict schema and numeric checks."""

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = frozenset(reader.fieldnames or ())
        missing = sorted(REQUIRED_FIELDS - fields)
        if missing:
            raise ValueError(f"Operating-point table is missing columns: {missing}")
        raw_rows = list(reader)
    if not raw_rows:
        raise ValueError("Operating-point table must not be empty.")

    rows: list[dict[str, float | int | bool]] = []
    for row_index, raw in enumerate(raw_rows, start=2):
        parsed: dict[str, float | int | bool] = {}
        for field in FLOAT_FIELDS:
            parsed[field] = float(raw[field])
            if not math.isfinite(float(parsed[field])):
                raise ValueError(f"Non-finite {field} on CSV row {row_index}.")
        for field in INT_FIELDS:
            parsed[field] = int(raw[field])
        parsed[BOOL_FIELD] = _parse_bool(raw[BOOL_FIELD])
        rows.append(parsed)
    return rows


def verify_frozen_inputs(
    package_root: Path,
    manifest: Mapping[str, Mapping[str, str]],
) -> tuple[dict[str, Path], dict[str, str]]:
    """Resolve manifest paths inside the package and reject any hash drift."""

    root = package_root.resolve()
    paths: dict[str, Path] = {}
    hashes: dict[str, str] = {}
    for name, item in manifest.items():
        path = (root / str(item["path"])).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Frozen input {name} escapes the package root.")
        actual = sha256_file(path)
        expected = str(item["sha256"])
        if actual != expected:
            raise RuntimeError(
                f"Frozen input hash mismatch for {name}: {actual} != {expected}"
            )
        paths[name] = path
        hashes[name] = actual
    return paths, hashes


def validate_source_protocol(
    selection_config: Mapping[str, object],
    day_07_config: Mapping[str, object],
    day_07_summary: Mapping[str, object],
) -> dict[str, bool]:
    """Prove that selection uses Day 7 only and leaves Day 9 sealed."""

    holdout = selection_config["holdout"]
    day_07_input_hash = selection_config["inputs"]["day_07_config"]["sha256"]
    holdout_manifest = canonical_sha256(day_07_config["holdout_seed_pairs"])
    checks = {
        "day_07_config_hash_matches_summary": (
            str(day_07_summary["config_sha256"]) == str(day_07_input_hash)
        ),
        "holdout_manifest_matches_day_07": (
            holdout_manifest == str(holdout["manifest_sha256"])
            and holdout_manifest
            == str(day_07_summary["holdout_seed_manifest_sha256"])
        ),
        "holdout_policy_remains_sealed": (
            str(day_07_config["holdout_policy"]) == "sealed_until_day_09"
            and str(day_07_summary["holdout_policy"]) == "sealed_until_day_09"
            and str(holdout["policy"]) == "sealed_until_day_09"
            and holdout["evaluation_allowed"] is False
        ),
        "day_07_holdout_not_evaluated": day_07_summary["holdout_evaluated"] is False,
        "day_07_selection_not_performed": day_07_summary["selection_performed"] is False,
        "day_07_checks_passed": day_07_summary["all_checks_pass"] is True,
        "day_07_selection_reserved_for_day_08": (
            day_07_config["analysis"]["selection_policy"]
            == "reserved_for_day_08_after_review_of_day_07_outputs"
        ),
    }
    if not all(checks.values()):
        failed = ", ".join(key for key, passed in checks.items() if not passed)
        raise RuntimeError(f"Invalid Day 7 source protocol: {failed}")
    return checks


def validate_grid(
    rows: Sequence[Mapping[str, float | int | bool]],
    day_07_config: Mapping[str, object],
    rule: Mapping[str, object],
) -> dict[str, bool]:
    """Verify complete grid identity, sample accounting, and eligibility flags."""

    expected_keys = {
        (float(threshold), int(persistence))
        for persistence in day_07_config["analysis"]["persistence_values"]
        for threshold in day_07_config["analysis"]["thresholds"]
    }
    actual_keys = {
        (float(row["threshold"]), int(row["persistence"])) for row in rows
    }
    tolerance = float(rule["accuracy_tolerance"])
    recomputed = [
        float(row["accuracy_gap_vs_continuous"]) >= -tolerance - 1e-15
        for row in rows
    ]
    source_flags = [bool(row[BOOL_FIELD]) for row in rows]
    eligible_count = sum(recomputed)
    continuous = [float(row["always_continuous_accuracy"]) for row in rows]
    checks = {
        "complete_unique_grid": (
            len(rows) == int(rule["expected_grid_size"])
            and len(actual_keys) == len(rows)
            and actual_keys == expected_keys
        ),
        "calibration_sample_count_fixed": all(
            int(row["num_samples"])
            == int(rule["expected_num_calibration_samples"])
            for row in rows
        ),
        "continuous_reference_is_constant": max(continuous) - min(continuous) <= 1e-15,
        "accuracy_tolerance_matches_day_07": (
            tolerance == float(day_07_config["analysis"]["final_accuracy_tolerance"])
        ),
        "source_eligibility_flags_reproduced": (
            source_flags == recomputed
            if bool(rule["require_source_eligibility_flag"])
            else True
        ),
        "eligible_count_matches_manifest": (
            eligible_count == int(rule["expected_eligible_count"])
        ),
    }
    if not all(checks.values()):
        failed = ", ".join(key for key, passed in checks.items() if not passed)
        raise RuntimeError(f"Invalid Day 7 operating-point grid: {failed}")
    return checks


def _sort_component(row: Mapping[str, object], item: Mapping[str, object]) -> float:
    value = float(row[str(item["field"])])
    direction = str(item["direction"])
    if direction == "maximize":
        return -value
    if direction == "minimize":
        return value
    raise ValueError(f"Unsupported sort direction {direction!r}.")


def select_operating_point(
    rows: Sequence[Mapping[str, float | int | bool]],
    rule: Mapping[str, object],
) -> tuple[dict[str, float | int | bool], int]:
    """Apply the declared accuracy constraint and deterministic ordering."""

    tolerance = float(rule["accuracy_tolerance"])
    eligible = [
        dict(row)
        for row in rows
        if float(row["accuracy_gap_vs_continuous"]) >= -tolerance - 1e-15
    ]
    if not eligible:
        raise RuntimeError("No operating point satisfies the accuracy constraint.")
    ordering = [rule["objective"], *rule["tie_breakers"]]
    eligible.sort(
        key=lambda row: tuple(_sort_component(row, item) for item in ordering)
    )
    return eligible[0], len(eligible)
