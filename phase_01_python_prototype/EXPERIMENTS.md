# Phase 1 Experiment Log

This file tracks Phase 1 runs.

## Run 001 — DOA Python Reference Baseline

Status: pending.

Purpose: first end-to-end DOA-sector inference baseline using a physics-based ULA model.

Planned pipeline:

```text
ULA snapshots
    -> sample covariance matrix
    -> beamspace or covariance-derived features
    -> feature normalization
    -> rate-based spike encoding
    -> LIF-inspired DOA-sector inference
    -> baseline comparison
```

Initial configuration:

```text
N = 8
M = 128
d = lambda/2
DOA range = -60 deg to +60 deg
Sectors = 4
SNR sweep = [-10, -5, 0, 5, 10, 15, 20] dB
Spike time steps = 20
```

Expected outputs:

```text
results/run_001_metrics.txt
results/run_001_accuracy_vs_snr.csv
figures/run_001_example_beamspace_response.png
figures/run_001_accuracy_vs_snr.png
figures/run_001_confusion_matrix_snr_10db.png
figures/run_001_spike_count_distribution.png
```
