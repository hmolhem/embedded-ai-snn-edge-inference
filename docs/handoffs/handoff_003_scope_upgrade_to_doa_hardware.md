# Handoff 003 — Scope Upgrade to Physics-Based DOA and Hardware-Facing Inference

## 1. Context

The initial Phase 1 concept used a generic synthetic embedded-sensing dataset to test spike encoding and a lightweight LIF-inspired classifier. During review, this was judged to be too weak as the core summer-term project. It was useful only as a smoke test, not as a strong final project.

The project scope has therefore been upgraded. The course project should be based on a physics-based DOA sensing model, not arbitrary synthetic data. The intended direction is to generate array-sensing data using a proper ULA/DOA model, apply spike encoding, perform DOA-sector inference, and prepare the inference path for hardware implementation.

## 2. Key Decision

The project is no longer defined primarily as:

```text
generic synthetic sensing vector -> spike encoding -> LIF classifier
```

The upgraded project is:

```text
physics-based ULA/DOA data generation
        -> covariance or beamspace feature extraction
        -> spike encoding
        -> LIF-inspired edge inference
        -> DOA-sector output
        -> hardware-facing implementation path
```

## 3. Revised Course-Facing Title

```text
Spike-Based Edge Inference for Physics-Based DOA Sector Estimation
```

## 4. Internal Research Direction

```text
Hardware-Aware Spike-Encoded DOA Inference for Edge Robotic Sensing
```

This internal direction can connect to prior work in MIMO radar, covariance computation, Jacobi-based DOA estimation, FPGA acceleration, PYNQ, and Vitis HLS.

## 5. Technical Model

The dataset will be generated using a single-source narrowband ULA model:

```text
x[m] = a(theta) s[m] + n[m]
```

where:

```text
x[m]      : received array vector at snapshot m
a(theta) : steering vector
s[m]      : complex source signal
n[m]      : complex Gaussian noise
```

For a ULA:

```text
a_n(theta) = exp(-j 2 pi d n sin(theta) / lambda)
```

Initial assumptions:

```text
Array elements: 8
Spacing: lambda/2
Source model: single narrowband source
Noise: additive complex Gaussian
DOA range: -60 deg to +60 deg
Task: coarse DOA sector classification
```

Initial sector labels:

```text
Class 0: -60 deg to -30 deg
Class 1: -30 deg to   0 deg
Class 2:   0 deg to  30 deg
Class 3:  30 deg to  60 deg
```

## 6. Feature Plan

Candidate features:

```text
1. diagonal power features from sample covariance
2. magnitudes of selected off-diagonal covariance entries
3. real/imaginary parts of selected covariance terms
4. beamspace energy features over a small steering grid
```

The sample covariance matrix is:

```text
R_xx = (1/M) sum_m x[m] x[m]^H
```

The first practical implementation should keep the feature vector compact and hardware-friendly.

## 7. Spike and Inference Plan

The extracted features will be normalized to `[0, 1]`, then rate-encoded into spike trains:

```text
P(spike_k[t] = 1) = feature_k
```

The first classifier will be a LIF-inspired class accumulator:

```text
spike features -> class membrane potentials -> leak/update -> final sector decision
```

Decision rule:

```text
predicted class = argmax(final membrane potential)
```

## 8. Hardware Implementation Path

The realistic staged hardware path is:

```text
Stage 1: Python reference model
Stage 2: fixed-point friendly spike encoder and LIF update
Stage 3: PYNQ/Zynq or FPGA-facing demonstration
Stage 4: optional Vitis HLS kernel for spike encoding or LIF inference
```

The course project should target a hardware-facing DOA-sector inference pipeline. Full continuous-angle DOA estimation on FPGA is possible as a research extension, but it is too large to guarantee as the minimum summer-course deliverable.

## 9. Success Criteria

Minimum success criteria:

```text
1. physics-based ULA/DOA dataset generation
2. DOA-sector labels from physical angles
3. compact covariance or beamspace features
4. spike encoding implementation
5. LIF-inspired sector classification
6. baseline comparison
7. accuracy versus SNR
8. hardware-aware discussion
```

Preferred success criteria:

```text
1. fixed-point-ready spike/LIF implementation
2. PYNQ or HLS-facing kernel plan
3. operation-count and memory-footprint analysis
4. report-quality figures and reproducible results
```

## 10. Repository Updates

The main course proposal was revised:

```text
docs/project_proposal/course_project_proposal.md
```

The revised proposal now reflects physics-based DOA data generation, spike encoding, LIF-inspired DOA-sector inference, baseline comparison, and hardware-facing implementation.

## 11. Immediate Next Actions

1. Pull the updated repository locally.
2. Review the revised course proposal.
3. Replace the toy Phase 1 implementation plan with a DOA reference model.
4. Implement the ULA data generator.
5. Implement feature extraction.
6. Implement spike encoding.
7. Implement LIF-inspired classifier.
8. Run baseline DOA-sector classification.
9. Add handoff after first DOA run.

## 12. Resume Point for Next Chat

Continue from Handoff 003. The project scope has been upgraded from a generic synthetic sensing prototype to a physics-based DOA-sector inference project with spike encoding and hardware-facing implementation. The next task is to implement the Python ULA/DOA data generator and define the compact feature vector.
