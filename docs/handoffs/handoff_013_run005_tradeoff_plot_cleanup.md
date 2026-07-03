# Handoff 013 — Run 005 Tradeoff Plot Cleanup

## Branch

```text
phase-01-improve-run005-tradeoff-plot
```

## Objective

Improve the readability of the Run 005 LIF accuracy--latency tradeoff figure used as Figure 1.4 in the Phase 1 report.

The previous version annotated every sweep point with a `T=...` label. The updated version labels only the two engineering anchor points.

## Files Updated

```text
phase_01_python_prototype/src/plots.py
phase_01_python_prototype/figures/run_005_lif_accuracy_latency_tradeoff.png
docs/reports/phase_01_latex/phase_01_report.pdf
docs/handoffs/index.md
```

## Files Added

```text
docs/handoffs/handoff_013_run005_tradeoff_plot_cleanup.md
```

## Plotting Change

Updated `plot_lif_parameter_sweep_tradeoff()` in:

```text
phase_01_python_prototype/src/plots.py
```

The figure now highlights only:

```text
Best accuracy: T=40, leak=0.99
Lowest latency: T=10, leak=0.99
```

## Regenerated Artifacts

```text
phase_01_python_prototype/figures/run_005_lif_accuracy_latency_tradeoff.png
docs/reports/phase_01_latex/phase_01_report.pdf
```

## Scope

This branch changes visualization readability only. It does not change Run 005 numerical data, classifier logic, citations, or bibliography.
