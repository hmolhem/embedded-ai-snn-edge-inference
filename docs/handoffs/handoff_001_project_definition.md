# Handoff 001 — Project Definition and Repository Plan

## 1. Context

This handoff summarizes the initial definition of the end-of-course project for EE 6900 Edge AI for Robotics / Embedded AI. The project is intended to be small enough for a course deliverable, but structured so that it can grow into a portfolio project, PYNQ/Vitis HLS implementation, and possible research-paper direction.

The strategic objective is to connect edge AI, spike-based inference, neuromorphic concepts, embedded sensing, and future FPGA-ready implementation without overclaiming in the initial course submission.

## 2. Core Decision

The project will start conservatively as a software-level prototype:

> Lightweight Spike-Based Edge Inference for Embedded Sensing

The deeper internal research direction is:

> FPGA-Ready Spike-Encoded DOA Sector Classification for Edge Robotic Sensing

The public/course-facing version should avoid premature claims about DOA, MIMO radar, FPGA acceleration, or publishable novelty until results justify those claims.

## 3. Project Philosophy

The project should follow this engineering strategy:

```text
Start small.
Design clean.
Measure carefully.
Document professionally.
Extend strategically.
```

The first deliverable should be technically defensible and easy to explain. Later phases can add radar/DOA features, PYNQ execution, Vitis HLS kernels, and paper-level comparisons.

## 4. Phase 1 — Minimal Python Prototype

### Goal

Develop a small Python prototype that demonstrates spike-based edge inference on a simulated sensing dataset.

### Scope

The first version should include:

- simulated sensing dataset
- feature normalization
- rate-based or spike-like encoding
- lightweight LIF-inspired classifier
- classification accuracy
- confusion matrix
- average spike count
- latency measured in time steps

### Exclusions

Phase 1 should not attempt:

- full neuromorphic hardware
- full robotic autonomy stack
- ROS / Gazebo / Isaac Sim dependency
- full radar processor
- full MUSIC implementation
- FPGA implementation
- publishable novelty claim

### Expected Deliverables

- Python source code
- clean README
- figures
- results tables
- short technical report section
- handoff after implementation

## 5. Phase 2 — Radar / DOA Sensing Case Study

### Goal

Connect the Phase 1 spike-based inference framework to radar/array-processing features.

### Possible Pipeline

```text
ULA / MIMO radar simulation
    ↓
Sample covariance matrix or beamspace features
    ↓
Feature normalization
    ↓
Spike encoding
    ↓
Small LIF-inspired classifier
    ↓
DOA sector label
```

### Possible Classes

Example DOA-sector labels:

```text
Class 1: -60° to -30°
Class 2: -30° to   0°
Class 3:   0° to  30°
Class 4:  30° to  60°
```

### Strategic Note

This phase is important for portfolio and paper development, but it should not be exposed prematurely if collaboration/ownership concerns arise.

## 6. Phase 3 — PYNQ Edge Demo

### Goal

Show that the inference path can be connected to an embedded edge device.

### Recommended Levels

```text
PYNQ Phase A: Run Python inference on the ARM processor side.
PYNQ Phase B: Move one small kernel to FPGA fabric.
```

### Candidate FPGA Kernels

- spike encoder
- LIF neuron update
- fixed-point spike accumulation

### Exclusions

Do not attempt full DOA processing, full MUSIC, or a complete SNN accelerator on FPGA at this stage.

## 7. Phase 4 — AMD Vitis HLS Kernel

### Goal

Implement and synthesize a small hardware-friendly kernel using AMD Vitis HLS.

### Candidate Kernels

- rate-based spike encoder
- LIF neuron-array update
- fixed-point thresholding / reset logic

### Expected Outputs

- C++ HLS source
- testbench
- C simulation output
- synthesis report
- latency estimate
- resource estimate: LUT, FF, DSP, BRAM

## 8. Paper / Portfolio Path

The paper-level question should not be simply whether an SNN works. It should be framed as hardware-aware inference:

> Can spike-encoded sensing features support low-power edge classification with favorable accuracy, spike count, operation count, and memory footprint?

For a stronger paper direction, compare:

- classical lightweight classifier
- small DNN baseline
- SNN-inspired classifier

Possible metrics:

- accuracy
- confusion matrix
- robustness versus SNR or noise level
- spike count
- time steps
- operation count
- memory footprint
- hardware-mapping complexity

## 9. GitHub Strategy

Use one private repository initially:

```text
hmolhem/embedded-ai-snn-edge-inference
```

Recommended structure:

```text
embedded-ai-snn-edge-inference/
├── README.md
├── docs/
│   ├── handoffs/
│   ├── project_proposal/
│   ├── literature_notes/
│   └── reports/
├── phase_01_python_prototype/
│   ├── src/
│   ├── notebooks/
│   ├── figures/
│   └── results/
├── phase_02_radar_sensing_case_study/
│   ├── src/
│   ├── data/
│   ├── figures/
│   └── results/
├── phase_03_pynq_edge_demo/
│   ├── src/
│   ├── deployment_notes/
│   └── figures/
├── phase_04_vitis_hls_kernel/
│   ├── hls_src/
│   ├── testbench/
│   └── synthesis_reports/
└── paper/
    ├── latex/
    ├── figures/
    └── references/
```

## 10. Immediate Next Actions

1. Build the repository skeleton.
2. Create Phase 1 README.
3. Define the Phase 1 simulated dataset.
4. Define the feature vector.
5. Implement spike encoding.
6. Implement a simple LIF-inspired classifier.
7. Generate accuracy and confusion matrix.
8. Generate spike-count and latency plots.
9. Write Handoff 002 after Phase 1 design is frozen.

## 11. Key Risk-Control Rules

- Keep the course-facing version modest and defensible.
- Do not overclaim novelty before results exist.
- Do not expose the full DOA/MIMO/FPGA research direction prematurely.
- Share only the minimal educational version if collaboration becomes required.
- Keep deeper extensions in private/internal development until ready.

## 12. Current Status

- Presentation video for the paper review has been submitted.
- Conservative paper-review version has been prepared.
- End-of-course project planning has started.
- GitHub repository has been created.
- This is the first formal project handoff.
