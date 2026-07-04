# Handoff 018 — Cite Prior SCM HLS Work in Phase 1 Proposal

## Branch

```text
cite-scm-hls-prior-work-in-proposal
```

## Objective

Connect the Phase 1 embedded-AI proposal to the author's prior FPGA/HLS sample-covariance-matrix accelerator repository.

## Motivation

The Phase 1 proposal already describes a path from ULA-based DOA sector inference toward hardware-aware implementation, FPGA acceleration, PYNQ deployment, and Vitis HLS-oriented embedded inference. The prior SCM HLS repository provides a concrete engineering foundation for this direction because it implements and verifies the covariance stage of a DOA preprocessing pipeline in Vitis HLS.

## Summary of Changes

- Added a BibTeX entry for the prior SCM HLS repository.
- Updated the Phase 1 proposal Motivation section to mention the author's prior FPGA/HLS work on sample-covariance-matrix acceleration for DOA preprocessing.
- Updated the Relevance to Embedded AI section to identify the prior SCM HLS accelerator as a hardware-aware foundation for mapping the covariance stage of an array-processing pipeline toward FPGA implementation.
- Regenerated the Phase 1 proposal PDF after running LaTeX and BibTeX.

## Files Updated

```text
docs/reports/phase_01_latex/reference.bib
docs/reports/phase_01_latex/phase_01_proposal.tex
docs/reports/phase_01_latex/phase_01_proposal.pdf
docs/handoffs/index.md
```

## Files Added

```text
docs/handoffs/handoff_018_cite_scm_hls_prior_work.md
```

## Scope

This branch updates proposal documentation and bibliography only. It does not change experiment data, Python code, model logic, or numerical results.

## Engineering Interpretation

The citation should be interpreted as prior author engineering work, not as an external theoretical authority. It strengthens the proposal narrative by showing that the current embedded-AI direction continues an existing DOA, covariance-processing, and FPGA/HLS portfolio path.
