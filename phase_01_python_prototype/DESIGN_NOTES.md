# Phase 1 Design Notes

## 1. Design Status

Status: **revised and frozen for DOA-based initial implementation**

This file records the concrete design for Phase 1 of the project while preserving the original phase structure:

```text
Phase 1: Python prototype
Phase 2: Radar/DOA sensing case study
Phase 3: PYNQ edge demo
Phase 4: Vitis HLS kernel
```

The important correction is that Phase 1 will not use an arbitrary toy dataset. The Python prototype will be based on a proper engineering DOA model using a Uniform Linear Array (ULA), array snapshots, sample covariance features, spike encoding, and lightweight LIF-inspired sector inference.

The purpose of Phase 1 is to build the first end-to-end reference model:

```text
physics-based DOA data generation
        -> covariance-derived feature extraction
        -> feature normalization
        -> spike encoding
        -> LIF-inspired DOA-sector inference
        -> metrics and figures
```

## 2. Relation to Prior Work

A previous project developed a hardware-aware Vitis HLS acceleration study for Sample Covariance Matrix (SCM) computation in MIMO radar / DOA preprocessing. That prior work used:

```text
N = 8 ULA elements
M = 128 snapshots
SCM computation as the main DOA preprocessing bottleneck
FPGA/HLS optimization of the covariance kernel
```

Phase 1 of the present project builds on that direction at the algorithmic Python-reference level. Instead of repeating the SCM accelerator, this phase uses SCM-derived or beamspace features as inputs to a spike-based edge-inference pipeline for DOA-sector estimation.

## 3. Physical DOA Data Model

The dataset will be generated from a single-source narrowband array model:

```text
x[m] = a(theta) s[m] + n[m]
```

where:

```text
x[m]      : received complex array vector at snapshot m
a(theta) : ULA steering vector
s[m]      : complex source sample
n[m]      : additive complex Gaussian noise
m         : snapshot index
```

For a ULA, the steering vector is:

```text
a_n(theta) = exp(-j 2 pi d n sin(theta) / lambda)
```

Initial assumptions:

```text
Array type:          Uniform Linear Array
Number of elements:  N = 8
Snapshots:           M = 128
Element spacing:     d = lambda/2
Source count:        1
Signal type:         narrowband complex baseband
Noise model:         additive complex Gaussian noise
DOA range:           -60 deg to +60 deg
Task:                coarse DOA-sector classification
```

## 4. DOA Sector Labels

The first classification task is DOA-sector estimation, not continuous-angle super-resolution estimation.

Initial sectors:

```text
Class 0: -60 deg to -30 deg
Class 1: -30 deg to   0 deg
Class 2:   0 deg to  30 deg
Class 3:  30 deg to  60 deg
```

For each simulated sample:

1. draw a true DOA angle from the angular range,
2. assign the DOA angle to one of the four sectors,
3. generate `M` array snapshots,
4. add noise according to the selected SNR,
5. compute the sample covariance matrix or beamspace response,
6. extract compact features for spike-based inference.

## 5. SNR Sweep

The initial run will include multiple SNR values to make the result engineering-relevant.

Recommended first sweep:

```text
SNR_dB = [-10, -5, 0, 5, 10, 15, 20]
```

Recommended first dataset size:

```text
samples_per_class_per_snr = 100 to 250
```

The exact number can be adjusted for runtime.

## 6. Feature Extraction

The feature vector must come from the physical DOA model. It should not be an arbitrary random vector.

Initial candidate feature sets:

### Option A — Covariance Magnitude Features

Use selected entries of the sample covariance matrix:

```text
R_xx = (1/M) sum_m x[m] x[m]^H
```

Candidate components:

```text
- diagonal powers: abs(R[i,i])
- selected off-diagonal magnitudes: abs(R[i,j])
- selected real/imaginary covariance terms if needed
```

### Option B — Beamspace Energy Features

Evaluate a small steering grid and compute beam energies:

```text
E(theta_g) = |a(theta_g)^H R_xx a(theta_g)|
```

Then use the beam energies over a coarse grid as a compact feature vector.

### Initial Choice

For Run 001, the recommended first feature is **beamspace energy over a small steering grid**, because it is physically interpretable for DOA-sector inference and naturally produces nonnegative features suitable for rate-based spike encoding.

Recommended grid:

```text
beam_grid_deg = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
num_features  = 9
```

This feature vector is still compact and hardware-friendly.

## 7. Feature Normalization

Before spike encoding, each feature vector will be normalized to `[0, 1]`.

Recommended method:

```text
Use train-set min/max values for each feature.
Apply the same normalization to test data.
Clip normalized values to [0, 1].
```

## 8. Spike Encoding

The first spike-encoding method will be **rate-based encoding**.

For each normalized feature value:

```text
P(spike_k[t] = 1) = feature_k
```

Initial parameter:

```text
num_time_steps = 20
```

Spike tensor shape:

```text
num_samples x num_time_steps x num_features
```

## 9. LIF-Inspired Classifier

The first classifier will be a lightweight LIF-inspired class accumulator.

Concept:

```text
input spike trains
        -> weighted class accumulation
        -> leaky membrane update
        -> final class membrane potentials
        -> predicted DOA sector
```

Decision rule:

```text
predicted class = argmax(final membrane potential)
```

Initial weight strategy:

```text
Use class prototypes estimated from the training features.
The spike/LIF classifier acts as a hardware-friendly temporal template matcher.
```

This avoids starting with a heavy training algorithm before the pipeline is validated.

## 10. Baseline Comparison

Phase 1 should include at least one non-spiking baseline on the same features.

Recommended baseline for Run 001:

```text
nearest-centroid classifier on normalized beamspace/covariance features
```

Optional later baselines:

```text
- logistic regression
- small MLP
- classical maximum-beam sector decision
```

## 11. Metrics

Minimum metrics for Run 001:

```text
- classification accuracy versus SNR
- confusion matrix at selected SNR values
- average spike count per sample
- spike-count distribution
- latency proxy in time steps
- comparison with nearest-centroid baseline
```

Hardware-aware metrics for later refinement:

```text
- feature-vector dimension
- number of time steps
- approximate operation count
- approximate memory footprint
- fixed-point feasibility
```

## 12. Figures

Minimum figures for Run 001:

```text
1. example beamspace response versus angle grid
2. accuracy versus SNR
3. confusion matrix at a selected SNR
4. spike-count distribution
```

Optional figures:

```text
- true DOA histogram by sector
- spike raster for one example sample
- accuracy versus number of time steps
- baseline versus spike classifier comparison
```

## 13. Planned Output Files

Results should be saved under:

```text
phase_01_python_prototype/results/
```

Figures should be saved under:

```text
phase_01_python_prototype/figures/
```

Recommended first output files:

```text
results/run_001_metrics.txt
results/run_001_accuracy_vs_snr.csv
figures/run_001_example_beamspace_response.png
figures/run_001_accuracy_vs_snr.png
figures/run_001_confusion_matrix_snr_10db.png
figures/run_001_spike_count_distribution.png
```

## 14. Implementation Modules

The existing scaffold remains valid:

```text
src/dataset.py
src/spike_encoding.py
src/lif.py
src/metrics.py
src/plots.py
src/main.py
run_phase_01.py
```

Updated module responsibilities:

```text
dataset.py          ULA/DOA data generation, steering vector, snapshots, covariance/beamspace features
spike_encoding.py   rate-based spike encoding
lif.py              LIF-inspired class-level sector inference
metrics.py          accuracy, confusion matrix, SNR summaries, spike statistics
plots.py            result figures
main.py             run full Phase 1 experiment
run_phase_01.py     convenience runner
```

## 15. Non-Goals for Phase 1

Phase 1 does not attempt:

```text
- full MUSIC or ESPRIT implementation
- full multi-source high-resolution DOA estimation
- full neuromorphic-chip design
- PYNQ deployment
- Vitis HLS synthesis
- complete FPGA accelerator
```

However, Phase 1 must remain compatible with the later hardware path. The feature extraction, spike encoding, and LIF update should be written in a way that can later be refactored toward fixed-point and HLS-friendly code.

## 16. Success Criteria for Run 001

Run 001 is successful if it produces:

```text
- physics-based ULA/DOA dataset generation
- valid DOA-sector labels
- compact beamspace or covariance-derived feature vectors
- nearest-centroid baseline result
- spike/LIF-inspired classifier result
- accuracy versus SNR
- saved metrics file
- saved figures
- interpretable spike-count statistics
```

## 17. Next Step

Implement the Phase 1 DOA Python reference model using this frozen design.

After the first successful run, create:

```text
docs/handoffs/handoff_004_phase_01_doa_run_001_results.md
```
