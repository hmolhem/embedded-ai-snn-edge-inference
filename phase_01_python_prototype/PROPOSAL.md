# Phase 1 Proposal — DOA Python Reference Prototype

## 1. Title

**Spike-Based DOA Sector Inference Using Physics-Based Array Features**

## 2. Motivation

Edge-AI systems for robotics, radar, wireless sensing, and autonomous platforms often need directional awareness under strict constraints on power, memory, latency, and compute resources. Direction-of-arrival (DOA) estimation is a core sensing primitive, but full high-resolution DOA algorithms can be computationally demanding for embedded edge hardware.

This phase establishes the Python reference model for a hardware-facing spike-based DOA inference pipeline. The project will not start from arbitrary random feature vectors. Instead, the input data will be generated from a proper Uniform Linear Array (ULA) signal model and converted into compact covariance-derived or beamspace features.

The purpose of Phase 1 is to demonstrate a physically meaningful end-to-end pipeline that can later be refined toward PYNQ and Vitis HLS implementation.

## 3. Problem Statement

The problem is to determine whether physics-based array-sensing features can be converted into spike trains and used by a lightweight LIF-inspired classifier to infer coarse DOA sectors.

The central question is:

```text
Can a compact spike-based edge-inference pipeline classify DOA sectors from ULA-generated covariance or beamspace features?
```

## 4. Objective

Build an end-to-end Python prototype that performs:

1. ULA/DOA data generation,
2. steering-vector construction,
3. snapshot generation under controlled SNR,
4. sample covariance or beamspace feature extraction,
5. feature normalization,
6. spike encoding,
7. LIF-inspired DOA-sector classification,
8. baseline comparison,
9. metric and figure generation.

## 5. Technical Scope

### Included

- N = 8 ULA model
- M = 128 snapshots
- single-source narrowband signal model
- additive complex Gaussian noise
- SNR sweep
- DOA sector labels
- beamspace or covariance-derived feature vector
- rate-based spike encoding
- lightweight LIF-inspired classifier
- nearest-centroid baseline
- accuracy versus SNR
- confusion matrix
- average spike count
- latency proxy in time steps
- clean figures and result summaries

### Excluded in Phase 1

- full MUSIC or ESPRIT implementation
- full multi-source high-resolution DOA estimation
- PYNQ deployment
- Vitis HLS synthesis
- full FPGA accelerator
- neuromorphic-chip design
- robotic simulator dependency

These are reserved for later phases or future work.

## 6. Methodology

### 6.1 ULA Signal Model

The received array snapshot is modeled as:

```text
x[m] = a(theta) s[m] + n[m]
```

where:

```text
x[m]      : received array vector at snapshot m
a(theta) : steering vector
s[m]      : complex source sample
n[m]      : additive complex Gaussian noise
```

For a ULA:

```text
a_n(theta) = exp(-j 2 pi d n sin(theta) / lambda)
```

Initial parameters:

```text
N = 8
M = 128
d = lambda/2
DOA range = -60 deg to +60 deg
```

### 6.2 Sector Labels

The first task is coarse DOA-sector classification:

```text
Class 0: -60 deg to -30 deg
Class 1: -30 deg to   0 deg
Class 2:   0 deg to  30 deg
Class 3:  30 deg to  60 deg
```

### 6.3 Feature Extraction

The first implementation will use a compact feature vector suitable for spike encoding and later hardware refactoring.

Recommended first feature:

```text
beamspace energy over a small steering grid
```

Candidate grid:

```text
[-60, -45, -30, -15, 0, 15, 30, 45, 60] degrees
```

Feature definition:

```text
E(theta_g) = |a(theta_g)^H R_xx a(theta_g)|
```

where:

```text
R_xx = (1/M) sum_m x[m] x[m]^H
```

### 6.4 Spike Encoding

The beamspace or covariance feature vector is normalized to `[0, 1]` and then encoded using rate-based spike encoding:

```text
P(spike_k[t] = 1) = feature_k
```

Initial parameter:

```text
num_time_steps = 20
```

### 6.5 LIF-Inspired Classifier

A lightweight class-level LIF-inspired accumulator will integrate spikes over time and output the predicted DOA sector.

Decision rule:

```text
predicted class = argmax(final membrane potential)
```

Initial weights can be derived from class prototypes estimated from the training set.

## 7. Implementation Modules

The existing module structure remains unchanged:

```text
src/dataset.py          ULA/DOA data generation and feature extraction
src/spike_encoding.py   spike encoding
src/lif.py              LIF-inspired DOA-sector classifier
src/metrics.py          metrics and summaries
src/plots.py            plotting
src/main.py             experiment runner
run_phase_01.py         convenience runner
```

## 8. Expected Deliverables

- Python code under `src/`
- ULA/DOA data generator
- beamspace or covariance feature extractor
- spike-encoding module
- LIF-inspired inference module
- nearest-centroid baseline
- accuracy-versus-SNR figure
- confusion matrix figure
- spike-count distribution
- metrics file under `results/`
- figures under `figures/`
- updated `DESIGN_NOTES.md`
- updated `EXPERIMENTS.md`
- handoff after first DOA run

## 9. Evaluation Metrics

Minimum metrics:

- classification accuracy versus SNR
- confusion matrix
- average spike count per sample
- latency proxy in time steps
- comparison with nearest-centroid baseline

Optional metrics:

- accuracy versus number of time steps
- spike-count distribution by class
- operation-count estimate
- memory-footprint estimate
- fixed-point feasibility discussion

## 10. Risks and Limitations

The main risk is scope expansion. A full DOA estimator, full SNN training workflow, and full FPGA accelerator are each substantial tasks. Phase 1 therefore focuses on a controlled single-source DOA-sector inference problem.

Another limitation is that Phase 1 is still a Python reference model. Hardware deployment is reserved for later phases. However, the implementation should be written with hardware refactoring in mind.

## 11. Future Extension

After Phase 1 is stable, the same software architecture can be extended toward:

- broader radar/DOA sensing case study,
- more feature sets,
- SNR and snapshot-count sensitivity analysis,
- PYNQ ARM-side execution,
- fixed-point spike/LIF implementation,
- Vitis HLS implementation of the inference kernel,
- paper-level comparison with classical and lightweight neural baselines.
