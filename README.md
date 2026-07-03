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
│   ├── results/
│   ├── INDEX.md
│   ├── EXPERIMENTS.md
│   └── REPORT_SECTION.md
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

### Phase 1 — Python DOA/SNN Reference Prototype

Status: completed as a reproducible Python reference prototype.

Phase 1 implements a physics-based DOA-sector inference workflow using a uniform linear array signal model, beamspace features, a nearest-centroid baseline, rate-based spike encoding, and a LIF-inspired temporal classifier.

Primary Phase 1 navigation files:

```text
phase_01_python_prototype/INDEX.md
phase_01_python_prototype/README.md
phase_01_python_prototype/EXPERIMENTS.md
phase_01_python_prototype/REPORT_SECTION.md
```

Key Phase 1 results:

```text
nearest-centroid baseline accuracy: 0.869048
fixed Run 003 LIF accuracy:         0.825000
best Run 005 LIF accuracy:          0.841667
best Run 005 configuration:         T=40, leak=0.99
lowest-latency Run 005 configuration: T=10, leak=0.99
```

### Phase 2 — Radar / DOA Sensing Case Study

Extend the prototype toward a richer radar/array-processing case study. Candidate extensions include multi-source DOA scenes, MUSIC or ESPRIT-style reference estimators, covariance-domain features, and more explicit comparison against classical signal-processing baselines.

### Phase 3 — PYNQ Edge Demo

Demonstrate the inference path on PYNQ as an edge-device workflow. The first target is Python execution on the ARM processor side. A later extension may move one small kernel, such as spike encoding or LIF update, into FPGA fabric.

### Phase 4 — Vitis HLS Kernel

Implement a small hardware-friendly kernel in AMD Vitis HLS. Candidate kernels include rate-based spike encoding, LIF neuron-array update, or fixed-point spike accumulation. The target outputs are C simulation, synthesis report, latency, and resource utilization.

### Paper / Portfolio Track

After the course deliverable is stable, the project can be expanded into a research prototype comparing classical lightweight models, small DNNs, and SNN-inspired inference under accuracy, spike-count, operation-count, memory-footprint, and hardware-suitability metrics.

## Current Status

- Repository initialized.
- Handoff protocol established.
- Phase 1 Python DOA/SNN prototype completed.
- Run 001 through Run 005 results generated and documented.
- Phase 1 report-ready narrative drafted.
- Next target: decide whether to extend Phase 1 into a final course report package or start a new Phase 2 branch.

## Handoff Protocol

Every major technical decision, result, scope change, or phase transition should be summarized in a Markdown handoff under:

```text
docs/handoffs/
```

Each handoff should be self-contained enough to restart the project in a new chat or work session.
