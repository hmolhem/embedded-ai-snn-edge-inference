# Handoff 007 — Run 005 LIF Parameter Sweep

## 1. Context

This handoff records Run 005 for the Phase 1 Python DOA/SNN prototype.

Previous completed work:

```text
PR #5: Run 004 accuracy and latency comparison plots
PR #6: Run 004 completion message cleanup
```

Current development branch:

```text
sweep-lif-time-steps-leak
```

## 2. Objective

Evaluate the sensitivity of the LIF-inspired spike classifier to two hardware-relevant inference parameters:

```text
num_time_steps
leak
```

The goal is to characterize the accuracy-latency trade-off rather than relying on a single manually selected LIF configuration.

## 3. Sweep Grid

```text
num_time_steps = [10, 20, 30, 40]
leak = [0.90, 0.95, 0.97, 0.99]
total configurations = 16
```

The nearest-centroid baseline accuracy remains the reference upper comparison:

```text
baseline_nearest_centroid_accuracy: 0.869048
```

## 4. Implementation Files

Added:

```text
phase_01_python_prototype/src/parameter_sweep.py
phase_01_python_prototype/run_phase_01_parameter_sweep.py
```

Updated:

```text
phase_01_python_prototype/src/plots.py
```

The new plot utility generates an accuracy-latency trade-off figure from the Run 005 sweep rows.

## 5. Generated Outputs

```text
phase_01_python_prototype/results/run_005_lif_parameter_sweep.csv
phase_01_python_prototype/results/run_005_lif_parameter_sweep_summary.txt
phase_01_python_prototype/figures/run_005_lif_accuracy_latency_tradeoff.png
```

## 6. Local Verification Command

Run from the repository root:

```powershell
python phase_01_python_prototype\run_phase_01_parameter_sweep.py
```

The command completed successfully and generated the Run 005 CSV, text summary, and trade-off figure.

## 7. Key Results

Best accuracy configuration:

```text
num_time_steps: 40
leak: 0.99
overall_accuracy: 0.841667
mean_latency_steps: 8.396429
```

Lowest latency configuration:

```text
num_time_steps: 10
leak: 0.99
overall_accuracy: 0.776190
mean_latency_steps: 3.782143
```

## 8. Engineering Interpretation

Run 005 supports a clear embedded-inference design trade-off:

```text
Increasing num_time_steps generally improves LIF accuracy.
Higher leak values generally preserve accumulated evidence better.
Shorter spike windows reduce latency but reduce accuracy.
The best sweep accuracy still remains below the continuous nearest-centroid baseline.
```

Compared with the previous fixed LIF configuration from Run 003:

```text
Run 003 fixed LIF accuracy: 0.825000
Run 005 best LIF accuracy: 0.841667
```

Thus the parameter sweep improves the LIF-inspired result while preserving the report narrative that spike-based inference trades some continuous-valued accuracy for temporal sparse processing and latency control.

## 9. Resume Point

After merging this branch, synchronize local `main`, delete the `sweep-lif-time-steps-leak` branch, and continue with the next focused branch action.

Recommended next action:

```text
run-005-report-section
```

Purpose: convert Run 001 through Run 005 into a concise report-ready Phase 1 section with figures, tables, and engineering interpretation.
