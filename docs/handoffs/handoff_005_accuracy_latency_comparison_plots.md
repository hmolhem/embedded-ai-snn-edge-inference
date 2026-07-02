# Handoff 005 — Accuracy and Latency Comparison Plots

## 1. Context

This handoff records the focused action completed on branch:

```text
accuracy-latency-comparison-plots
```

This action follows PR #4, which added the LIF-inspired spike classifier for Phase 1 DOA-sector inference.

## 2. Scope

This branch adds two report-ready figures:

```text
run_004_accuracy_comparison_vs_snr.png
run_004_lif_latency_vs_snr.png
```

The physical DOA model, dataset configuration, spike encoder, and LIF classifier logic were not changed.

## 3. Code Changes

Modified files:

```text
phase_01_python_prototype/src/plots.py
phase_01_python_prototype/src/main.py
```

New plotting utilities:

```text
plot_accuracy_comparison_vs_snr()
plot_latency_vs_snr()
```

## 4. Generated Figures

```text
phase_01_python_prototype/figures/run_004_accuracy_comparison_vs_snr.png
phase_01_python_prototype/figures/run_004_lif_latency_vs_snr.png
```

## 5. Technical Interpretation

The accuracy comparison figure overlays the continuous nearest-centroid baseline and the sparse LIF-inspired spike classifier on the same SNR grid.

The latency figure shows the mean stable-decision latency of the LIF classifier versus SNR. This supports the edge-AI interpretation because the classifier tends to stabilize earlier as the sensing condition improves.

## 6. Key Numerical Context

Nearest-centroid baseline:

```text
overall_accuracy: 0.869048
```

LIF-inspired spike classifier:

```text
overall_accuracy: 0.825000
mean_latency_steps: 6.423810
num_time_steps: 20
```

## 7. Workflow Status

The code and figures were committed locally and pushed to the remote branch in commit:

```text
c847751 Add Phase 1 accuracy and latency comparison plots
```

This handoff completes the documentation record for the current branch action.

## 8. Next Step

Open a focused PR from `accuracy-latency-comparison-plots` into `main`, squash-merge it, synchronize local `main`, delete the branch, and start the next action from a new branch.
