# Phase 1 Design Notes

## 1. Design Status

Status: **frozen for initial implementation**

This file records the first concrete design for Phase 1 of the project:

> Lightweight Spike-Based Edge Inference for Embedded Sensing

The purpose of this phase is to build a minimal, defensible, end-to-end Python prototype. The design is intentionally simple so that it can be implemented, tested, documented, and extended without overclaiming.

## 2. Dataset

The initial dataset will be a synthetic embedded-sensing dataset with four classes and eight numerical features.

The dataset is generic by design. It should not be described as radar, DOA, MIMO, robotics simulator output, or FPGA data in Phase 1. It represents a small simulated sensing problem with class-dependent feature signatures.

### Parameters

```text
num_samples    = 1000
num_classes    = 4
num_features   = 8
random_seed    = 42
```

### Dataset Concept

Each class will have a different center in the eight-dimensional feature space. Gaussian noise will be added to create overlap between classes.

The class labels may be interpreted generically as:

```text
Class 0: sensing state A
Class 1: sensing state B
Class 2: sensing state C
Class 3: sensing state D
```

The dataset must be simple enough to demonstrate the spike-inference pipeline but not so trivial that the classification result has no value.

## 3. Features

Each sample is represented by an eight-dimensional feature vector:

```text
x = [x1, x2, x3, x4, x5, x6, x7, x8]
```

Feature values will be normalized to the interval `[0, 1]` before spike encoding.

### Feature-Generation Plan

1. Define one feature-center vector per class.
2. Draw samples around each center using Gaussian noise.
3. Clip or normalize the final dataset into a bounded range.
4. Split into training and test subsets.

Recommended first split:

```text
train_fraction = 0.70
test_fraction  = 0.30
```

## 4. Spike Encoding

The first spike-encoding method will be **rate-based encoding**.

### Rationale

Rate coding is simple, explainable, and hardware-friendly. It is not the most biologically detailed encoding method, but it is appropriate for the first minimal prototype.

### Method

1. Normalize features into `[0, 1]`.
2. Interpret each feature value as a spike probability.
3. Generate binary spikes over a fixed number of time steps.
4. Higher feature values produce higher spike rates.

### Parameters

```text
num_time_steps = 20
```

### Spike Tensor Shape

```text
num_samples × num_time_steps × num_features
```

## 5. Classifier

The first classifier will be a lightweight LIF-inspired class accumulator.

### Concept

Input spike trains are accumulated into class-level membrane states. Each class has a score or membrane potential. A leak factor may be applied at each time step.

```text
input spikes
    ↓
weighted accumulation
    ↓
leaky membrane update
    ↓
final class scores
    ↓
predicted class
```

### Decision Rule

The first decision rule will be:

> Predict the class with the largest final membrane potential.

This is more stable than using earliest threshold crossing for the first implementation.

### Initial Weight Strategy

For the first baseline, class weights can be derived from normalized class-center vectors. This avoids introducing a training algorithm before the pipeline is working.

Later versions may add logistic regression, nearest-centroid classification, or a small DNN baseline.

## 6. Metrics

Minimum metrics for Run 001:

- classification accuracy
- confusion matrix
- average spike count per sample
- average latency proxy in time steps

### Accuracy Target

For four classes, random guessing is approximately 25 percent. The first target is:

```text
accuracy > 75 percent
```

This is a baseline target, not a final research claim.

### Latency Proxy

Latency will initially be measured as the number of time steps required by the inference window. Optional later versions may estimate earliest stable decision time.

## 7. Figures

Minimum figures for Run 001:

1. dataset visualization using the first two features or PCA-like projection,
2. confusion matrix,
3. spike-count distribution.

Optional later figures:

- accuracy versus number of time steps,
- spike count versus number of time steps,
- accuracy versus noise level,
- class-wise spike activity.

## 8. Planned Output Files

Results should be saved under:

```text
phase_01_python_prototype/results/
```

Figures should be saved under:

```text
phase_01_python_prototype/figures/
```

Recommended first output files:

```text
results/run_001_metrics.txt
figures/run_001_dataset_visualization.png
figures/run_001_confusion_matrix.png
figures/run_001_spike_count_distribution.png
```

## 9. Implementation Modules

The first implementation should use the existing scaffold:

```text
src/dataset.py
src/spike_encoding.py
src/lif.py
src/metrics.py
src/plots.py
src/main.py
run_phase_01.py
```

### Module Responsibilities

```text
dataset.py          generate data and normalize features
spike_encoding.py   convert normalized features to spike tensor
lif.py              class-level LIF-inspired inference
metrics.py          accuracy, confusion matrix, spike statistics
plots.py            generate and save figures
main.py             run full experiment
run_phase_01.py     convenience runner
```

## 10. Non-Goals for Phase 1

Phase 1 does not attempt:

- full neuromorphic hardware,
- full robotic autonomy,
- robotics simulators,
- radar/DOA/MIMO implementation,
- PYNQ deployment,
- Vitis HLS synthesis,
- publication-level novelty claim.

## 11. Success Criteria for Run 001

Run 001 is successful if it produces:

- complete end-to-end execution,
- saved metrics file,
- saved figures,
- accuracy above random guessing,
- interpretable spike-count statistics,
- clean enough output for the first course-report section.

## 12. Next Step

Implement the baseline code using this frozen design.

After the first successful run, create:

```text
docs/handoffs/handoff_003_phase_01_run_001_results.md
```
