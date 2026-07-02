# Phase 1 — Python Prototype

## Objective

Build a Python reference prototype for spike-based DOA-sector inference using a physics-based Uniform Linear Array (ULA) signal model.

This phase keeps the original project structure intact. Phase 1 remains the Python prototype phase, but the prototype is now based on an engineering DOA model rather than an arbitrary synthetic sensing dataset.

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

## Current Output Files

```text
results/run_001_dataset_summary.txt
results/run_001_metrics.txt
results/run_001_accuracy_vs_snr.csv
results/run_002_spike_encoding_summary.txt
results/run_003_lif_metrics.txt
results/run_003_lif_accuracy_vs_snr.csv
results/run_003_lif_latency_vs_snr.csv

figures/run_001_example_beamspace_response.png
figures/run_001_accuracy_vs_snr.png
figures/run_001_confusion_matrix_snr_10db.png
figures/run_002_spike_count_distribution.png
figures/run_003_lif_accuracy_vs_snr.png
figures/run_003_lif_confusion_matrix_snr_10db.png
```

## Run Command

From the repository root:

```powershell
python phase_01_python_prototype\run_phase_01.py
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
