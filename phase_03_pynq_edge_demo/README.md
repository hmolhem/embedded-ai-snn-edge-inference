# Phase 3 — PYNQ Edge Demo

## Objective

Demonstrate the spike-based inference workflow on an embedded edge platform using PYNQ.

## Recommended Development Levels

### Phase 3A — ARM-Side Python Demo

Run the Python inference workflow on the PYNQ processor side. This validates the embedded deployment path without requiring immediate FPGA-fabric implementation.

### Phase 3B — FPGA-Fabric Kernel Extension

Move one small kernel into FPGA fabric after the Python workflow is stable.

Candidate kernels:

- spike encoder
- LIF neuron update
- fixed-point threshold/reset logic

## Non-Goals

This phase should not attempt to move the full radar pipeline, full SNN, or full MUSIC/DOA algorithm into FPGA fabric.

## Planned Outputs

- deployment notes
- PYNQ setup notes
- timing observations
- optional hardware/kernel experiment
