# Phase 2 Proposal LaTeX Package

This directory is the maintained source package for the Phase 2 proposal:

```text
Robustness and Accuracy--Latency Evaluation of Spike-Based
DOA-Sector Inference for Autonomous Edge Sensing
```

The proposal is a direct continuation of the completed Phase 1 ULA/DOA-sector inference pipeline. It defines a controlled robustness study involving low SNR, sector-boundary ambiguity, and array gain/phase mismatch.

## Package Structure

```text
main.tex                         Main LaTeX entry point
references.bib                   Proposal bibliography
setup/                           Shared template configuration; modify only when explicitly required
frontmatter/                     Title page, objective, abstract, and front matter
content/                         Proposal sections 01 through 11
appendices/                      Appendix structure
appendices/console_outputs/      Reserved for reproducible console records
codes/                           Reserved for report-associated source listings
figures/                         Proposal and later report figures
README.md                        This package guide
```

## Source-of-Truth Rule

The established LaTeX template structure in this directory is the source of truth. Do not replace the package wholesale or modify `setup/`, template macros, title-page structure, or bibliography configuration without an explicit technical reason and review.

The bibliography uses the established `biblatex`/Biber configuration. Local Biber execution has been unreliable, so final bibliography compilation and visual review are performed in Overleaf.

## Editing and Overleaf Workflow

```text
1. Make project-specific changes on a GitHub feature branch.
2. Review every changed file from the branch after writing it.
3. Pull the branch into the local repository.
4. Copy only the changed `.tex` files into the matching Overleaf project.
5. Compile and inspect the complete PDF in Overleaf.
6. Return required corrections to the same feature branch.
7. Create or update the handoff and handoff-index entry.
8. Open the pull request.
9. Merge only after explicit approval.
10. Synchronize local `main` after the merge.
```

## Current Status

The Phase 2 proposal technical rewrite was merged through PR #23. The scientific scope, methodology, experimental plan, deliverables, timeline, risks, and conclusion are documented in:

```text
docs/handoffs/handoff_022_phase02_proposal_technical_rewrite.md
```

The next technical activity is Phase 2 Run 001: reproduce the Phase 1 reference results inside the Phase 2 experiment structure before adding new stress conditions.
