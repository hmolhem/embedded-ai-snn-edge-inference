# Handoff 021 — Phase 2 Proposal LaTeX Template

## Branch

```text
phase-02-proposal-latex-template
```

## Objective

Start Phase 2 in a dedicated GitHub branch and create the initial Phase 2 proposal package using the established LaTeX report-template structure.

## Key Rule Confirmed

All GitHub work must be performed in a feature branch. No direct work should be performed on `main`.

The core LaTeX template structure is preserved:

```text
main.tex
README.md
references.bib
setup/
frontmatter/
content/
appendices/
appendices/console_outputs/
codes/
figures/
```

Project-specific folders such as `cst_setup/` are not copied unless required by the project. Phase 2 is not a CST/RF simulation package, so no `cst_setup/` folder is added.

## Proposal Direction

Phase 2 is defined as a continuation of Phase 1 rather than a separate project.

```text
Phase 1: controlled proof-of-concept for DOA-sector inference using ULA, covariance/beamspace features, spike encoding, and LIF-inspired inference.

Phase 2: robustness and extension study of the same Phase 1 pipeline under more challenging radar/DOA sensing conditions.
```

## Files Added

```text
docs/reports/phase_02_latex/proposal/main.tex
docs/reports/phase_02_latex/proposal/README.md
docs/reports/phase_02_latex/proposal/references.bib
docs/reports/phase_02_latex/proposal/setup/
docs/reports/phase_02_latex/proposal/frontmatter/
docs/reports/phase_02_latex/proposal/content/
docs/reports/phase_02_latex/proposal/appendices/
docs/reports/phase_02_latex/proposal/appendices/console_outputs/
docs/reports/phase_02_latex/proposal/codes/
docs/reports/phase_02_latex/proposal/figures/
```

## Scientific Anchor

The proposal anchors Phase 2 around this question:

```text
Does the Phase 1 spike-based temporal inference path remain accurate, sparse, and latency-controllable when the radar/DOA sensing scenario becomes more challenging?
```

## Next Step

Compile the proposal locally, inspect formatting, then revise content before opening a pull request.
