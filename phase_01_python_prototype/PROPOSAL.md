# Phase 1 Proposal — Minimal Python Prototype

## 1. Title

**Lightweight Spike-Based Edge Inference for Embedded Sensing**

## 2. Motivation

Edge-AI systems must often operate under strict limits on power, memory, latency, and compute resources. Conventional dense neural-network inference can be inefficient for always-on sensing tasks, especially when useful information is sparse or event-like. Spike-based inference provides a useful educational and engineering framework for studying sparse temporal computation without immediately requiring specialized neuromorphic hardware.

This phase establishes the minimal software foundation of the project. It is intentionally conservative and course-facing: the goal is to demonstrate the core idea clearly, not to claim a complete neuromorphic processor, a full robotic autonomy stack, or a new hardware architecture.

## 3. Problem Statement

The problem is to determine whether a simple spike-based inference workflow can classify a small simulated sensing dataset while producing edge-relevant metrics such as spike count and inference latency in time steps.

The emphasis is not only on classification accuracy. The project also asks how feature encoding, spike sparsity, and lightweight neuron dynamics affect the behavior of an edge-inference pipeline.

## 4. Objective

Build an end-to-end Python prototype that performs:

1. simulated sensing-data generation,
2. feature normalization,
3. spike-like encoding,
4. lightweight LIF-inspired classification,
5. metric and figure generation.

## 5. Technical Scope

### Included

- small simulated sensing dataset
- multi-class classification task
- normalized feature vector
- rate-based or simple temporal spike encoding
- lightweight LIF-inspired classifier
- accuracy calculation
- confusion matrix
- average spike count
- latency measured in time steps
- clean figures and result summaries

### Excluded

- full neuromorphic-chip design
- full robotic autonomy stack
- ROS, Gazebo, Isaac Sim, or Habitat dependency
- full radar/DOA/MIMO implementation
- PYNQ deployment
- Vitis HLS synthesis
- publication-level novelty claim

## 6. Methodology

The first implementation will use a simulated sensing dataset with several separable classes. Each sample will contain a compact feature vector. The features will be normalized into a bounded range and then converted into spike-like representations.

A small LIF-inspired classifier will accumulate spike activity over a fixed number of time steps. The predicted class will be selected from the output unit or class score with the strongest accumulated response.

The implementation should be modular:

```text
src/dataset.py          dataset generation
src/spike_encoding.py   spike encoding
src/lif.py              LIF-inspired classifier
src/metrics.py          metrics
src/plots.py            plotting
src/main.py             experiment runner
```

## 7. Expected Deliverables

- Python code under `src/`
- experiment runner
- dataset visualization
- confusion matrix figure
- spike-count summary
- latency summary
- result files under `results/`
- figures under `figures/`
- updated `DESIGN_NOTES.md`
- updated `EXPERIMENTS.md`
- Handoff 002 after the Phase 1 design is frozen

## 8. Evaluation Metrics

Minimum metrics:

- classification accuracy
- confusion matrix
- average spike count per sample
- average latency in time steps

Optional metrics:

- spike-count distribution by class
- accuracy versus number of time steps
- accuracy versus noise level
- simple operation-count estimate

## 9. Risks and Limitations

The main risk is making the simulated dataset either too easy or too artificial. A very easy dataset may produce high accuracy but weak engineering value. A very difficult dataset may obscure the spike-inference demonstration. The dataset should therefore be simple but not trivial.

Another limitation is that this phase uses a software-level LIF-inspired model. It should not be presented as a hardware implementation. Hardware mapping is reserved for later phases.

## 10. Future Extension

After Phase 1 is stable, the same software architecture can be extended toward:

- radar/array-sensing case study,
- DOA-sector classification,
- PYNQ ARM-side execution,
- Vitis HLS implementation of one small kernel,
- paper-level comparison with lightweight DNN or classical baselines.
