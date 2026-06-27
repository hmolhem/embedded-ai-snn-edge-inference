# Phase 1 — Minimal Python Prototype

## Objective

Build a minimal, defensible Python prototype for spike-based edge inference using a small simulated sensing dataset.

This phase is the course-facing foundation of the project. It should demonstrate the basic workflow without depending on robotics simulators, PYNQ, FPGA fabric, or full radar/DOA processing.

## Minimal Pipeline

```text
Simulated sensing dataset
    ↓
Feature normalization
    ↓
Spike encoding
    ↓
LIF-inspired classifier
    ↓
Class prediction
    ↓
Metrics and figures
```

## Initial Technical Tasks

1. Define a simple simulated sensing dataset.
2. Normalize features into a bounded range.
3. Encode normalized features into spike-like representations.
4. Implement a lightweight LIF-inspired classifier.
5. Evaluate classification accuracy.
6. Generate a confusion matrix.
7. Measure average spike count.
8. Measure latency in time steps.
9. Save all figures and results.

## Planned Outputs

- `src/` — Python implementation
- `notebooks/` — optional exploratory notebooks
- `figures/` — generated plots
- `results/` — metrics, CSV summaries, and run logs

## Success Criteria

Phase 1 is successful if it produces a complete end-to-end result with clear figures and defensible metrics, even if the dataset is simple.

## Non-Goals

This phase does not attempt:

- full robotic autonomy
- full neuromorphic chip design
- PYNQ deployment
- Vitis HLS synthesis
- full radar/DOA implementation
- publication-level novelty claim
