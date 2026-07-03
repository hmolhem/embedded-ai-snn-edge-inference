# Handoff 015 — Phase 1 Proposal Template Sync

## Branch

```text
phase-01-proposal-template-sync
```

## Objective

Update the Phase 1 proposal so that it follows the same report-style academic structure used by the main Phase 1 deliverables.

## Summary of Changes

- Converted the proposal from a simple article-style document to a report-style document.
- Added a cover page, Objective page, Project Summary, Table of Contents, List of Figures, and List of Tables.
- Added Chapter 1 with an introductory paragraph.
- Renamed Objectives to Specific Objectives.
- Expanded the Technical Approach section with signal model, feature extraction, baseline classifier, spike encoding, and LIF-inspired inference subsections.
- Added explanatory text before the dataset configuration table.
- Replaced Evaluation Metrics with an Evaluation Plan.
- Added Relevance to Embedded AI.
- Added Timeline / Phase Plan.
- Replaced the manual bibliography with BibTeX references from reference.bib.
- Regenerated phase_01_proposal.pdf.
- Updated .gitignore to exclude LaTeX build artifacts.

## Files Updated

```text
.gitignore
docs/reports/phase_01_latex/phase_01_proposal.tex
docs/reports/phase_01_latex/phase_01_proposal.pdf
docs/handoffs/index.md
```

## Files Added

```text
docs/handoffs/handoff_015_phase01_proposal_template_sync.md
```

## Scope

This branch updates the Phase 1 proposal document and LaTeX workflow only. It does not change experiment data, Python code, model logic, or numerical results.
