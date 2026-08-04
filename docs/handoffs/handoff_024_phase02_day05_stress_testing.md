# Handoff 024 — Phase 2 Day 5 Multi-Seed Stress Testing

## Purpose

Record the first executable Phase 2 confidence-aware fast–slow DOA pipeline,
its fixed Day 4 candidate operating point, and the pre-registered Day 5
multi-seed stress evaluation.

## Repository Workflow

```text
Base branch: main
Feature branch: feature/day-05-stress-testing
Handoff: 024
Pull request: pending creation after validation
Merge and remote-branch deletion: reserved for Hossein
```

No repository file was written directly to `main`.

## Scope Added

The branch adds `phase_02_confidence_aware_fast_slow_doa/` with:

1. aligned progressive snapshot features at `M=32`, `64`, and `128`;
2. a causal normalized-margin plus winner-persistence confidence gate;
3. a mandatory `M=128` nearest-centroid fallback;
4. adaptive cost accounting for snapshots, LIF steps, and spikes;
5. deterministic fixed-device gain/phase mismatch modeling;
6. explicit boundary-condition generation;
7. standard-library unit tests and reproducible result exports; and
8. a JSON-controlled five-seed Day 5 stress runner.

The Phase 1 source code remains unchanged.

## Fixed Day 5 Operating Point

The Day 4 development run selected the following candidate before Day 5:

```text
fast snapshot budget: M=32
fallback snapshot budget: M=128
maximum spike steps: T=40
LIF leak: 0.99
confidence threshold: tau=0.8
winner persistence: K=5
```

Day 5 did not sweep or reselect any of these values.

## Stress Protocol

### Seed pairs

```text
dataset/spike: 43/743
dataset/spike: 44/744
dataset/spike: 45/745
dataset/spike: 46/746
dataset/spike: 47/747
```

### SNR

The nominal paired test split was evaluated at:

```text
-15, -10, -5, 0, 5, 10, 15, and 20 dB
```

### Boundary stress

Signed offsets `±0.5`, `±1`, `±2`, `±5`, and `±10` degrees were evaluated
around each internal boundary (`-30`, `0`, and `30` degrees) over the complete
SNR grid.

### Array mismatch

One zero-mean fixed element-error direction was generated per dataset seed and
scaled to four nested RMS levels:

| Level | Gain RMS | Phase RMS |
|---|---:|---:|
| Nominal | 0 dB | 0 degrees |
| Mild | 0.25 dB | 2 degrees |
| Moderate | 0.5 dB | 5 degrees |
| Severe | 1.0 dB | 10 degrees |

Models and normalization statistics were trained only on nominal data. No
stress-condition recalibration or retraining was permitted.

## Validation Results

```text
unit tests: 15/15 passed
Phase 1 M=128 reproduction error: 0.0
five unique seed pairs completed: passed
all expected aggregate groups present: passed
every aggregate group contains five seeds: passed
paired mismatch metadata identity: passed
configured mismatch RMS values: passed
adaptive snapshot accounting formula: passed
operating point fixed without reselection: passed
```

## Main Five-Seed Findings

### Nominal uniform-angle test

| Method | Accuracy, mean ± std | Average snapshots | Average LIF steps |
|---|---:|---:|---:|
| Always fast | 0.6681 ± 0.0554 | 32.00 | 40.00 |
| Always continuous | 0.7846 ± 0.0306 | 128.00 | 0.00 |
| Adaptive | 0.7850 ± 0.0304 | 122.86 ± 0.50 | 38.93 ± 0.08 |

For the adaptive method:

```text
coverage: 0.0535 ± 0.0052
selective accuracy: 0.9623 ± 0.0239
false-confidence rate among accepted samples: 0.0377 ± 0.0239
fallback rate: 0.9465 ± 0.0052
snapshot reduction relative to M=128: about 4.02 percent
```

### Severe fixed-device mismatch

```text
always-fast accuracy: 0.6563
always-continuous accuracy: 0.7738
adaptive accuracy: 0.7748
adaptive nominal-to-severe accuracy drop: 0.0102
adaptive coverage: 0.0469
```

### SNR and boundary behavior

At `-15 dB`, both adaptive and always-continuous accuracy averaged `0.4167`,
and the gate accepted no samples. Near the closest boundary offsets, continuous
and adaptive accuracy fell to approximately `0.44–0.49`, while adaptive
coverage was only about `0.8–1.5%`. At `±10` degrees from a boundary, adaptive
accuracy recovered to approximately `0.88–0.90`.

## Engineering Interpretation

The Day 4 single-seed result did not generalize as an efficiency result. The
fixed gate preserved continuous-baseline accuracy and kept accepted decisions
highly selective, but it fell back on about `94.65%` of nominal samples.
Therefore the earlier `30%` snapshot reduction must remain labeled as a
development-seed observation, not a final project claim.

Day 5 is a successful validation checkpoint but an unsuccessful generalization
of the proposed efficiency gain. This negative result is retained because it
identifies the next real research problem: the current LIF margin is not a
stable, calibrated confidence measure across seeds, SNR, and boundary geometry.

## Reproduction Commands

Run from the repository root:

```powershell
python -m unittest discover -s phase_02_confidence_aware_fast_slow_doa/tests -v
python -m phase_02_confidence_aware_fast_slow_doa.run_day_02_progressive_snapshot_validation
python -m phase_02_confidence_aware_fast_slow_doa.run_day_03_causal_gate_validation
python -m phase_02_confidence_aware_fast_slow_doa.run_day_04_adaptive_controller
python -m phase_02_confidence_aware_fast_slow_doa.run_day_05_stress_tests
```

## Primary Outputs

```text
results/day_05_per_seed_metrics.csv
results/day_05_aggregate_metrics.csv
results/day_05_stress_test_summary.json
```

## Next Step

Day 6 should create figures and tables from the frozen Day 5 outputs and explain
the failure modes without tuning on the validation results. A subsequent gate
redesign must introduce a distinct calibration/development set and then use
fresh holdout seeds for evaluation.
