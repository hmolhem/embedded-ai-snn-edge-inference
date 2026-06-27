# Phase 3 Proposal — PYNQ Edge Demo

## 1. Title

**PYNQ-Based Edge Demonstration of Spike-Based Inference**

## 2. Motivation

Phases 1 and 2 focus on software-level development and sensing-oriented evaluation. Phase 3 begins the transition from a desktop Python prototype to an embedded edge-device workflow.

PYNQ provides a practical platform for demonstrating edge deployment because it combines a processor system with programmable FPGA fabric. The first goal is not to build a complete accelerator. The first goal is to show that the inference workflow can run on an embedded platform and to identify which computation blocks are good candidates for later hardware acceleration.

## 3. Problem Statement

The problem is to evaluate how the Phase 1 or Phase 2 inference workflow can be executed on a PYNQ platform in a controlled and incremental way.

The phase should answer two practical questions:

1. Can the Python inference workflow run on the PYNQ processor side?
2. Which small kernel is the best candidate for future FPGA-fabric implementation?

## 4. Objective

Demonstrate embedded execution of the spike-based inference workflow on PYNQ, starting with ARM-side Python execution and leaving FPGA-fabric acceleration as a limited extension.

## 5. Technical Scope

### Included

- PYNQ environment setup notes
- Python inference execution on the ARM processor side
- timing observations
- memory and runtime discussion
- identification of a candidate FPGA kernel
- optional small hardware-fabric experiment if time permits

### Excluded

- full FPGA implementation of the entire pipeline
- full radar processor on FPGA
- full SNN accelerator
- real-time robotics integration
- ROS integration
- hardware novelty claim

## 6. Methodology

The Phase 1 or Phase 2 Python code will be transferred to the PYNQ environment. The workflow will first be executed on the ARM processor side. Runtime, memory behavior, and practical deployment issues will be documented.

After the processor-side execution is verified, the project will identify one small computation block for possible FPGA-fabric acceleration. Candidate blocks include:

- spike encoder,
- LIF neuron update,
- fixed-point threshold and reset logic.

The preferred implementation strategy is incremental:

```text
Desktop Python result
    ↓
PYNQ ARM-side Python execution
    ↓
Candidate kernel identification
    ↓
Optional FPGA-fabric kernel experiment
```

## 7. Expected Deliverables

- PYNQ setup notes
- deployment instructions
- ARM-side execution result
- timing observations
- screenshots or figures
- candidate-kernel analysis
- updated deployment notes

## 8. Evaluation Metrics

Minimum metrics:

- successful execution on PYNQ
- runtime observation
- memory or resource discussion
- comparison with desktop Python result

Optional metrics:

- timing for spike encoding
- timing for LIF update
- rough speed comparison
- notes for later HLS acceleration

## 9. Risks and Limitations

The main risk is spending too much time on board setup, environment problems, or hardware integration before the core algorithm is stable. Therefore, this phase should only begin after Phase 1 is working and Phase 2 is either complete or clearly scoped.

A second risk is attempting to accelerate too much. The FPGA-fabric part should be limited to one small kernel, not the complete inference workflow.

## 10. Future Extension

A successful PYNQ demonstration can support:

- a stronger embedded-AI portfolio artifact,
- migration of one kernel to Vitis HLS,
- hardware-aware comparison of software and hardware execution,
- future edge-sensing demo for industry or research presentation.
