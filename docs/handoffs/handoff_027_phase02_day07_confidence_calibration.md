# Handoff 027 — Phase 2 Day 7 Confidence Calibration

## Purpose

Measure whether the existing confidence signals separate correct and incorrect
fast-path DOA decisions on independent development data, while preventing
Day 5 validation leakage and preserving a sealed final holdout.

## Repository Workflow

```text
Base branch: main at 3f515bc (merged PR #29)
Feature branch: feature/day-07-confidence-calibration
Handoff: 027
Pull request: pending at handoff creation
Merge and remote-branch deletion: reserved for Hossein
```

No repository file is written directly to `main`.

## Leakage-Controlled Seed Protocol

The configuration registers three mutually disjoint groups:

```text
Frozen Day 5 dataset/spike seeds: 43/743 through 47/747
Day 7 calibration seeds:         101/1101 through 105/1105
Sealed Day 9 holdout seeds:      201/1201 through 205/1205
```

Day 7 evaluates only the five calibration pairs. The holdout policy is
`sealed_until_day_09`; no holdout dataset, feature, spike tensor, prediction,
or metric is generated. The canonical holdout-manifest SHA-256 is:

```text
e2549c689da20987555303f6c6a7996c2299497de3e65cc2067142d43f193420
```

The Day 7 configuration SHA-256 is:

```text
2fc232b490f88d09fa0e3bf9fb6f70fa00e12396735b5c08abe405af27aabdc2
```

## Scope Added

Day 7 adds:

1. validated calibration/holdout/Day 5 seed isolation;
2. per-sample normalized margin, winner persistence, stable winner time,
   spike count, firing rate, SNR, and boundary-distance diagnostics;
3. a tie-aware AUROC measuring whether margin ranks fast-decision correctness;
4. an equal-width reliability analysis and expected calibration error;
5. a descriptive risk-coverage curve based on final margin;
6. the complete 14-threshold by 5-persistence causal gate grid;
7. pooled and across-seed accuracy, coverage, cost, and variability metrics;
8. four report-ready figures in PNG and PDF; and
9. focused regression tests for diagnostic math and seed leakage.

The runner exports the complete grid but contains no selection operation.

## Validation Results

```text
unit tests: 31/31 passed
five unique calibration pairs: passed
five unique holdout pairs: passed
calibration/holdout separation: passed
Day 5 seed non-reuse: passed
only registered calibration seeds evaluated: passed
holdout not evaluated: passed
complete 70-point causal grid: passed
coverage monotonic with threshold: passed
snapshot accounting formula: passed
reliability sample accounting: passed
no Day 7 operating-point selection: passed
all Day 7 runner checks: passed
repeat execution reproduced all 13 result/figure SHA-256 hashes: passed
```

## Main Calibration Findings

Across 4,800 independent calibration samples:

| Metric | Value |
|---|---:|
| Always-fast accuracy | 0.6750 |
| Always-continuous accuracy | 0.7808 |
| Final-margin AUROC for fast correctness | 0.7614 |
| Raw-margin expected calibration error | 0.5856 |
| Mean margin, correct fast decisions | 0.1192 |
| Mean margin, incorrect fast decisions | 0.0374 |
| Mean correct-minus-incorrect margin | 0.0818 |

The margin therefore contains useful ranking information, but its numeric value
must not be interpreted as a calibrated probability of correctness. This is
the central Day 7 result.

The frozen reference gate (`tau=0.8`, `K=5`) produced:

```text
adaptive accuracy: 0.7810
continuous accuracy: 0.7808
coverage: 0.0494
selective accuracy: 0.9451
false-confidence rate: 0.0549
fallback rate: 0.9506
average snapshots: 123.26
snapshot reduction: 3.70 percent
```

This independently reproduces the Day 5 conclusion: the reference gate is
safe and selective but obtains its accuracy primarily through fallback.

Twenty-seven of the 70 analyzed points satisfied the descriptive criterion of
pooled adaptive accuracy no more than one percentage point below the
continuous baseline. The most aggressive eligible grid point was
`tau=0.2, K=5`, with 24.29 percent coverage, 18.22 percent snapshot reduction,
and a 0.958-percentage-point accuracy deficit. This is an unselected
calibration observation only; it is not yet the Day 8 operating point and has
not been tested on the holdout.

## Generated Outputs

```text
day_07_confidence_calibration_config.json
src/confidence_calibration.py
tests/test_confidence_calibration.py
results/day_07_calibration_samples.csv
results/day_07_operating_points.csv
results/day_07_confidence_reliability.csv
results/day_07_risk_coverage.csv
results/day_07_confidence_calibration_summary.json
figures/day_07_confidence_reliability.{png,pdf}
figures/day_07_risk_coverage.{png,pdf}
figures/day_07_coverage_snapshot_reduction.{png,pdf}
figures/day_07_accuracy_gap.{png,pdf}
```

## Reproduction Commands

Run from the repository root:

```powershell
python -m unittest discover -s phase_02_confidence_aware_fast_slow_doa/tests -v
python -m phase_02_confidence_aware_fast_slow_doa.run_day_07_confidence_calibration
```

## Scope Boundary and Next Step

Day 7 does not fit a probability calibrator, select a gate, change the Day 5
record, or evaluate holdout seeds. Day 8 must first freeze a robust selection
rule using only the Day 7 tables. Day 9 may then evaluate exactly one selected
operating point once on the sealed holdout pairs.
