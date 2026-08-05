# Handoff 028 — Phase 2 Day 8 Frozen Gate Selection

## Purpose

Apply the agreed accuracy-constrained cost rule to the frozen Day 7
calibration grid, select exactly one causal gate, and lock that gate for a
single Day 9 evaluation without opening the sealed holdout.

## Repository Workflow

```text
Base branch: main at ab5d5ea (merged PR #30)
Feature branch: feature/day-08-gate-selection
Handoff: 028
Pull request: pending at handoff creation
Merge and remote-branch deletion: reserved for Hossein
```

No repository file is written directly to `main`.

## Frozen Inputs

Day 8 reads only three Day 7 files:

| Input | SHA-256 |
|---|---|
| `day_07_confidence_calibration_config.json` | `2fc232b490f88d09fa0e3bf9fb6f70fa00e12396735b5c08abe405af27aabdc2` |
| `results/day_07_operating_points.csv` | `d38ff0fe896b02632bde04d693bba75e306051147c7c713e72a2520666e25b9a` |
| `results/day_07_confidence_calibration_summary.json` | `8a23c900664f193ba2f7c5431ebaee0086822ab0992fbca13936a60237f5fed5` |

The Day 8 selection configuration SHA-256 is:

```text
6574c6792de4a481aa3dfdbe8b3c3d12eb7bf9c5b1e8dd0db3fcfbc56ffedea6
```

The sealed Day 9 holdout-manifest SHA-256 remains:

```text
e2549c689da20987555303f6c6a7996c2299497de3e65cc2067142d43f193420
```

No Day 9 dataset, feature, spike tensor, prediction, or metric was generated.

## Declared Selection Rule

1. Reproduce the complete unique 70-point `(tau, K)` grid and all Day 7
   eligibility flags.
2. Keep points whose pooled adaptive accuracy is no more than one percentage
   point below the pooled always-continuous reference.
3. Maximize `snapshot_reduction_fraction`.
4. Break an exact tie by, in order:
   - higher final accuracy;
   - lower false-confidence rate;
   - higher persistence;
   - higher threshold.
5. Freeze exactly one source row for Day 9.

This is a selection step only. It does not fit a probability calibrator,
recompute Day 7, or inspect holdout outcomes.

## Frozen Selection

The rule selected:

```text
threshold (tau): 0.2
persistence (K): 5
```

Calibration-set metrics:

| Metric | Value |
|---|---:|
| Samples | 4,800 |
| Accepted fast decisions | 1,166 |
| Adaptive accuracy | 0.77125 |
| Continuous accuracy | 0.780833 |
| Accuracy gap | -0.009583 (-0.958 percentage point) |
| Coverage | 0.242917 |
| Selective accuracy | 0.864494 |
| False-confidence rate | 0.135506 |
| Fallback rate | 0.757083 |
| Average snapshots | 104.68 |
| Snapshot reduction | 0.1821875 (18.219 percent) |

Relative to the previous `tau=0.8`, `K=5` reference, calibration-set
snapshot reduction increased by 14.516 percentage points and fast-path
coverage increased by 19.354 percentage points. Adaptive accuracy decreased
by 0.979 percentage point relative to that reference and remains within the
declared one-point deficit from the continuous baseline.

These are calibration results, not holdout claims.

## Validation Results

```text
unit tests: 38/38 passed
three frozen Day 7 input hashes: passed
Day 7 configuration/summary identity: passed
holdout manifest and sealed policy: passed
Day 7 holdout not evaluated: passed
complete unique 70-point grid: passed
4,800-sample accounting at every point: passed
source eligibility flags reproduced: passed
27 eligible points reproduced: passed
exactly one source row selected: passed
selected point maximizes eligible snapshot reduction: passed
Day 8 holdout not evaluated: passed
repeat execution reproduced both result hashes: passed
all Day 8 checks: passed
```

Generated artifact SHA-256 values:

```text
results/day_08_selected_operating_point.json
1f9fca3a3d91df309b8b280f89bb625dfd4fa49711ba444270981daf10a6bb1a

results/day_08_gate_selection_report.md
e9f5bc17ec6637678e204eb73819b1d4ec979eb088e0e8af4ed8dd2582872a5c
```

## Added or Updated Files

```text
phase_02_confidence_aware_fast_slow_doa/day_08_gate_selection_config.json
phase_02_confidence_aware_fast_slow_doa/src/gate_selection.py
phase_02_confidence_aware_fast_slow_doa/run_day_08_gate_selection.py
phase_02_confidence_aware_fast_slow_doa/tests/test_gate_selection.py
phase_02_confidence_aware_fast_slow_doa/results/day_08_selected_operating_point.json
phase_02_confidence_aware_fast_slow_doa/results/day_08_gate_selection_report.md
phase_02_confidence_aware_fast_slow_doa/README.md
docs/project_log.md
docs/handoffs/index.md
docs/handoffs/handoff_028_phase02_day08_gate_selection.md
```

## Reproduction Commands

Run from the repository root:

```powershell
python -m unittest discover -s phase_02_confidence_aware_fast_slow_doa/tests -v
python -m phase_02_confidence_aware_fast_slow_doa.run_day_08_gate_selection
```

## Next Step and Irreversibility Rule

Day 9 may evaluate exactly `tau=0.2`, `K=5` once on the five sealed
holdout seed pairs `201/1201` through `205/1205`. It must verify the Day 8
config, selected-result artifact, and holdout-manifest hashes before generating
any holdout data.

No threshold change, persistence change, recalibration, grid search, or second
holdout attempt is permitted after outcomes are observed. Day 10 will report
the holdout result whether positive, neutral, or negative.
