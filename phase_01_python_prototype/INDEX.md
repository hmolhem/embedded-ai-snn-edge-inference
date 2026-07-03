# Phase 1 Documentation Index

This index is the navigation entry point for the completed Phase 1 Python prototype.

## Core Files

| File | Purpose |
|---|---|
| `README.md` | Phase 1 objective, pipeline, run commands, outputs, and success criteria. |
| `EXPERIMENTS.md` | Chronological experiment log for Run 001 through Run 005. |
| `REPORT_SECTION.md` | Report-ready narrative section with tables, figures to cite, and engineering interpretation. |

## Source Code Entry Points

| File | Purpose |
|---|---|
| `run_phase_01.py` | Main Phase 1 pipeline runner. |
| `run_phase_01_parameter_sweep.py` | Run 005 LIF time-step/leak parameter sweep runner. |
| `src/main.py` | Main orchestration code for the reference pipeline. |
| `src/parameter_sweep.py` | Run 005 sweep implementation. |
| `src/plots.py` | Plotting utilities for metrics, latency, and trade-off figures. |

## Result Files

| File | Purpose |
|---|---|
| `results/run_001_dataset_summary.txt` | Dataset and split summary. |
| `results/run_001_metrics.txt` | Baseline and initial LIF metrics. |
| `results/run_001_accuracy_vs_snr.csv` | Nearest-centroid accuracy versus SNR. |
| `results/run_002_spike_encoding_summary.txt` | Spike encoding summary. |
| `results/run_003_lif_metrics.txt` | Fixed LIF configuration metrics. |
| `results/run_003_lif_accuracy_vs_snr.csv` | LIF accuracy versus SNR. |
| `results/run_003_lif_latency_vs_snr.csv` | LIF stable-decision latency versus SNR. |
| `results/run_005_lif_parameter_sweep.csv` | Full LIF time-step/leak sweep results. |
| `results/run_005_lif_parameter_sweep_summary.txt` | Human-readable Run 005 sweep summary. |

## Figure Files

| File | Purpose |
|---|---|
| `figures/run_001_example_beamspace_response.png` | Example beamspace response. |
| `figures/run_001_accuracy_vs_snr.png` | Baseline accuracy versus SNR. |
| `figures/run_001_confusion_matrix_snr_10db.png` | Baseline confusion matrix at 10 dB SNR. |
| `figures/run_002_spike_count_distribution.png` | Spike count distribution. |
| `figures/run_003_lif_accuracy_vs_snr.png` | Fixed LIF accuracy versus SNR. |
| `figures/run_003_lif_confusion_matrix_snr_10db.png` | LIF confusion matrix at 10 dB SNR. |
| `figures/run_004_accuracy_comparison_vs_snr.png` | Baseline versus LIF accuracy comparison. |
| `figures/run_004_lif_latency_vs_snr.png` | LIF mean latency versus SNR. |
| `figures/run_005_lif_accuracy_latency_tradeoff.png` | LIF accuracy-latency trade-off from the parameter sweep. |

## Phase 1 Summary

The completed Phase 1 prototype establishes a controlled Python reference workflow for DOA-sector inference using:

```text
physics-based ULA data generation
beamspace feature extraction
nearest-centroid baseline classification
rate-based spike encoding
LIF-inspired temporal accumulation
accuracy, latency, and parameter-sweep analysis
```

Key results:

```text
nearest-centroid baseline accuracy: 0.869048
fixed Run 003 LIF accuracy:         0.825000
best Run 005 LIF accuracy:          0.841667
best Run 005 configuration:         T=40, leak=0.99
lowest-latency Run 005 configuration: T=10, leak=0.99
```

## Recommended Reading Order

1. `README.md`
2. `EXPERIMENTS.md`
3. `REPORT_SECTION.md`
4. `results/run_005_lif_parameter_sweep_summary.txt`
5. `docs/handoffs/index.md`
