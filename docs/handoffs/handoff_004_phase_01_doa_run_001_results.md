# Handoff 004 — Phase 1 DOA Run 001 Results

## 1. Context

This handoff records the first successful local execution of the Phase 1 Python prototype for the `embedded-ai-snn-edge-inference` repository.

The current Phase 1 prototype is no longer an arbitrary toy dataset. It is a physics-based DOA-sector inference reference model built from:

```text
ULA / DOA signal model
    -> array snapshots with controlled SNR
    -> sample covariance matrix
    -> beamspace energy features
    -> train-set min/max normalization
    -> rate-based spike encoding
    -> LIF-inspired sector inference
    -> baseline comparison, metrics, and figures
```

The run was executed locally by Hossein Molhem in the `DS` conda environment from:

```text
C:\MyDocument\embedded-ai-snn-edge-inference
```

Command:

```powershell
python phase_01_python_prototype\run_phase_01.py
```

## 2. Repository Status Before Run

The local repository was updated successfully:

```text
git pull
Updating 22c7019..34249bc
Fast-forward
```

Updated files included:

```text
phase_01_python_prototype/README.md
phase_01_python_prototype/config.yaml
phase_01_python_prototype/src/lif.py
phase_01_python_prototype/src/main.py
phase_01_python_prototype/src/plots.py
```

## 3. Dataset Configuration

The generated dataset summary was:

```text
num_samples: 2800
num_features: 9
num_elements: 8
num_snapshots: 128
spacing_wavelengths: 0.5
theta_range_deg: [-59.95, 59.97]
snr_values_db: [-10.0, -5.0, 0.0, 5.0, 10.0, 15.0, 20.0]
beam_grid_deg: [-60.0, -45.0, -30.0, -15.0, 0.0, 15.0, 30.0, 45.0, 60.0]
```

Class balance:

```text
class_0: 700
class_1: 700
class_2: 700
class_3: 700
```

SNR balance:

```text
-10 dB: 400
 -5 dB: 400
  0 dB: 400
  5 dB: 400
 10 dB: 400
 15 dB: 400
 20 dB: 400
```

Train/test split:

```text
total_train: 1960
total_test: 840
```

The split was stratified by both SNR and DOA class. Each SNR/class cell used:

```text
train = 70
test  = 30
```

## 4. Run 001 — Nearest-Centroid Baseline

The non-spiking nearest-centroid baseline achieved:

```text
overall_accuracy: 0.869048
```

Accuracy versus SNR:

```text
-10.0 dB: 0.758333
 -5.0 dB: 0.908333
  0.0 dB: 0.891667
  5.0 dB: 0.858333
 10.0 dB: 0.866667
 15.0 dB: 0.925000
 20.0 dB: 0.875000
```

Confusion matrix at 10 dB:

```text
rows=true, columns=predicted

     23     7     0     0
      0    29     1     0
      0     3    27     0
      0     0     5    25
```

Interpretation:

The baseline is strong and defensible. It proves that the 9-dimensional beamspace feature vector carries enough physical information for coarse DOA-sector classification. Most errors occur near adjacent sectors, which is expected because the sector boundaries are angularly adjacent and the beamspace grid is coarse.

## 5. Run 002 — Rate-Based Spike Encoding

Spike encoding used:

```text
num_time_steps: 20
num_features: 9
max_possible_spikes_per_sample: 180
```

Training spike statistics:

```text
num_samples: 1960
mean_firing_rate: 0.144436
mean_spike_count_per_sample: 25.998469
std_spike_count_per_sample: 28.827628
min_spike_count_per_sample: 1
max_spike_count_per_sample: 116
```

Testing spike statistics:

```text
num_samples: 840
mean_firing_rate: 0.143201
mean_spike_count_per_sample: 25.776190
std_spike_count_per_sample: 28.698223
min_spike_count_per_sample: 2
max_spike_count_per_sample: 113
```

Interpretation:

The spike representation is sparse. On average, the test set uses about 25.78 spikes out of 180 possible spike slots, equivalent to approximately 14.32% mean firing activity. This is consistent with the intended edge-AI / neuromorphic direction: inference uses sparse binary events rather than dense continuous-valued vectors.

## 6. Run 003 — LIF-Inspired Spike Classifier

The LIF-inspired classifier used:

```text
num_time_steps: 20
leak: 0.97
num_classes: 4
```

Overall result:

```text
overall_accuracy: 0.825000
```

Latency proxy:

```text
mean_latency_steps: 6.423810
std_latency_steps: 6.148086
min_latency_steps: 1
max_latency_steps: 20
```

Accuracy versus SNR:

```text
-10.0 dB: 0.658333
 -5.0 dB: 0.816667
  0.0 dB: 0.800000
  5.0 dB: 0.866667
 10.0 dB: 0.883333
 15.0 dB: 0.883333
 20.0 dB: 0.866667
```

Mean latency versus SNR:

```text
-10.0 dB: 8.775000
 -5.0 dB: 8.641667
  0.0 dB: 7.383333
  5.0 dB: 5.566667
 10.0 dB: 4.783333
 15.0 dB: 4.841667
 20.0 dB: 4.975000
```

Confusion matrix at 10 dB:

```text
rows=true, columns=predicted

     22     8     0     0
      0    28     2     0
      0     2    28     0
      0     0     2    28
```

Interpretation:

The LIF-inspired classifier achieved 82.5% accuracy from sparse spike trains. This is lower than the continuous nearest-centroid baseline, as expected, but still far above the 25% random baseline for a four-class task. At moderate and high SNR values, the LIF classifier approaches or exceeds the baseline in some cells, for example at 10 dB.

The latency proxy is meaningful: as SNR improves, the classifier stabilizes earlier. The mean stable-decision latency falls from about 8.78 time steps at -10 dB to about 4.78 time steps at 10 dB. This gives a defensible edge-inference narrative: easier sensing conditions require fewer spike-time updates before a stable decision emerges.

## 7. Key Technical Conclusions

1. The DOA/ULA data generator works and produces balanced class/SNR data.
2. Beamspace energy features are physically interpretable and useful for coarse DOA-sector classification.
3. The nearest-centroid baseline reaches 86.9% accuracy.
4. Rate encoding produces a sparse spike representation with about 14.3% mean firing activity on the test set.
5. The LIF-inspired classifier reaches 82.5% accuracy using sparse binary spike trains.
6. LIF latency decreases as SNR improves, supporting the embedded/edge-AI interpretation.
7. The results are strong enough for the course project, portfolio, and a future report section.

## 8. Generated Output Files

The local run generated:

```text
phase_01_python_prototype/results/run_001_dataset_summary.txt
phase_01_python_prototype/results/run_001_metrics.txt
phase_01_python_prototype/results/run_001_accuracy_vs_snr.csv
phase_01_python_prototype/results/run_002_spike_encoding_summary.txt
phase_01_python_prototype/results/run_003_lif_metrics.txt
phase_01_python_prototype/results/run_003_lif_accuracy_vs_snr.csv
phase_01_python_prototype/results/run_003_lif_latency_vs_snr.csv
```

Figures generated:

```text
phase_01_python_prototype/figures/run_001_example_beamspace_response.png
phase_01_python_prototype/figures/run_001_accuracy_vs_snr.png
phase_01_python_prototype/figures/run_001_confusion_matrix_snr_10db.png
phase_01_python_prototype/figures/run_002_spike_count_distribution.png
phase_01_python_prototype/figures/run_003_lif_accuracy_vs_snr.png
phase_01_python_prototype/figures/run_003_lif_confusion_matrix_snr_10db.png
```

## 9. Risks and Caveats

1. The LIF classifier is currently prototype-weight based, not trained by STDP or surrogate gradients.
2. The classifier uses rate-coded static features, not direct event-camera or robotic sensor streams.
3. Accuracy varies non-monotonically with SNR because the dataset is randomly generated and sector boundary effects are present.
4. The latency metric is a proxy based on stable predicted class, not measured wall-clock or hardware latency.
5. Generated result files and figures exist locally after the run. They should be committed if the repository is intended to preserve numerical outputs.

## 10. Recommended Next Actions

### Immediate

1. Inspect generated figures in:

```text
phase_01_python_prototype/figures/
```

2. Run:

```powershell
git status
```

3. Add and commit the generated results and figures if they look correct.

Suggested commands:

```powershell
git add phase_01_python_prototype/results phase_01_python_prototype/figures
git commit -m "Add Phase 1 DOA run outputs"
git push
```

### Technical refinement

1. Add an accuracy-versus-time-step sweep.
2. Add LIF-vs-baseline comparison figure on the same SNR axis.
3. Add a latency-versus-SNR figure.
4. Test several time windows: T = 5, 10, 20, 40.
5. Test leakage values: 0.90, 0.95, 0.97, 1.00.
6. Add a short method description for the course report.

### Report preparation

The Phase 1 report section should emphasize:

```text
physics-based sensing model
compact beamspace features
sparse rate-coded spike representation
LIF-inspired temporal inference
accuracy/latency trade-off
hardware-aware edge-AI direction
```

## 11. Resume Point for Another Chat

Continue from Handoff 004. The Phase 1 DOA Python prototype has run successfully. The nearest-centroid baseline achieved 86.9% accuracy, and the sparse LIF-inspired spike classifier achieved 82.5% accuracy with a mean stable-decision latency of 6.42 time steps. Next tasks are to inspect/commit local generated figures and results, create comparison/latency plots, and begin converting the run into a formal course-report section.
