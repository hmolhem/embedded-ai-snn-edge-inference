# Course Project Proposal

## Title

**Lightweight Spike-Based Edge Inference for Embedded Sensing**

## Student

Hossein Molhem  
Department of Electrical and Computer Engineering  
Kennesaw State University  
EE 6900 Edge AI for Robotics

## 1. Project Motivation

Edge-AI systems are increasingly used in embedded and robotic applications where computation must be performed close to the sensor. These systems often operate under strict constraints on power consumption, memory footprint, latency, and communication bandwidth. Conventional dense neural-network inference can be effective, but it may be inefficient for always-on sensing tasks when the useful information is sparse, temporal, or event-like.

Spiking neural networks and spike-inspired inference models provide a useful framework for exploring sparse temporal computation. Instead of processing dense activations at every step, spike-based systems can represent information through event activity over time. This makes them relevant to embedded sensing and neuromorphic edge-AI systems.

This project proposes a modest, software-level prototype to study the basic behavior of spike-based edge inference. The goal is not to design a complete neuromorphic processor or a full robotic autonomy system. The goal is to build a clean, measurable, and defensible prototype that demonstrates spike encoding, lightweight LIF-inspired inference, and edge-relevant metrics.

## 2. Problem Statement

The project investigates whether a compact spike-based inference workflow can classify a small simulated sensing dataset while producing useful edge-AI metrics such as classification accuracy, spike count, and inference latency in time steps.

The central problem is:

> Can normalized sensing features be converted into spike-like temporal representations and classified using a lightweight LIF-inspired model in a way that is simple, interpretable, and suitable for future embedded implementation?

## 3. Project Objective

The objective is to implement an end-to-end Python prototype with the following stages:

1. generate a small simulated sensing dataset,
2. normalize feature vectors,
3. convert normalized features into spike-like representations,
4. classify samples using a lightweight LIF-inspired model,
5. evaluate performance using accuracy, confusion matrix, spike count, and latency proxy.

## 4. Technical Scope

### Included in the Project

- simulated embedded-sensing dataset
- four-class classification problem
- eight-dimensional feature vector
- rate-based spike encoding
- lightweight LIF-inspired classifier
- accuracy evaluation
- confusion matrix
- average spike count per sample
- latency proxy in time steps
- result figures and metrics summary
- discussion of future embedded and hardware-aware extensions

### Not Included in the Initial Scope

- full neuromorphic-chip design
- full robotic autonomy stack
- ROS, Gazebo, Isaac Sim, or Habitat dependency
- full radar, DOA, or MIMO implementation
- PYNQ deployment as a required deliverable
- FPGA implementation as a required deliverable
- Vitis HLS synthesis as a required deliverable
- claim of publication-level novelty in the initial course version

## 5. Methodology

### 5.1 Dataset Generation

The first dataset will be a synthetic embedded-sensing dataset with four classes and eight features. Each class will have a different feature-space signature. Gaussian noise will be added to create realistic overlap between classes.

Initial parameters:

```text
num_samples    = 1000
num_classes    = 4
num_features   = 8
random_seed    = 42
```

The class labels will be treated generically as four sensing states:

```text
Class 0: sensing state A
Class 1: sensing state B
Class 2: sensing state C
Class 3: sensing state D
```

This intentionally keeps the first implementation general and course-facing.

### 5.2 Feature Normalization

Each feature vector will be normalized into the interval `[0, 1]`. This normalized representation is required before spike encoding because each feature value will be interpreted as a spike probability or spike-rate parameter.

### 5.3 Spike Encoding

The initial encoding method will be rate-based spike encoding. For each normalized feature value, binary spikes will be generated over a fixed number of time steps. Larger feature values will produce higher spike rates.

Initial parameter:

```text
num_time_steps = 20
```

The spike tensor will have the shape:

```text
num_samples × num_time_steps × num_features
```

### 5.4 LIF-Inspired Classifier

The classifier will use a lightweight leaky-integrate-and-fire inspired accumulation model. Input spike trains will be accumulated into class-level membrane states. A leak factor may be applied at each time step. The predicted class will be selected using the largest final membrane potential.

The first decision rule will be:

> predict the class with the largest final membrane potential.

This rule is selected because it is stable and easy to explain for the baseline implementation.

### 5.5 Evaluation

The project will evaluate both classification performance and edge-relevant behavior. Accuracy alone is not sufficient. Spike count and latency proxy are included because they are relevant to sparse temporal inference and future embedded implementation.

## 6. Expected Deliverables

The expected deliverables are:

- Python source code,
- experiment runner,
- dataset visualization,
- confusion-matrix figure,
- spike-count distribution figure,
- metrics summary file,
- short technical report section,
- GitHub documentation,
- final handoff after baseline results.

Expected output locations:

```text
phase_01_python_prototype/src/
phase_01_python_prototype/results/
phase_01_python_prototype/figures/
docs/reports/
docs/handoffs/
```

## 7. Evaluation Metrics

Minimum metrics:

- classification accuracy,
- confusion matrix,
- average spike count per sample,
- latency proxy in time steps.

Optional metrics if time permits:

- accuracy versus number of time steps,
- spike count versus number of time steps,
- accuracy versus noise level,
- comparison with a simple non-spiking baseline.

## 8. Success Criteria

For a four-class problem, random guessing is approximately 25 percent. The first baseline target is:

```text
accuracy > 75 percent
```

This target is intended only as a practical baseline. The main success criterion is a complete, reproducible, and well-documented end-to-end spike-based edge-inference workflow.

## 9. Risks and Limitations

The main risk is choosing a synthetic dataset that is either too easy or too difficult. A dataset that is too easy may not demonstrate meaningful behavior, while a dataset that is too difficult may obscure the purpose of the spike-based prototype. The first dataset will therefore be simple but not trivial.

Another limitation is that the initial prototype is a software-level model. It should not be presented as a hardware implementation. PYNQ, FPGA, and Vitis HLS extensions are future directions, not required results for the first course deliverable.

## 10. Future Work

After the baseline prototype is stable, the project can be extended in several directions:

1. sensing-specific case study using radar or array-derived features,
2. coarse direction-sector classification,
3. comparison with classical or small DNN baselines,
4. PYNQ ARM-side deployment,
5. Vitis HLS implementation of one small kernel such as spike encoding or LIF update,
6. hardware-aware analysis for possible portfolio or paper development.

## 11. Project Management Plan

The project will be developed in a staged GitHub repository. Each major discussion, design decision, result, or phase transition will be documented using Markdown handoff files.

Current repository:

```text
hmolhem/embedded-ai-snn-edge-inference
```

Current local path:

```text
C:\MyDocument\embedded-ai-snn-edge-inference
```

The immediate next step is to implement the Phase 1 baseline prototype according to the frozen design notes.
