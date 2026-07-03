# Phase 1 Report Section — DOA-Sector Inference with LIF-Inspired Edge Processing

## 1. Purpose

This section summarizes the first completed engineering prototype for embedded AI inference in this project. The objective is to demonstrate a complete, reproducible Python reference model for direction-of-arrival (DOA) sector classification using a physics-based uniform linear array (ULA) signal model, a conventional non-spiking baseline, rate-based spike encoding, and a lightweight LIF-inspired classifier.

The purpose of this phase is not to claim a novel DOA algorithm. Instead, the purpose is to establish a controlled engineering baseline that can later be refactored toward embedded, FPGA, PYNQ, or Vitis HLS implementation.

## 2. Signal Model and Dataset

The Phase 1 dataset is generated from a narrowband single-source ULA model. For each simulated source angle and SNR value, the received array snapshot matrix is modeled as

```math
X = a(\theta)s + N,
```

where `a(theta)` is the ULA steering vector, `s` is a complex narrowband source signal, and `N` is circular complex additive white Gaussian noise. The sample covariance matrix is computed as

```math
R_{xx} = \frac{1}{M}XX^H,
```

where `M = 128` snapshots.

The feature vector is extracted using beamspace energy values over a fixed angular grid. These features are then normalized using training-set statistics before baseline classification or spike encoding.

Dataset configuration:

| Parameter | Value |
|---|---:|
| Array type | Uniform Linear Array |
| Number of array elements | 8 |
| Snapshots per sample | 128 |
| Element spacing | lambda / 2 |
| Source count | 1 |
| DOA range | -60 deg to +60 deg |
| Number of DOA sectors | 4 |
| SNR values | -10, -5, 0, 5, 10, 15, 20 dB |
| Samples per sector per SNR | 100 |
| Total samples | 2800 |
| Train/test split | 70/30, stratified by SNR and class |
| Test samples | 840 |

## 3. Baseline Classifier

The non-spiking reference classifier is a nearest-centroid classifier trained on the normalized beamspace feature vectors. This baseline is intentionally simple, deterministic, and interpretable. Its role is to establish how much DOA-sector information is present in the compact feature representation before converting the features into spike trains.

The baseline achieved the following overall test accuracy:

```text
nearest_centroid_overall_accuracy = 0.869048
```

Baseline accuracy versus SNR:

| SNR (dB) | Accuracy |
|---:|---:|
| -10 | 0.758333 |
| -5 | 0.908333 |
| 0 | 0.891667 |
| 5 | 0.858333 |
| 10 | 0.866667 |
| 15 | 0.925000 |
| 20 | 0.875000 |

The baseline result confirms that the beamspace features are informative for coarse DOA-sector classification.

## 4. Spike Encoding and LIF-Inspired Inference

Normalized beamspace features are converted into binary spike trains using rate-based encoding. A feature with larger normalized magnitude has a higher probability of emitting spikes across the time window. This produces a sparse temporal representation suitable for later hardware-oriented experiments.

The LIF-inspired classifier is implemented as a class-level leaky membrane accumulator. It is not intended to be a biologically detailed spiking neural network. Instead, it is a hardware-facing approximation in which each class accumulates spike-driven evidence over time. The leak factor controls how much accumulated membrane evidence is retained from one time step to the next.

The fixed Run 003 LIF configuration used:

```text
num_time_steps = 20
leak = 0.97
```

Run 003 achieved:

```text
lif_overall_accuracy = 0.825000
mean_stable_decision_latency = 6.423810 time steps
```

This result is below the continuous nearest-centroid baseline but far above the 25% random baseline for four balanced DOA sectors. The result supports the feasibility of sparse temporal inference, while also showing the expected accuracy cost introduced by rate-coded spike representation.

## 5. Accuracy and Latency Comparison

Run 004 generated report-ready comparison figures:

```text
figures/run_004_accuracy_comparison_vs_snr.png
figures/run_004_lif_latency_vs_snr.png
```

The accuracy comparison overlays the nearest-centroid baseline and the LIF-inspired classifier on the same SNR grid. The latency plot reports the mean stable-decision latency of the LIF classifier as a function of SNR.

The latency trend supports the edge-inference interpretation: when the signal quality is higher, the LIF classifier generally stabilizes earlier. This suggests that the temporal decision process can potentially be used for early-exit or adaptive-latency embedded inference in later phases.

## 6. Run 005 Parameter Sweep

Run 005 evaluates the sensitivity of the LIF-inspired classifier to two hardware-relevant parameters:

```text
num_time_steps
leak
```

Sweep grid:

| Parameter | Values |
|---|---|
| num_time_steps | 10, 20, 30, 40 |
| leak | 0.90, 0.95, 0.97, 0.99 |
| total configurations | 16 |

Run 005 generated:

```text
results/run_005_lif_parameter_sweep.csv
results/run_005_lif_parameter_sweep_summary.txt
figures/run_005_lif_accuracy_latency_tradeoff.png
```

Run 005 key results:

| Case | num_time_steps | leak | Accuracy | Mean latency steps |
|---|---:|---:|---:|---:|
| Best LIF accuracy | 40 | 0.99 | 0.841667 | 8.396429 |
| Lowest mean latency | 10 | 0.99 | 0.776190 | 3.782143 |
| Fixed Run 003 reference | 20 | 0.97 | 0.825000 | 6.423810 |
| Non-spiking baseline | N/A | N/A | 0.869048 | N/A |

Full Run 005 sweep:

| num_time_steps | leak | Accuracy | Mean latency steps |
|---:|---:|---:|---:|
| 10 | 0.90 | 0.773810 | 4.280952 |
| 10 | 0.95 | 0.778571 | 4.011905 |
| 10 | 0.97 | 0.779762 | 3.914286 |
| 10 | 0.99 | 0.776190 | 3.782143 |
| 20 | 0.90 | 0.809524 | 7.732143 |
| 20 | 0.95 | 0.816667 | 6.579762 |
| 20 | 0.97 | 0.819048 | 6.340476 |
| 20 | 0.99 | 0.816667 | 5.753571 |
| 30 | 0.90 | 0.802381 | 10.946429 |
| 30 | 0.95 | 0.829762 | 8.870238 |
| 30 | 0.97 | 0.838095 | 8.126190 |
| 30 | 0.99 | 0.832143 | 7.352381 |
| 40 | 0.90 | 0.801190 | 14.945238 |
| 40 | 0.95 | 0.822619 | 10.778571 |
| 40 | 0.97 | 0.830952 | 9.697619 |
| 40 | 0.99 | 0.841667 | 8.396429 |

## 7. Engineering Interpretation

The parameter sweep confirms a clear accuracy-latency design trade-off.

Increasing the spike time-window generally improves classification accuracy because the rate-coded representation has more opportunities to approximate the original normalized feature vector. However, a longer time window also increases the temporal budget and can increase stable-decision latency.

The leak factor controls evidence retention. Higher leak values generally preserve accumulated information better, which is helpful for this prototype because the DOA-sector decision depends on integrating evidence across sparse spike events. In the current sweep, the best LIF accuracy occurs at `T = 40` and `leak = 0.99`.

The best LIF accuracy improves over the fixed Run 003 LIF configuration:

```text
Run 003 fixed LIF accuracy = 0.825000
Run 005 best LIF accuracy  = 0.841667
```

However, the best LIF result remains below the continuous nearest-centroid baseline:

```text
nearest-centroid baseline accuracy = 0.869048
best LIF sweep accuracy            = 0.841667
```

This is an expected and useful result. The spike-based classifier trades some continuous-valued accuracy for sparse temporal processing and explicit latency control. That trade-off is central to the embedded AI motivation of this project.

## 8. Report-Ready Conclusions

The Phase 1 Python prototype successfully establishes an end-to-end DOA-sector inference pipeline based on a physics-derived ULA signal model. The nearest-centroid classifier demonstrates that compact beamspace features provide strong sector-level DOA information, achieving 86.9% test accuracy.

The LIF-inspired spike classifier demonstrates that the same normalized features can be converted into sparse temporal spike trains and classified using a hardware-facing leaky evidence accumulator. The fixed LIF configuration achieves 82.5% accuracy, while the Run 005 parameter sweep improves the best LIF result to 84.17%.

The Run 005 sweep shows that the LIF model has tunable behavior. Shorter spike windows reduce latency at the cost of accuracy, while longer windows and stronger membrane retention improve accuracy. This supports the next project step: using the Python reference model as a stable baseline for embedded implementation and later hardware acceleration.

## 9. Files to Reference in the Report

Recommended figures:

```text
figures/run_001_example_beamspace_response.png
figures/run_004_accuracy_comparison_vs_snr.png
figures/run_004_lif_latency_vs_snr.png
figures/run_005_lif_accuracy_latency_tradeoff.png
```

Recommended tables:

```text
results/run_001_accuracy_vs_snr.csv
results/run_003_lif_accuracy_vs_snr.csv
results/run_003_lif_latency_vs_snr.csv
results/run_005_lif_parameter_sweep.csv
```

Recommended summary files:

```text
results/run_001_metrics.txt
results/run_003_lif_metrics.txt
results/run_005_lif_parameter_sweep_summary.txt
```
