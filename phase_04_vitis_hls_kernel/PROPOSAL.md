# Phase 4 Proposal — AMD Vitis HLS Kernel

## 1. Title

**Hardware-Friendly Spike-Processing Kernel Using AMD Vitis HLS**

## 2. Motivation

After the software and embedded demonstrations are stable, the next step is to investigate whether part of the spike-based inference workflow can be mapped into FPGA fabric. AMD Vitis HLS provides a practical path for expressing a small computation kernel in C/C++ and generating hardware implementation reports.

This phase is not intended to implement the complete application in hardware. The purpose is to identify and synthesize one small kernel that is representative of the computational structure of spike-based edge inference.

## 3. Problem Statement

The problem is to determine whether a small spike-processing operation can be expressed in a hardware-friendly form and synthesized with measurable latency and resource utilization.

The key engineering question is:

> Which part of the spike-based inference pipeline is simple, useful, and appropriate for FPGA acceleration?

## 4. Objective

Implement and synthesize one small Vitis HLS kernel related to the spike-based inference pipeline.

Candidate kernels include:

- rate-based spike encoder,
- LIF neuron-array update,
- fixed-point accumulation and thresholding,
- spike-count accumulation.

## 5. Technical Scope

### Included

- one HLS C++ kernel
- one C/C++ testbench
- C simulation
- synthesis report
- latency and initiation-interval analysis
- resource-utilization summary
- discussion of fixed-point suitability

### Excluded

- complete FPGA accelerator
- full SNN processor
- full radar/DOA pipeline
- AXI integration unless time allows
- PYNQ overlay generation unless a later extension is justified
- claim of optimized hardware architecture

## 6. Methodology

A single kernel will be selected after Phase 1 and Phase 2 identify the most useful computation block. The kernel will be rewritten in hardware-friendly C++ using fixed-size arrays and simple loops. The design will be tested using a C/C++ testbench and synthesized in AMD Vitis HLS.

The implementation will emphasize clarity and measurability over aggressive optimization. If time permits, basic HLS pragmas may be tested, such as loop pipelining or array partitioning.

Candidate kernel pattern:

```text
for each time step:
    for each neuron:
        update membrane state
        compare with threshold
        emit spike or no spike
        apply reset if needed
```

## 7. Expected Deliverables

- HLS C++ source file
- header file if needed
- testbench
- C simulation output
- synthesis report
- latency summary
- resource-utilization table
- short discussion of hardware mapping

## 8. Evaluation Metrics

Minimum metrics:

- successful C simulation
- successful HLS synthesis
- latency estimate
- initiation interval if applicable
- LUT utilization
- FF utilization
- DSP utilization
- BRAM utilization

Optional metrics:

- comparison between floating-point and fixed-point versions
- effect of loop pipelining
- effect of array partitioning
- estimated throughput per time step

## 9. Risks and Limitations

The main risk is expanding the hardware scope too quickly. A full hardware implementation of the whole inference pipeline is not the goal. The phase should remain limited to one kernel.

Another limitation is that HLS synthesis results alone do not prove complete system performance. A complete embedded design would also require data movement, memory interfaces, and integration overhead. These should be discussed honestly.

## 10. Future Extension

A successful HLS kernel can support:

- PYNQ fabric integration,
- a hardware-aware portfolio artifact,
- comparison of software and hardware latency,
- paper-level analysis of spike-based inference mapped to edge hardware,
- future extension toward radar/DOA sensing kernels.
