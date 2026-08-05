# Project Log

This file is the high-level chronological log for the repository. It is intentionally brief. Detailed technical decisions, run results, and repository transitions are recorded in `docs/handoffs/` and in the phase-specific documentation.

## 2026-06-27 — Repository Initialization

- Repository created.
- Main README initialized.
- Handoff 001 added.
- Phase folders and initial scaffolds added.
- Phase 1 minimal Python prototype structure created.

## Phase 1 — Completed

- Replaced the initial generic sensing concept with a physics-based ULA/DOA model.
- Implemented covariance and beamspace feature extraction.
- Implemented nearest-centroid baseline classification.
- Implemented Bernoulli rate encoding and LIF-inspired temporal inference.
- Completed accuracy, confusion-matrix, spike-activity, latency, and parameter-sweep studies.
- Completed Phase 1 report, paper, presentation, transcript, and review package.

Primary records:

```text
phase_01_python_prototype/INDEX.md
phase_01_python_prototype/EXPERIMENTS.md
docs/handoffs/index.md
```

## Phase 2 — Proposal Completed

- Created the Phase 2 LaTeX proposal package.
- Rewrote the proposal as a controlled robustness study of the completed Phase 1 pipeline.
- Defined low-SNR, sector-boundary, and array-model-mismatch experiments.
- Defined Bartlett, continuous nearest-centroid, and LIF-inspired comparison paths.
- Merged the technical proposal rewrite through PR #23.

Primary record:

```text
docs/handoffs/handoff_022_phase02_proposal_technical_rewrite.md
```

## Phase 2 — Fast–Slow DOA Through Day 7

- Implemented aligned progressive snapshots, a causal confidence gate, and a
  mandatory full-data fallback.
- Completed five-seed SNR, sector-boundary, and array-mismatch stress testing.
- Froze and visualized the Day 5 result: baseline accuracy was preserved, but
  the fixed gate generalized to only about 4 percent snapshot reduction.
- Added strict frozen-input hash and condition-identity validation.
- Completed Day 7 on five independent calibration seed pairs while keeping
  five additional holdout pairs sealed for Day 9.
- Confirmed that final normalized margin has useful ranking ability but is not
  calibrated as a probability; no new operating point has yet been selected.

Primary records:

```text
docs/handoffs/handoff_024_phase02_day05_stress_testing.md
docs/handoffs/handoff_025_phase02_day06_results_visualization.md
docs/handoffs/handoff_026_day06_frozen_input_validation.md
docs/handoffs/handoff_027_phase02_day07_confidence_calibration.md
```

## Current Technical Target

Day 8 will apply a pre-declared selection rule to the frozen Day 7 calibration
table. Day 9 will then evaluate that single selected gate once on the sealed
holdout seed pairs.
