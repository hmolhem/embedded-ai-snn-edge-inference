# Phase 1 Experiment Log

This file tracks Phase 1 runs.

## Run 001 — DOA Python Reference Baseline

Status: completed locally.

Purpose: first end-to-end DOA-sector inference baseline using a physics-based ULA model.

Pipeline:

```text
ULA snapshots
    -> sample covariance matrix
    -> beamspace energy features
    -> feature normalization
    -> nearest-centroid baseline
    -> rate-based spike encoding
    -> LIF-inspired DOA-sector inference
    -> accuracy, confusion, spike, and latency metrics
```

Configuration:

```text
N = 8
M = 128
d = lambda/2
DOA range = -60 deg to +60 deg
Sectors = 4
SNR sweep = [-10, -5, 0, 5, 10, 15, 20] dB
Samples per class per SNR = 100
Total samples = 2800
Train/test split = 70/30, stratified by SNR and class
Spike time steps = 20
LIF leak = 0.97
```

Dataset summary:

```text
num_samples: 2800
num_features: 9
train_samples: 1960
test_samples: 840
class_counts: 700 per class
snr_counts: 400 per SNR value
```

Nearest-centroid baseline:

```text
overall_accuracy: 0.869048
```

Baseline accuracy versus SNR:

```text
-10.0 dB: 0.758333
 -5.0 dB: 0.908333
  0.0 dB: 0.891667
  5.0 dB: 0.858333
 10.0 dB: 0.866667
 15.0 dB: 0.925000
 20.0 dB: 0.875000
```

Rate-based spike encoding:

```text
num_time_steps: 20
num_features: 9
max_possible_spikes_per_sample: 180
mean_test_firing_rate: 0.143201
mean_test_spike_count_per_sample: 25.776190
```

LIF-inspired spike classifier:

```text
overall_accuracy: 0.825000
mean_latency_steps: 6.423810
std_latency_steps: 6.148086
min_latency_steps: 1
max_latency_steps: 20
```

LIF accuracy versus SNR:

```text
-10.0 dB: 0.658333
 -5.0 dB: 0.816667
  0.0 dB: 0.800000
  5.0 dB: 0.866667
 10.0 dB: 0.883333
 15.0 dB: 0.883333
 20.0 dB: 0.866667
```

LIF mean latency versus SNR:

```text
-10.0 dB: 8.775000
 -5.0 dB: 8.641667
  0.0 dB: 7.383333
  5.0 dB: 5.566667
 10.0 dB: 4.783333
 15.0 dB: 4.841667
 20.0 dB: 4.975000
```

Generated outputs:

```text
results/run_001_dataset_summary.txt
results/run_001_metrics.txt
results/run_001_accuracy_vs_snr.csv
results/run_002_spike_encoding_summary.txt
results/run_003_lif_metrics.txt
results/run_003_lif_accuracy_vs_snr.csv
results/run_003_lif_latency_vs_snr.csv
figures/run_001_example_beamspace_response.png
figures/run_001_accuracy_vs_snr.png
figures/run_001_confusion_matrix_snr_10db.png
figures/run_002_spike_count_distribution.png
figures/run_003_lif_accuracy_vs_snr.png
figures/run_003_lif_confusion_matrix_snr_10db.png
```

Interpretation:

The first complete Phase 1 run is successful. The nearest-centroid baseline confirms that compact beamspace features are informative for coarse DOA-sector inference. The LIF-inspired spike classifier achieves 82.5% accuracy using sparse rate-coded spike trains, far above the 25% random baseline. The mean stable-decision latency decreases as SNR improves, supporting the edge-inference interpretation.

Follow-up work completed after Run 001:

1. Generated report-ready accuracy and latency comparison plots.
2. Swept LIF time-step and leak parameters.
3. Recorded Run 005 CSV, summary, and trade-off figure.
4. Drafted the Phase 1 report-ready narrative section.
5. Added a Phase 1 documentation index.

## Run 004 — Accuracy and Latency Comparison Plots

Status: completed locally.

Purpose: generate report-ready comparison plots for the Phase 1 DOA nearest-centroid baseline and LIF-inspired spike classifier.

Generated figures:

```text
figures/run_004_accuracy_comparison_vs_snr.png
figures/run_004_lif_latency_vs_snr.png
```

Interpretation:

The accuracy comparison plot overlays the continuous-valued nearest-centroid baseline and the sparse LIF-inspired spike classifier across the same SNR grid. The latency plot shows the mean stable-decision latency of the LIF classifier versus SNR, with the full spike window used as a reference.

This run supports the Phase 1 accuracy-latency-energy narrative for embedded neuromorphic inference.

## Run 005 — LIF Time-Step and Leak Parameter Sweep

Status: completed locally.

Purpose: evaluate the sensitivity of the LIF-inspired spike classifier to spike-window length and membrane leak factor.

Sweep grid:

```text
num_time_steps = [10, 20, 30, 40]
leak = [0.90, 0.95, 0.97, 0.99]
total_configurations = 16
```

Reference baseline:

```text
baseline_nearest_centroid_accuracy: 0.869048
```

Best accuracy configuration:

```text
num_time_steps: 40
leak: 0.99
overall_accuracy: 0.841667
mean_latency_steps: 8.396429
```

Lowest latency configuration:

```text
num_time_steps: 10
leak: 0.99
overall_accuracy: 0.776190
mean_latency_steps: 3.782143
```

Generated outputs:

```text
results/run_005_lif_parameter_sweep.csv
results/run_005_lif_parameter_sweep_summary.txt
figures/run_005_lif_accuracy_latency_tradeoff.png
```

Interpretation:

Run 005 confirms the expected accuracy-latency trade-off. Increasing the spike-window length generally improves LIF accuracy, while shorter windows reduce stable-decision latency. Higher leak values tend to preserve accumulated evidence better. The best LIF configuration improves over the fixed Run 003 setting but remains below the continuous nearest-centroid baseline, which is consistent with the intended embedded sparse-inference narrative.
