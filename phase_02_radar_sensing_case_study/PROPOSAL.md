# Phase 2 Proposal — Radar / DOA Sensing Case Study

## 1. Title

**Spike-Encoded Sensing Features for Direction-Sector Classification**

## 2. Motivation

Phase 1 establishes a minimal spike-based edge-inference prototype using a generic simulated sensing dataset. Phase 2 provides a more meaningful sensing case study by connecting the prototype to radar and array-processing concepts.

Radar and array sensors are relevant to embedded and robotic systems because they can support perception under conditions where vision may be limited, such as poor lighting, dust, fog, or industrial environments. A full radar processor or a full DOA estimator is beyond the scope of this phase. Instead, the focus is on compact features that can be used for lightweight direction-sector classification.

## 3. Problem Statement

The problem is to evaluate whether compact radar/array-derived features can be converted into spike-like representations and used for coarse direction-sector classification.

This phase is not intended to replace full MUSIC, ESPRIT, or high-resolution DOA estimation. It is a small edge-inference case study that connects spike-based classification with sensing-oriented feature extraction.

## 4. Objective

Extend the Phase 1 software workflow to a radar/array-sensing dataset and evaluate coarse angular-sector classification.

The objective is to build a technically controlled case study that can later support portfolio development, hardware-aware analysis, and possible research extension.

## 5. Technical Scope

### Included

- ULA or simplified MIMO/array simulation
- single-source or simple multi-class direction scenario
- coarse DOA-sector labels
- compact feature extraction
- spike encoding of the feature vector
- lightweight LIF-inspired classification
- comparison against at least one simple non-spiking baseline if time permits
- accuracy and confusion-matrix analysis
- robustness test versus SNR or noise level

### Excluded

- full radar signal chain
- full MUSIC or ESPRIT implementation as the main deliverable
- multi-source high-resolution DOA estimation
- real radar hardware
- FPGA implementation
- claim of a complete neuromorphic radar processor

## 6. Methodology

A simple array-sensing simulation will generate snapshots for a uniform linear array or an equivalent compact array model. From the simulated data, a small set of features will be extracted. Candidate features include:

- selected covariance-matrix entries,
- covariance magnitudes and phases,
- beamspace energy samples,
- simple angular response samples.

The feature vector will be normalized and passed through the same spike-encoding framework developed in Phase 1. A lightweight LIF-inspired classifier will then predict a coarse direction sector.

Candidate sector labels:

```text
Class 1: -60° to -30°
Class 2: -30° to   0°
Class 3:   0° to  30°
Class 4:  30° to  60°
```

## 7. Expected Deliverables

- radar/array-sensing simulation script
- feature-extraction module
- spike-encoded feature pipeline
- classification results
- confusion matrices
- accuracy versus SNR or noise plot
- spike-count and latency analysis
- updated Phase 2 README and design notes
- Handoff after Phase 2 design and first results

## 8. Evaluation Metrics

Minimum metrics:

- classification accuracy
- confusion matrix
- average spike count
- latency in time steps
- accuracy versus SNR or noise level

Optional metrics:

- baseline comparison with logistic regression, nearest centroid, or a small dense neural network
- feature-dimension comparison
- simple operation-count estimate
- memory-footprint estimate

## 9. Risks and Limitations

This phase must remain controlled. It should not expand into a full radar-processing thesis. The angular-sector classifier should be framed as coarse edge sensing, not high-resolution DOA estimation.

Another risk is premature exposure of deeper research ideas. The course-facing description can remain general, while the more specialized DOA/MIMO/FPGA research path can be developed internally after baseline results are available.

## 10. Future Extension

If Phase 2 produces strong and clean results, it can support:

- a portfolio-quality radar/edge-AI demonstration,
- comparison with classical and DNN baselines,
- PYNQ deployment of the inference workflow,
- Vitis HLS implementation of spike encoding or LIF update,
- paper-level investigation of hardware-aware spike-based sensing inference.
