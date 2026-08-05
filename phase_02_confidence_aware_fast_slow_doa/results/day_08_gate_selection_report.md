# Day 8 Frozen Gate Selection

Day 8 applied the declared rule to the byte-verified Day 7 calibration grid.
No holdout data were generated or evaluated.

## Selected gate

| Metric | Value |
|---|---:|
| Threshold (tau) | 0.20 |
| Persistence (K) | 5 |
| Adaptive accuracy | 77.125% |
| Continuous accuracy | 78.083% |
| Accuracy gap | -0.958 pp |
| Coverage | 24.292% |
| Selective accuracy | 86.449% |
| Fallback rate | 75.708% |
| Average snapshots | 104.68 |
| Snapshot reduction | 18.219% |

## Comparison with the previous reference gate

The prior `tau=0.8, K=5` gate reduced
snapshots by 3.703%. The selected
gate improves calibration-set snapshot reduction by
14.516 percentage points while using
19.354 percentage points more fast-path coverage.

## Frozen boundary

The Day 9 holdout manifest remains `e2549c689da20987555303f6c6a7996c2299497de3e65cc2067142d43f193420` with
policy `sealed_until_day_09`. Day 9 may evaluate exactly this one gate once.
