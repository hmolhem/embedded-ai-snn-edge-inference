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

## Current Technical Target

Begin Phase 2 Run 001 by reproducing the Phase 1 reference point inside the Phase 2 experiment structure before introducing any new stress model.
