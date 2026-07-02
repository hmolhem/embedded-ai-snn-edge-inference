# Handoff 003 — Phase 1 Alignment with Physics-Based DOA Model

## 1. Context

The original repository phase structure remains valid and should not be changed without explicit approval:

```text
Phase 1: Python prototype
Phase 2: Radar/DOA sensing case study
Phase 3: PYNQ edge demo
Phase 4: Vitis HLS kernel
```

The important correction is conceptual: Phase 1 should not be based on an arbitrary toy sensing dataset. The Python prototype must use a defensible engineering model connected to DOA, array processing, and future hardware implementation.

The project now uses the prior SCM/HLS work as the technical foundation. The previous project studied hardware-aware Sample Covariance Matrix computation for MIMO radar / DOA preprocessing. The present project extends the direction toward spike-based DOA-sector inference using covariance-derived or beamspace features.

## 2. Key Decision

Do not rename the phase folders and do not restructure the repository at this point.

The phase structure remains:

```text
phase_01_python_prototype/
phase_02_radar_sensing_case_study/
phase_03_pynq_edge_demo/
phase_04_vitis_hls_kernel/
```

However, the content of Phase 1 is upgraded from:

```text
arbitrary synthetic sensing vector -> spike encoding -> LIF classifier
```

to:

```text
physics-based ULA/DOA data generation
        -> covariance or beamspace feature extraction
        -> spike encoding
        -> LIF-inspired DOA-sector inference
        -> baseline comparison
        -> metrics and figures
```

## 3. Project Narrative

The project narrative is:

```text
Prior work:
SCM acceleration for MIMO radar / DOA preprocessing using HLS.

Current work:
Spike-based edge inference for DOA-sector estimation using SCM-derived or beamspace features.

Future hardware path:
PYNQ or Vitis HLS implementation of spike encoding and LIF inference kernels.
```

This creates a coherent professional pipeline from array-signal modeling to hardware-aware edge AI.

## 4. Phase 1 Technical Model

The Phase 1 dataset will be generated using a single-source narrowband ULA model:

```text
x[m] = a(theta) s[m] + n[m]
```

where:

```text
x[m]      : received array vector at snapshot m
a(theta) : ULA steering vector
s[m]      : complex source sample
n[m]      : additive complex Gaussian noise
m         : snapshot index
```

For a ULA:

```text
a_n(theta) = exp(-j 2 pi d n sin(theta) / lambda)
```

Initial assumptions:

```text
Array elements: 8
Snapshots: 128
Spacing: lambda/2
Source model: single narrowband source
Noise: additive complex Gaussian
DOA range: -60 deg to +60 deg
Task: coarse DOA-sector classification
```

Initial sector labels:

```text
Class 0: -60 deg to -30 deg
Class 1: -30 deg to   0 deg
Class 2:   0 deg to  30 deg
Class 3:  30 deg to  60 deg
```

## 5. Feature Plan

The first practical feature choice is beamspace energy over a small steering grid, because it is physically interpretable, nonnegative, compact, and suitable for rate-based spike encoding.

Recommended grid:

```text
beam_grid_deg = [-60, -45, -30, -15, 0, 15, 30, 45, 60]
num_features  = 9
```

Feature definition:

```text
E(theta_g) = |a(theta_g)^H R_xx a(theta_g)|
```

where:

```text
R_xx = (1/M) sum_m x[m] x[m]^H
```

Later feature alternatives:

```text
1. diagonal covariance powers
2. selected off-diagonal covariance magnitudes
3. real/imaginary upper-triangular covariance terms
4. expanded beamspace grids
```

## 6. Spike and Inference Plan

Extracted features will be normalized to `[0, 1]`, then rate-encoded into spike trains:

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

Initial classifier weights can be derived from class prototypes estimated from the training features.

## 7. Baseline Plan

Run 001 should include a non-spiking baseline on the same features.

Recommended baseline:

```text
nearest-centroid classifier on normalized beamspace features
```

This baseline will help show whether the spike-based path preserves useful DOA-sector information.

## 8. Hardware Implementation Path

The realistic staged hardware path remains:

```text
Phase 1: Python reference model
Phase 2: broader radar/DOA sensing case study
Phase 3: PYNQ edge demo using the inference path
Phase 4: Vitis HLS kernel for spike encoding or LIF inference
```

The course project should target a hardware-facing DOA-sector inference pipeline. Full continuous-angle DOA estimation or full MUSIC/ESPRIT acceleration can be treated as a research extension.

## 9. Success Criteria

Minimum success criteria for the first DOA-based implementation:

```text
1. physics-based ULA/DOA dataset generation
2. DOA-sector labels from physical angles
3. compact beamspace or covariance-derived features
4. spike encoding implementation
5. LIF-inspired sector classification
6. nearest-centroid baseline comparison
7. accuracy versus SNR
8. confusion matrix
9. spike-count analysis
10. hardware-aware discussion
```

Preferred additional criteria:

```text
1. fixed-point-ready spike/LIF implementation style
2. operation-count and memory-footprint analysis
3. report-quality figures and reproducible results
4. clear connection to prior SCM/HLS acceleration work
```

## 10. Repository Updates Completed

The following files were updated to align Phase 1 with the DOA engineering model while preserving the existing phase structure:

```text
phase_01_python_prototype/README.md
phase_01_python_prototype/PROPOSAL.md
phase_01_python_prototype/DESIGN_NOTES.md
phase_01_python_prototype/EXPERIMENTS.md
docs/tasks_phase_01.md
docs/handoffs/handoff_003_scope_upgrade_to_doa_hardware.md
```

The main course proposal had already been revised earlier:

```text
docs/project_proposal/course_project_proposal.md
```

No code files were changed in this update.

## 11. Immediate Next Actions

1. Pull the updated repository locally.
2. Review the updated Phase 1 files.
3. Implement the ULA steering-vector function.
4. Implement snapshot generation.
5. Implement covariance and beamspace feature extraction.
6. Implement the spike encoder.
7. Implement the LIF-inspired classifier.
8. Run the first DOA-based Phase 1 experiment.
9. Create Handoff 004 after Run 001 results.

## 12. Resume Point for Next Chat

Continue from Handoff 003. The phase structure is preserved. Phase 1 remains the Python prototype phase, but its implementation is now based on a physics-based ULA/DOA model, covariance or beamspace features, spike encoding, LIF-inspired DOA-sector inference, and baseline comparison. The next task is to implement the Python ULA/DOA reference model.
