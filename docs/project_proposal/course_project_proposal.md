# Course Project Proposal

## Title

**Spike-Based Edge Inference for Physics-Based DOA Sector Estimation**

## Student

Hossein Molhem  
Department of Electrical and Computer Engineering  
Kennesaw State University  
EE 6900 Edge AI for Robotics

## 1. Project Motivation

Edge-AI systems for autonomous and robotic sensing often need to estimate the direction of relevant signals under constraints on power, latency, memory, and communication bandwidth. Direction-of-arrival (DOA) estimation is an important sensing primitive in radar, wireless sensing, acoustic sensing, and array-based perception. In many embedded or robotic systems, a coarse directional decision may be sufficient for navigation, tracking, alerting, or sensor steering, even when a full high-resolution DOA estimate is computationally expensive.

Spiking neural networks and spike-inspired inference models provide a hardware-friendly framework for sparse temporal computation. Instead of processing dense activations continuously, spike-based systems represent information through event activity over time. This project investigates whether physically generated array-sensing data can be converted into spike representations and used for lightweight DOA sector inference suitable for future FPGA or edge-chip implementation.

## 2. Problem Statement

The project addresses the following problem:

> Can physics-based array-sensing data be used to generate spike-encoded features for lightweight edge inference of DOA sectors, and can the resulting inference pipeline be prepared for hardware implementation?

The goal is not to claim a complete neuromorphic radar processor. The goal is to build a defensible engineering prototype that connects array-signal modeling, spike encoding, LIF-inspired inference, and hardware-aware implementation.

## 3. Project Objective

The main objective is to implement and evaluate an end-to-end DOA-sector inference workflow with the following stages:

1. generate array-sensing data from a physical DOA model,
2. extract compact features from the received array data,
3. normalize and encode the features into spike trains,
4. classify the DOA sector using a lightweight LIF-inspired classifier,
5. evaluate accuracy, confusion matrix, spike activity, latency proxy, and hardware-relevant complexity,
6. prepare a hardware-facing implementation path for PYNQ/Zynq or FPGA-based edge deployment.

## 4. Technical Scope

### Included in the Project

- uniform linear array (ULA) signal model,
- physics-based synthetic DOA dataset,
- single-source narrowband signal model,
- additive complex Gaussian noise,
- SNR-controlled data generation,
- DOA-sector labels,
- compact feature extraction from array snapshots or covariance-derived quantities,
- rate-based spike encoding,
- LIF-inspired edge classifier,
- classical baseline comparison,
- accuracy versus SNR,
- confusion matrices,
- spike-count and latency-proxy analysis,
- hardware-aware discussion,
- optional PYNQ/Zynq or Vitis HLS kernel preparation.

### Controlled Initial Assumptions

The first implementation will use a controlled model:

```text
Number of array elements: 8
Array type: Uniform Linear Array
Element spacing: lambda / 2
Signal model: single narrowband source
Snapshots per sample: M
Noise model: additive complex Gaussian noise
DOA range: -60 degrees to +60 degrees
Task: classify coarse DOA sector
```

Initial DOA sectors:

```text
Class 0: -60 deg to -30 deg
Class 1: -30 deg to   0 deg
Class 2:   0 deg to  30 deg
Class 3:  30 deg to  60 deg
```

### Not Included in the First Required Deliverable

- full multi-source high-resolution DOA estimation,
- full MUSIC or ESPRIT hardware implementation,
- ASIC-level neuromorphic-chip design,
- complete robotic autonomy stack,
- mandatory ROS, Gazebo, Isaac Sim, or Habitat integration,
- complete FPGA accelerator for the full signal-processing chain.

These items may be discussed as future work or implemented partially if time permits.

## 5. Physical Data-Generation Model

The dataset will be generated from a narrowband array-processing model. For a single source arriving from angle theta, the received array snapshot is modeled as

```text
x[m] = a(theta) s[m] + n[m]
```

where

```text
x[m]      : received array vector at snapshot m
a(theta) : steering vector of the ULA
s[m]      : complex source signal
n[m]      : complex Gaussian noise
m         : snapshot index
```

For a ULA with half-wavelength spacing, the steering vector can be written as

```text
a_n(theta) = exp(-j 2 pi d n sin(theta) / lambda)
```

where `n` is the array-element index and `d = lambda/2`.

For each simulated sample:

1. randomly select a DOA angle from the desired angular range,
2. assign the angle to a coarse DOA sector,
3. generate source snapshots,
4. generate additive complex Gaussian noise at a specified SNR,
5. form the received array snapshots,
6. compute compact features for spike-based inference.

## 6. Feature Extraction

The initial feature set will be intentionally compact and hardware-friendly. Candidate features include:

- diagonal power features from the sample covariance matrix,
- magnitudes of selected off-diagonal covariance entries,
- real and imaginary parts of selected covariance terms,
- beamspace energy features over a small number of steering directions.

The sample covariance matrix is

```text
R_xx = (1/M) sum_m x[m] x[m]^H
```

The first baseline will use a compact feature vector rather than the full covariance matrix. This keeps the computation suitable for edge hardware and allows the project to focus on spike encoding and lightweight inference.

## 7. Spike Encoding

The compact feature vector will be normalized to the range `[0, 1]`. Each normalized feature will then be converted into a spike train using rate-based encoding:

```text
P(spike_k[t] = 1) = feature_k
```

where `k` indexes the feature and `t` indexes the discrete time step.

Initial parameter:

```text
num_time_steps = 20
```

The spike tensor will have the form:

```text
num_samples x num_time_steps x num_features
```

## 8. LIF-Inspired Edge Classifier

The first classifier will be a lightweight leaky-integrate-and-fire inspired class accumulator. Spike trains will be integrated into class-level membrane states. A leak factor will be applied over time, and the predicted class will be selected using the largest final membrane potential.

First decision rule:

```text
Predicted class = argmax(final membrane potential)
```

This classifier is selected because it is interpretable, simple to implement, and suitable for later fixed-point or hardware-oriented implementation.

## 9. Baseline Comparison

The spike-based inference method will be compared against at least one non-spiking baseline. Candidate baselines include:

- nearest-centroid classifier,
- logistic regression,
- small multilayer perceptron,
- classical beam-scanning sector decision.

The baseline comparison is important because the project should evaluate the spike-based method against a conventional alternative rather than only demonstrate spike generation.

## 10. Evaluation Metrics

The project will report:

- classification accuracy,
- confusion matrix,
- accuracy versus SNR,
- average spike count per sample,
- latency proxy in time steps,
- feature-vector dimension,
- rough operation-count estimate,
- memory-footprint estimate,
- hardware-facing discussion of implementation cost.

## 11. Hardware Implementation Path

The intended hardware path is staged.

### Stage 1: Python Reference Model

A complete Python model will generate the DOA dataset, extract features, encode spikes, perform inference, and report metrics.

### Stage 2: Hardware-Friendly Refactoring

The spike encoder and LIF update will be rewritten in a form suitable for fixed-point arithmetic and loop-based hardware implementation.

### Stage 3: PYNQ/Zynq or FPGA-Facing Demonstration

A minimal hardware-facing demonstration may implement one or more of the following:

- spike encoding kernel,
- LIF update kernel,
- fixed-point class accumulator,
- DOA-sector inference on precomputed features.

The practical course target is a hardware-facing DOA-sector inference pipeline. Full continuous-angle DOA estimation on FPGA is a research extension and may be discussed as future work unless sufficient time and hardware access are available.

## 12. Expected Deliverables

Expected deliverables include:

- Python source code for DOA data generation,
- feature extraction module,
- spike-encoding module,
- LIF-inspired inference module,
- baseline comparison module,
- accuracy-versus-SNR results,
- confusion matrices,
- spike-count and latency analysis,
- hardware-aware discussion,
- project proposal,
- final report,
- GitHub documentation,
- handoff/checkpoint documents.

Expected repository locations:

```text
phase_01_python_prototype/src/
phase_01_python_prototype/results/
phase_01_python_prototype/figures/
phase_02_radar_sensing_case_study/src/
phase_02_radar_sensing_case_study/results/
phase_02_radar_sensing_case_study/figures/
docs/reports/
docs/handoffs/
```

## 13. Success Criteria

The minimum success criteria are:

1. physics-based ULA/DOA dataset generation works correctly,
2. DOA-sector labels are generated from physical angles,
3. compact features are extracted from array data,
4. spike encoding is implemented and measured,
5. LIF-inspired classifier produces meaningful sector classification,
6. at least one baseline comparison is included,
7. accuracy versus SNR is reported,
8. hardware-facing implementation path is documented.

The preferred success criterion is to produce a working edge-inference prototype whose core spike-encoding and LIF-inference steps are suitable for PYNQ/Zynq or FPGA-oriented implementation.

## 14. Risks and Limitations

The main technical risk is scope control. A full DOA estimator, full SNN training workflow, and full FPGA accelerator are each substantial projects. The project will therefore focus on a controlled DOA-sector inference problem and a hardware-friendly spike-based inference pipeline.

Another risk is overcomplicating the first implementation. The first version will use a single-source ULA model and coarse sector labels. More advanced cases such as multiple sources, high-resolution continuous-angle estimation, or full MUSIC/ESPRIT acceleration will be treated as extensions.

## 15. Future Work

Possible future extensions include:

1. continuous-angle DOA estimation instead of sector classification,
2. multi-source DOA cases,
3. MUSIC or ESPRIT comparison,
4. covariance-matrix acceleration using HLS,
5. PYNQ deployment with fixed-point spike/LIF kernels,
6. integration with prior FPGA acceleration work,
7. paper-oriented hardware-aware spike-based DOA inference.

## 16. Project Management Plan

The project will be developed in a staged GitHub repository. Each major design decision, technical result, risk, and phase transition will be documented using Markdown handoff files.

Current repository:

```text
hmolhem/embedded-ai-snn-edge-inference
```

Current local path:

```text
C:\MyDocument\embedded-ai-snn-edge-inference
```

The immediate next step is to implement the physics-based DOA data-generation model and then build the spike-based inference pipeline on top of it.
