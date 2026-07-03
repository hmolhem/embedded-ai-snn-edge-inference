# Phase 1 — Python Prototype

## Objective

Build a Python reference prototype for spike-based DOA-sector inference using a physics-based Uniform Linear Array (ULA) signal model.

This phase keeps the original project structure intact. Phase 1 remains the Python prototype phase, but the prototype is now based on an engineering DOA model rather than an arbitrary synthetic sensing dataset.

## Navigation

| File | Purpose |
|---|---|
| `INDEX.md` | Phase 1 documentation and artifact map. |
| `EXPERIMENTS.md` | Chronological experiment log for Run 001 through Run 005. |
| `REPORT_SECTION.md` | Report-ready Phase 1 narrative and interpretation. |
| `results/` | Text and CSV outputs. |
| `figures/` | Generated report figures. |
| `src/` | Source code for the Phase 1 reference implementation. |

## Minimal Engineering Pipeline

```text
ULA / DOA signal model
    ↓
Array snapshots with controlled SNR
    ↓
Sample covariance matrix Rxx
    ↓
Beamspace or covariance-derived features
    ↓
Feature normalization
    ↓
Spike encoding
    ↓
LIF-inspired DOA-sector classifier
    ↓
Baseline comparison
    ↓
Metrics and figures
```

## Initial Technical Tasks

1. Implement ULA steering-vector generation.
2. Generate single-source complex array snapshots.
3. Add complex Gaussian noise for selected SNR values.
4. Assign true DOA angles to coarse sector labels.
5. Compute sample covariance matrices.
6. Extract compact beamspace or covariance-derived features.
7. Normalize features using training-set statistics.
8. Encode normalized features into spike trains.
9. Implement a lightweight LIF-inspired sector classifier.
10. Implement a nearest-centroid non-spiking baseline.
11. Evaluate accuracy versus SNR.
12. Generate confusion matrices and spike-count plots.
13. Save all figures and results.
14. Sweep LIF time-window and leak parameters.
15. Convert Phase 1 results into a report-ready engineering section.
16. Add a final Phase 1 documentation index.

## Initial Parameters

```text
Array type:          Uniform Linear Array
Number of elements:  N = 8
Snapshots:           M = 128
Element spacing:     d = lambda/2
Source count:        1
DOA range:           -60 deg to +60 deg
Sectors:             4
SNR sweep:           -10, -5, 0, 5, 10, 15, 20 dB
Spike time steps:    20
LIF leak factor:     0.97
```

## Run 005 Parameter Sweep

Run 005 evaluates the sensitivity of the LIF-inspired classifier to the spike time-window length and leak factor:

```text
num_time_steps = [10, 20, 30, 40]
leak = [0.90, 0.95, 0.97, 0.99]
total configurations = 16
```

Key results:

```text
baseline_nearest_centroid_accuracy: 0.869048
best_lif_accuracy: 0.841667 at T=40, leak=0.99
lowest_latency_configuration: T=10, leak=0.99, mean_latency_steps=3.782143
```

This run supports the embedded-inference accuracy-latency trade-off narrative: longer spike windows and higher leak values generally improve accuracy, while shorter windows reduce stable-decision latency.

## Report Section

A report-ready Phase 1 narrative is available at:

```text
REPORT_SECTION.md
```

It summarizes the signal model, dataset, baseline classifier, spike encoding, LIF-inspired inference path, Run 005 parameter sweep, and accuracy-latency interpretation.

## Current Output Files

```text
results/run_001_dataset_summary.txt
results/run_001_metrics.txt
results/run_001_accuracy_vs_snr.csv
results/run_002_spike_encoding_summary.txt
results/run_003_lif_metrics.txt
results/run_003_lif_accuracy_vs_snr.csv
results/run_003_lif_latency_vs_snr.csv
results/run_005_lif_parameter_sweep.csv
results/run_005_lif_parameter_sweep_summary.txt

figures/run_001_example_beamspace_response.png
figures/run_001_accuracy_vs_snr.png
figures/run_001_confusion_matrix_snr_10db.png
figures/run_002_spike_count_distribution.png
figures/run_003_lif_accuracy_vs_snr.png
figures/run_003_lif_confusion_matrix_snr_10db.png
figures/run_004_accuracy_comparison_vs_snr.png
figures/run_004_lif_latency_vs_snr.png
figures/run_005_lif_accuracy_latency_tradeoff.png
```

## Run Commands

Main Phase 1 pipeline from the repository root:

```powershell
python phase_01_python_prototype\run_phase_01.py
```

Run 005 LIF parameter sweep from the repository root:

```powershell
python phase_01_python_prototype\run_phase_01_parameter_sweep.py
```

## Success Criteria

Phase 1 is successful if it produces a complete end-to-end DOA-sector inference result with:

- physics-based ULA data generation,
- valid DOA-sector labels,
- compact covariance or beamspace features,
- spike-based LIF-inspired classification,
- nearest-centroid baseline comparison,
- accuracy versus SNR,
- confusion matrix,
- spike-count analysis,
- latency proxy in time steps,
- LIF parameter sensitivity analysis,
- report-ready engineering interpretation,
- clear figures and reproducible metrics.

## Non-Goals

This phase does not attempt:

- full MUSIC or ESPRIT implementation,
- full multi-source DOA estimation,
- full robotic autonomy,
- full neuromorphic chip design,
- PYNQ deployment,
- Vitis HLS synthesis,
- complete FPGA accelerator,
- publication-level novelty claim.

The code should still be written in a hardware-aware style so that later phases can refactor the spike encoder and LIF inference path toward PYNQ or Vitis HLS.
