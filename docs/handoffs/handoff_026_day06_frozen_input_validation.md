# Handoff 026 — Day 6 Frozen-Input Validation Hardening

## Purpose

Close the two actionable review threads left on merged PR #28 without changing
the frozen Day 5 data, the pre-registered gate, the Day 6 figures, or any
scientific result.

## Repository Workflow

```text
Base branch: main
Fix branch: fix/day-06-frozen-input-validation
Handoff: 026
Pull request: pending at handoff creation
Merge and remote-branch deletion: reserved for Hossein
```

No repository file is written directly to `main`.

## Review Findings Addressed

### 1. Frozen hashes were recorded but not enforced

The Day 6 runner previously calculated and reported SHA-256 digests for the
four Day 5 inputs, but it did not compare them with an immutable expected set.
A modified input could therefore pass the remaining self-consistency checks.

The runner now contains the reviewed SHA-256 manifest for:

```text
day_05_per_seed_metrics.csv
day_05_aggregate_metrics.csv
day_05_stress_test_summary.json
day_05_stress_config.json
```

Execution fails unless the observed file-name/digest mapping exactly matches
that frozen manifest.

### 2. Condition validation checked counts, not identities

The previous validator required the expected number of rows and groups, but a
same-size replacement condition could still satisfy those shape checks.

The runner now derives the complete expected
`(experiment, condition, method)` set from `day_05_stress_config.json` and
requires exact equality for both aggregate and per-seed data. This includes:

- all eight configured SNR labels;
- all ten signed sector-boundary offsets;
- the `nominal`, `mild`, `moderate`, and `severe` mismatch levels; and
- `always_fast`, `always_continuous`, and `adaptive` for every condition.

Duplicate aggregate keys are also rejected.

## Regression Tests

Two focused negative tests were added:

1. a changed input digest is rejected even when the CSV/JSON contents remain
   otherwise self-consistent; and
2. replacing `-15_db` with the same-size unconfigured label `-14_db` in both
   CSV views is rejected even though row counts and recomputed statistics still
   agree.

## Validation Results

```text
unit tests: 22/22 passed
Day 6 runner: all checks passed
frozen input hashes match reviewed manifest: passed
aggregate group keys match config: passed
per-seed group keys match config: passed
Python compilation check: passed
all eight PNG/PDF figure SHA-256 hashes unchanged: passed
generated Markdown table SHA-256 unchanged: passed
Day 6 summary updated only to record the three new validation checks: passed
```

The numerical findings, gate parameters (`tau=0.8`, `K=5`), snapshot budgets
(`M=32/128`), figures, and report tables are unchanged.

## Reproduction Commands

Run from the repository root:

```powershell
python -m unittest discover -s phase_02_confidence_aware_fast_slow_doa/tests -v
python -m phase_02_confidence_aware_fast_slow_doa.run_day_06_results_visualization
```

## Scope Boundary

This fix strengthens provenance and structural validation only. It does not
retrain a model, sweep a threshold, recalibrate confidence, reselect an
operating point, or reinterpret the frozen Day 5 results.
