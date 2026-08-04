# Handoff 025 — Phase 2 Day 6 Frozen-Result Visualization

## Purpose

Convert the pre-registered Day 5 stress-test outputs into report-ready figures,
tables, and a bounded engineering interpretation without using validation data
to tune or reselect the confidence gate.

## Repository Workflow

```text
Base branch: main
Feature branch: feature/day-06-results-visualization
Handoff: 025
Pull request: pending at handoff creation
Merge and remote-branch deletion: reserved for Hossein
```

No repository file was written directly to `main`.

## Scope Added

Day 6 adds a one-command visualization runner that:

1. reads the frozen Day 5 per-seed and aggregate result files;
2. verifies the Day 5 configuration and pre-registered operating point agree;
3. recomputes every available aggregate mean and sample standard deviation;
4. records SHA-256 hashes of all frozen inputs;
5. creates PNG and PDF versions of four report-ready figures;
6. writes a Markdown table package and JSON validation summary; and
7. makes no training, threshold sweep, persistence sweep, or operating-point
   selection.

## Review-Follow-Up Fixes

Two valid edge cases reported during review of PR #27 are also closed:

- `compose_adaptive_decisions` now explicitly rejects a spike tensor with zero
  time steps before indexing cumulative spike counts.
- `adaptive_metrics` now explicitly rejects an empty sample set before computing
  ratios.

Each fix has a focused regression test.

## Generated Figures

```text
figures/day_06_nominal_accuracy_and_cost.{png,pdf}
figures/day_06_snr_stress.{png,pdf}
figures/day_06_boundary_stress.{png,pdf}
figures/day_06_array_mismatch_stress.{png,pdf}
```

All plotted points are five-seed means. Error bars and shaded bands show one
sample standard deviation across the five seed pairs.

## Validation Results

```text
unit tests: 20/20 passed
Day 5 validation summary: passed
expected aggregate row count: passed
expected per-seed group count: passed
five rows per aggregate group: passed
all three methods present: passed
aggregate statistics reproduced from per-seed data: passed
operating point matches frozen Day 5 configuration: passed
descriptive-analysis-only policy: passed
repeat execution produced identical SHA-256 hashes for all Day 6 artifacts: passed
```

## Main Findings

### Nominal five-seed result

| Method | Accuracy, mean ± std | Average snapshots |
|---|---:|---:|
| Always fast | 0.6681 ± 0.0554 | 32.00 |
| Always continuous | 0.7846 ± 0.0306 | 128.00 |
| Adaptive | 0.7850 ± 0.0304 | 122.86 ± 0.50 |

For the adaptive method:

```text
coverage: 0.0535 ± 0.0052
selective accuracy: 0.9623 ± 0.0239
fallback rate: 0.9465 ± 0.0052
snapshot reduction relative to M=128: 4.02 percent
```

### Failure-mode interpretation

- At `-15 dB`, the adaptive gate accepts no samples; adaptive and continuous
  accuracy are both `0.4167` and all cases use the full snapshot budget.
- At signed boundary offsets of `±0.5 degrees`, adaptive accuracy is roughly
  `0.44–0.49` and coverage is only `0.8–1.5 percent`.
- At signed boundary offsets of `±10 degrees`, adaptive accuracy recovers to
  roughly `0.88–0.90`, but coverage remains below `5 percent`.
- Severe fixed-device mismatch lowers adaptive accuracy by only about `1.02`
  percentage points relative to nominal, which is much smaller than the low-SNR
  and near-boundary effects.

The fixed gate is selective and preserves the continuous-baseline accuracy, but
it does so primarily by routing `94.65 percent` of nominal samples to the
fallback. Therefore Day 5 does not support a generalized 30-percent efficiency
claim.

## Scientific Lineage

The result follows the course progression: Week 4 motivates an event-driven
fast path, Week 7 motivates context-aware gating and system-level cost
accounting, and Week 8 motivates a fast/slow architecture with a reliable
fallback. Day 6 shows that the architecture is valid as a safety mechanism, but
the current confidence signal is not calibrated well enough to deliver broad
efficiency gains.

## Reproduction Commands

Run from the repository root:

```powershell
python -m unittest discover -s phase_02_confidence_aware_fast_slow_doa/tests -v
python -m phase_02_confidence_aware_fast_slow_doa.run_day_06_results_visualization
```

## Next Step

A later gate redesign must use a distinct calibration/development split and
fresh holdout seed pairs. The frozen Day 5 seeds must not be reused to select a
new threshold or confidence transformation.
