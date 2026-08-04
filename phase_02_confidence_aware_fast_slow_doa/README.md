# Phase 2 — Confidence-Aware Fast–Slow DOA

This local checkpoint extends the unchanged Phase 1 reference pipeline with
aligned progressive-snapshot feature views. For each observation, the
`M=32`, `M=64`, and `M=128` feature vectors are computed from prefixes of the
same 128-snapshot realization.

## Day 2 validation command

Run from the repository root:

```powershell
python -m phase_02_confidence_aware_fast_slow_doa.run_day_02_progressive_snapshot_validation
```

Run the focused tests with only the Python standard library:

```powershell
python -m unittest discover -s phase_02_confidence_aware_fast_slow_doa/tests -v
```

The validation must show exact reproducibility and a maximum absolute error no
greater than `1e-12` between the progressive `M=128` view and the unchanged
Phase 1 generator.

## Day 3 — Causal confidence gate

The gate uses a shared `T_max=40` spike realization and accepts a decision only
after the same winning class exceeds the normalized-margin threshold for `K`
consecutive observed time steps.

```powershell
python -m phase_02_confidence_aware_fast_slow_doa.run_day_03_causal_gate_validation
```

## Day 4 — Adaptive controller and fallback

This checkpoint combines accepted `M=32` LIF decisions with the mandatory
`M=128` continuous nearest-centroid fallback and exports both the complete
operating-point sweep and per-sample decisions for the selected preliminary
operating point.

```powershell
python -m phase_02_confidence_aware_fast_slow_doa.run_day_04_adaptive_controller
```

The operating-point selection rule is fixed before inspection: minimize average
snapshots among points whose final accuracy is no more than one percentage point
below the always-continuous reference.

## Day 5 — Multi-seed stress testing

Day 5 freezes the Day 4 candidate operating point (`tau=0.8`, `K=5`) and
evaluates it without retuning across five independent dataset/spike seed pairs.
The protocol covers:

- SNR values from `-15 dB` through `20 dB`;
- signed offsets of `0.5`, `1`, `2`, `5`, and `10` degrees around the internal
  sector boundaries at `-30`, `0`, and `30` degrees; and
- fixed per-element gain/phase mismatch at nominal, mild, moderate, and severe
  levels, with nominal-only training and normalization.

```powershell
python -m phase_02_confidence_aware_fast_slow_doa.run_day_05_stress_tests
```

The configuration is stored in `day_05_stress_config.json`. The detailed
per-seed table, five-seed aggregate table, and JSON validation summary are
written to `results/`. The stress runner compares always-fast,
always-continuous, and adaptive inference on the same samples and shared spike
realizations within every condition.

The Day 5 result is intentionally not used to reselect the threshold. Any
future gate redesign or recalibration must use a separate development split and
new validation seeds.

## Day 6 — Frozen-result visualization and interpretation

Day 6 creates report-ready figures, Markdown tables, and a machine-readable
summary directly from the frozen Day 5 CSV/JSON outputs:

```powershell
python -m phase_02_confidence_aware_fast_slow_doa.run_day_06_results_visualization
```

The runner verifies the Day 5 input hashes, reproduces every aggregate mean and
sample standard deviation from the per-seed rows, and rejects any mismatch
between the pre-registered operating point and the Day 5 configuration. It does
not train, sweep, calibrate, or select a new gate.

Primary outputs:

- `figures/day_06_nominal_accuracy_and_cost.{png,pdf}`
- `figures/day_06_snr_stress.{png,pdf}`
- `figures/day_06_boundary_stress.{png,pdf}`
- `figures/day_06_array_mismatch_stress.{png,pdf}`
- `results/day_06_report_tables.md`
- `results/day_06_results_summary.json`
