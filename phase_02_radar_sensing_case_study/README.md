# Phase 2 — Radar / DOA Sensing Case Study

## Objective

Extend the minimal spike-based inference prototype toward radar and array-processing features.

This phase is the main technical bridge between embedded AI, DSP, MIMO radar, DOA estimation, and future FPGA-ready implementation.

## Candidate Pipeline

```text
ULA or MIMO radar simulation
    ↓
Sample covariance matrix or beamspace features
    ↓
Compact feature extraction
    ↓
Spike encoding
    ↓
LIF-inspired classifier
    ↓
DOA sector classification
```

## Candidate Labels

A conservative initial sector-classification problem may use four angular sectors:

```text
Class 1: -60° to -30°
Class 2: -30° to   0°
Class 3:   0° to  30°
Class 4:  30° to  60°
```

## Planned Metrics

- accuracy
- confusion matrix
- robustness versus SNR
- average spike count
- latency in time steps
- feature dimension
- approximate operation count
- memory footprint

## Strategic Note

This phase should remain private/internal until the implementation is technically mature. The course-facing project should stay broader and more conservative if collaboration or ownership concerns arise.
