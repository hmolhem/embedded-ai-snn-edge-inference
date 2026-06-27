# Handoff 002 — Phase Proposal Review and Phase-1 Design Freeze Preparation

## 1. Context

This handoff records the project status after creating and reviewing the phase-level proposals for the repository:

```text
hmolhem/embedded-ai-snn-edge-inference
```

The user reviewed the phase proposals and approved the overall direction. The next step is to freeze the detailed Phase 1 design and begin implementation.

The project remains intentionally staged:

```text
Phase 1: Minimal Python prototype
Phase 2: Radar / DOA sensing case study
Phase 3: PYNQ edge demo
Phase 4: AMD Vitis HLS kernel
Paper track: future research extension
```

## 2. Repository State

The repository now contains separate `PROPOSAL.md` files for each phase:

```text
phase_01_python_prototype/PROPOSAL.md
phase_02_radar_sensing_case_study/PROPOSAL.md
phase_03_pynq_edge_demo/PROPOSAL.md
phase_04_vitis_hls_kernel/PROPOSAL.md
```

An index file was also added:

```text
docs/project_proposal/phase_proposal_index.md
```

The purpose of these files is to keep each phase scoped independently. This prevents the course deliverable from expanding too quickly while preserving a clear roadmap toward portfolio, hardware, and paper development.

## 3. Key Decision

The major decision is to keep Phase 1 as the official course-facing foundation:

> Lightweight Spike-Based Edge Inference for Embedded Sensing

This phase is intentionally conservative. It avoids premature claims about radar, DOA, MIMO, FPGA acceleration, or publishable novelty.

The deeper long-term direction remains available internally:

> FPGA-Ready Spike-Encoded DOA Sector Classification for Edge Robotic Sensing

That deeper direction will be developed only after the Phase 1 prototype produces stable results.

## 4. Approved Phase Proposal Strategy

Each phase now follows the same proposal structure:

```text
1. Title
2. Motivation
3. Problem Statement
4. Objective
5. Technical Scope
6. Methodology
7. Expected Deliverables
8. Evaluation Metrics
9. Risks and Limitations
10. Future Extension
```

This structure is useful because it separates:

- motivation from implementation,
- current deliverables from future extensions,
- course-facing work from research-facing work,
- safe public language from more specialized private directions.

## 5. Phase 1 Summary

### Title

**Lightweight Spike-Based Edge Inference for Embedded Sensing**

### Role

Phase 1 is the minimum viable course project and the foundation for all later phases.

### Objective

Build an end-to-end Python prototype that performs:

1. simulated sensing-data generation,
2. feature normalization,
3. spike-like encoding,
4. lightweight LIF-inspired classification,
5. metric and figure generation.

### Included

- small simulated sensing dataset
- multi-class classification
- normalized feature vector
- spike encoding
- LIF-inspired classifier
- accuracy
- confusion matrix
- average spike count
- latency in time steps
- result figures

### Excluded

- full neuromorphic-chip design
- full robotic autonomy stack
- robotics simulator dependency
- full radar/DOA/MIMO implementation
- PYNQ deployment
- Vitis HLS synthesis
- publication-level novelty claim

## 6. Phase 2 Summary

### Title

**Spike-Encoded Sensing Features for Direction-Sector Classification**

### Role

Phase 2 is the first technical bridge from generic embedded sensing to the user’s deeper DSP/radar/DOA direction.

### Scope

A controlled radar/array-sensing case study may include:

- ULA or simplified MIMO/array simulation,
- coarse direction-sector labels,
- compact feature extraction,
- spike encoding,
- LIF-inspired classification,
- accuracy versus SNR or noise.

### Strategic Control

Phase 2 should not be exposed prematurely as a full DOA/MIMO/FPGA research claim. The course-facing language can remain general while the deeper research path stays internal until strong results exist.

## 7. Phase 3 Summary

### Title

**PYNQ-Based Edge Demonstration of Spike-Based Inference**

### Role

Phase 3 moves the software workflow toward embedded deployment.

### Incremental Plan

```text
Desktop Python result
    ↓
PYNQ ARM-side Python execution
    ↓
Candidate kernel identification
    ↓
Optional FPGA-fabric kernel experiment
```

### Risk Control

Do not attempt to move the complete inference pipeline, full SNN, full radar chain, or full DOA algorithm into FPGA fabric during this phase.

## 8. Phase 4 Summary

### Title

**Hardware-Friendly Spike-Processing Kernel Using AMD Vitis HLS**

### Role

Phase 4 explores one small hardware-friendly kernel after software results are stable.

### Candidate Kernels

- rate-based spike encoder
- LIF neuron-array update
- fixed-point accumulation and thresholding
- spike-count accumulation

### Expected Outputs

- HLS C++ source
- testbench
- C simulation
- synthesis report
- latency estimate
- resource-utilization summary

## 9. Current Technical Position

The repository has a clean staged structure and proposal documentation, but Phase 1 implementation has not yet started.

Current Phase 1 source scaffold:

```text
phase_01_python_prototype/
├── PROPOSAL.md
├── README.md
├── DESIGN_NOTES.md
├── EXPERIMENTS.md
├── config.yaml
├── requirements.txt
├── run_phase_01.py
└── src/
    ├── __init__.py
    ├── main.py
    ├── dataset.py
    ├── spike_encoding.py
    ├── lif.py
    ├── metrics.py
    └── plots.py
```

The next step is not coding immediately. The next step is to freeze the Phase 1 design.

## 10. Phase 1 Design Decisions Still Needed

Before implementation, the following must be defined:

1. Dataset type
2. Number of classes
3. Number of features
4. Noise level or class overlap
5. Train/test split method
6. Spike-encoding method
7. Number of time steps
8. LIF-inspired classifier structure
9. Decision rule
10. Metrics
11. Figures
12. File outputs

## 11. Recommended Phase 1 Design Direction

The recommended first design is a small synthetic sensing dataset with four classes and eight features.

### Candidate Dataset

Use a simulated embedded-sensing dataset where each class has a different feature signature. This can represent a generic sensing system without exposing radar/DOA details.

Example interpretation:

```text
Class 0: low-left response pattern
Class 1: low-right response pattern
Class 2: high-left response pattern
Class 3: high-right response pattern
```

or more generally:

```text
Class 0: sensing state A
Class 1: sensing state B
Class 2: sensing state C
Class 3: sensing state D
```

### Candidate Parameters

```text
num_samples      = 1000
num_classes      = 4
num_features     = 8
num_time_steps   = 20
random_seed      = 42
```

These values already match the initial `config.yaml` scaffold.

## 12. Recommended Spike Encoding

Start with rate-based encoding because it is simple, explainable, and hardware-friendly.

Method:

1. Normalize each feature into the interval [0, 1].
2. Interpret each normalized feature as a spike probability.
3. Generate binary spikes over `T` time steps.
4. Higher feature values produce higher spike rates.

This is not biologically complete, but it is sufficient for a minimal edge-inference demonstration.

## 13. Recommended Classifier

Start with a lightweight LIF-inspired class accumulator.

Concept:

```text
Input spike trains
    ↓
Weighted accumulation into class membrane states
    ↓
Leak factor
    ↓
Threshold or final membrane comparison
    ↓
Predicted class
```

Decision rule options:

1. class with largest final membrane potential,
2. class with largest number of output spikes,
3. class with earliest threshold crossing.

Recommended first decision rule:

> predict the class with the largest final membrane potential.

This is simple and stable for the first baseline.

## 14. Recommended Metrics

Minimum metrics for Run 001:

- accuracy
- confusion matrix
- average spike count per sample
- average latency in time steps

Recommended plots:

- dataset feature visualization
- confusion matrix
- spike-count distribution
- accuracy versus number of time steps

Optional later plots:

- accuracy versus noise level
- average spike count versus time steps
- class-wise spike activity

## 15. Implementation Plan

### Step 1 — Dataset Generator

Implement `src/dataset.py`:

- generate synthetic class centers,
- add Gaussian noise,
- return features and labels,
- normalize features.

### Step 2 — Spike Encoding

Implement `src/spike_encoding.py`:

- rate_encode(features, num_time_steps, random_seed),
- return binary spike tensor.

Expected tensor shape:

```text
num_samples × num_time_steps × num_features
```

### Step 3 — LIF Classifier

Implement `src/lif.py`:

- define class weights,
- update class membrane potentials over time,
- apply leak,
- predict class.

### Step 4 — Metrics

Implement `src/metrics.py`:

- accuracy,
- confusion matrix,
- spike count,
- latency proxy.

### Step 5 — Plots

Implement `src/plots.py`:

- save confusion matrix figure,
- save spike-count histogram,
- save dataset visualization,
- save accuracy/time-step plot if included.

### Step 6 — Main Runner

Implement `src/main.py` and `run_phase_01.py`:

- run full experiment,
- save figures,
- save metrics summary,
- print concise report to console.

## 16. Success Criteria for Run 001

Run 001 is successful if it produces:

- a complete end-to-end execution,
- at least one saved metrics file,
- at least two saved figures,
- accuracy above random guessing,
- meaningful spike-count and latency values,
- clean enough results for a first report section.

For four classes, random guessing is about 25 percent. A reasonable first target is:

```text
accuracy > 75 percent
```

The goal is not to maximize accuracy yet. The goal is to demonstrate a functioning spike-based edge-inference pipeline.

## 17. Risk Controls

- Keep Phase 1 generic and modest.
- Do not mention radar/DOA as the official Phase 1 target.
- Do not claim hardware implementation in Phase 1.
- Do not optimize before baseline results exist.
- Prefer clear code and measurable outputs over complexity.
- Use deterministic random seeds for reproducibility.

## 18. GitHub Status

Updated files relevant to this handoff:

```text
phase_01_python_prototype/PROPOSAL.md
phase_02_radar_sensing_case_study/PROPOSAL.md
phase_03_pynq_edge_demo/PROPOSAL.md
phase_04_vitis_hls_kernel/PROPOSAL.md
docs/project_proposal/phase_proposal_index.md
docs/handoffs/handoff_002_pending_phase_01_design.md
```

## 19. Next Actions

1. Review this handoff.
2. Approve or modify the recommended Phase 1 design.
3. Update `phase_01_python_prototype/DESIGN_NOTES.md`.
4. Implement the first baseline code.
5. Run `Run 001`.
6. Save figures and metrics.
7. Create Handoff 003 after first implementation results.

## 20. Resume Point for a New Chat

If this project is continued in a new chat, provide this handoff and say:

> Continue from Handoff 002. The repository is initialized, all phase proposals are written, and the next task is to freeze and implement the Phase 1 minimal Python prototype.
