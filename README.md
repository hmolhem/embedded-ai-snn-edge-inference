# Embedded AI SNN Edge Inference

Lightweight spike-based edge inference prototypes for embedded sensing, robotic perception, and future FPGA/PYNQ deployment.

## Project Vision

This repository is organized as a staged research and engineering program around **hardware-aware edge AI**. The immediate course-facing goal is intentionally modest: build a small, defensible software prototype that demonstrates spike-based edge inference on simulated sensing data. The longer-term goal is to develop this work into a portfolio-quality and potentially paper-worthy path connecting embedded sensing, neuromorphic computing, radar/array features, PYNQ, and AMD Vitis HLS.

## Working Titles

**Course-facing title:**

> Lightweight Spike-Based Edge Inference for Embedded Sensing

**Internal research/portfolio direction:**

> FPGA-Ready Spike-Encoded DOA Sector Classification for Edge Robotic Sensing

The public/course-facing language should remain conservative until the technical results are strong enough to justify a more specialized research claim.

## Repository Structure

```text
embedded-ai-snn-edge-inference/
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

## Phase Roadmap

### Phase 1 — Minimal Python Prototype

Build a small Python-based spike-inference demonstration using simulated sensing data. The minimum deliverables are a dataset generator, feature normalization, spike encoding, a lightweight LIF-inspired classifier, accuracy metrics, a confusion matrix, spike-count statistics, and latency in time steps.

### Phase 2 — Radar / DOA Sensing Case Study

Extend the prototype to radar/array-processing features such as covariance-derived features, beamspace energies, or direction-sector labels. This phase is the technical bridge to prior DSP, MIMO radar, DOA estimation, and FPGA-related work.

### Phase 3 — PYNQ Edge Demo

Demonstrate the inference path on PYNQ as an edge-device workflow. The first target is Python execution on the ARM processor side. A later extension may move one small kernel, such as spike encoding or LIF update, into FPGA fabric.

### Phase 4 — Vitis HLS Kernel

Implement a small hardware-friendly kernel in AMD Vitis HLS. Candidate kernels include rate-based spike encoding, LIF neuron-array update, or fixed-point spike accumulation. The target outputs are C simulation, synthesis report, latency, and resource utilization.

### Paper / Portfolio Track

After the course deliverable is stable, the project can be expanded into a research prototype comparing classical lightweight models, small DNNs, and SNN-inspired inference under accuracy, spike-count, operation-count, memory-footprint, and hardware-suitability metrics.

## Current Status

- Repository initialized.
- Handoff protocol established.
- Phase 1 project scope defined.
- Next target: implement the minimal Python prototype.

## Handoff Protocol

Every major technical decision, result, scope change, or phase transition should be summarized in a Markdown handoff under:

```text
docs/handoffs/
```

Each handoff should be self-contained enough to restart the project in a new chat or work session.
