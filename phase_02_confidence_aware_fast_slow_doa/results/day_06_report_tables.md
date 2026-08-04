# Day 6 Frozen-Result Tables

These tables are generated only from the fixed Day 5 outputs. No threshold,
persistence, model parameter, or operating point is reselected here.

## Frozen input hashes

| Input | SHA-256 |
|---|---|
| `day_05_per_seed_metrics.csv` | `408b1858bda81a7e717d3c62f1544076898ec17a03d43872f7ffd4cb6e1dde1a` |
| `day_05_aggregate_metrics.csv` | `9263b8fce32060ab537ac0762f3b4798feb591d65f3ae98e9ec3560327a14e68` |
| `day_05_stress_test_summary.json` | `dde822e162d4856a3af9648df0f114ca55eade21c89205e9e62e54099211b48a` |
| `day_05_stress_config.json` | `e90e7f1b081d2ff8c337326f2d6ca87ab7b05f00d25f4aeb489739c251106e2f` |

## Nominal five-seed summary

| Method | Accuracy | Coverage | Selective accuracy | Fallback rate | Avg. snapshots | Avg. LIF steps |
|---|---:|---:|---:|---:|---:|---:|
| Always fast | 0.6681 +/- 0.0554 | N/A | N/A | N/A | 32.00 +/- 0.00 | 40.00 +/- 0.00 |
| Always continuous | 0.7846 +/- 0.0306 | N/A | N/A | N/A | 128.00 +/- 0.00 | 0.00 +/- 0.00 |
| Adaptive | 0.7850 +/- 0.0304 | 0.0535 +/- 0.0052 | 0.9623 +/- 0.0239 | 0.9465 +/- 0.0052 | 122.86 +/- 0.50 | 38.93 +/- 0.08 |

## Selected stress endpoints

| Stress condition | Method | Accuracy | Coverage | Avg. snapshots |
|---|---|---:|---:|---:|
| SNR -15 dB | Always continuous | 0.4167 +/- 0.0503 | N/A | 128.00 +/- 0.00 |
| SNR -15 dB | Adaptive | 0.4167 +/- 0.0503 | 0.0000 +/- 0.0000 | 128.00 +/- 0.00 |
| SNR 0 dB | Always continuous | 0.8400 +/- 0.0406 | N/A | 128.00 +/- 0.00 |
| SNR 0 dB | Adaptive | 0.8417 +/- 0.0437 | 0.1317 +/- 0.0160 | 115.36 +/- 1.54 |
| SNR 20 dB | Always continuous | 0.8367 +/- 0.0481 | N/A | 128.00 +/- 0.00 |
| SNR 20 dB | Adaptive | 0.8383 +/- 0.0484 | 0.0283 +/- 0.0173 | 125.28 +/- 1.66 |
| Boundary -0.5 deg | Always continuous | 0.4942 +/- 0.1313 | N/A | 128.00 +/- 0.00 |
| Boundary -0.5 deg | Adaptive | 0.4933 +/- 0.1306 | 0.0083 +/- 0.0051 | 127.20 +/- 0.49 |
| Boundary +0.5 deg | Always continuous | 0.4442 +/- 0.1320 | N/A | 128.00 +/- 0.00 |
| Boundary +0.5 deg | Adaptive | 0.4442 +/- 0.1336 | 0.0150 +/- 0.0056 | 126.56 +/- 0.54 |
| Boundary -10 deg | Always continuous | 0.8992 +/- 0.0185 | N/A | 128.00 +/- 0.00 |
| Boundary -10 deg | Adaptive | 0.8958 +/- 0.0184 | 0.0467 +/- 0.0225 | 123.52 +/- 2.16 |
| Boundary +10 deg | Always continuous | 0.8817 +/- 0.0288 | N/A | 128.00 +/- 0.00 |
| Boundary +10 deg | Adaptive | 0.8808 +/- 0.0318 | 0.0483 +/- 0.0173 | 123.36 +/- 1.66 |

## Array-mismatch endpoint

| Method | Nominal accuracy | Severe accuracy | Drop |
|---|---:|---:|---:|
| Always fast | 0.6681 | 0.6562 | 0.0119 |
| Always continuous | 0.7846 | 0.7737 | 0.0108 |
| Adaptive | 0.7850 | 0.7748 | 0.0102 |

## Interpretation boundary

- The adaptive method preserves the continuous-baseline accuracy within the observed five-seed uncertainty.
- The fixed gate accepts only a small fraction of cases, so average snapshots remain close to 128.
- Low SNR and close boundary offsets are the dominant difficulty regimes.
- Fixed array mismatch causes a smaller accuracy loss than low SNR or boundary proximity in this experiment.
- These results describe the frozen Day 5 operating point; they do not justify gate retuning on the validation set.
