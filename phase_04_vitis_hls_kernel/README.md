# Phase 4 — AMD Vitis HLS Kernel

## Objective

Implement a small hardware-friendly spike-processing kernel in AMD Vitis HLS.

## Candidate Kernels

- rate-based spike encoder
- LIF neuron-array update
- fixed-point accumulation and thresholding

## Expected Outputs

- HLS C++ source code
- testbench
- C simulation result
- synthesis report
- latency estimate
- initiation interval estimate
- resource utilization: LUT, FF, DSP, BRAM

## Design Principle

This phase should focus on one small kernel rather than the complete sensing or classification pipeline.
