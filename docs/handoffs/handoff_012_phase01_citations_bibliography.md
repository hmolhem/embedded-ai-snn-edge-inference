# Handoff 012 — Phase 1 Citations and Bibliography Update

## Context

This branch follows the completed Phase 1 theory and appendix update.

Current branch:

```text
phase-01-citations-bibliography
```

## Objective

Add formal citations and a BibTeX bibliography to the Phase 1 report.

This branch intentionally focuses on citation cleanup and bibliography integration only.

## Files Updated

```text
docs/reports/phase_01_latex/phase_01_report.tex
docs/handoffs/index.md
```

## Files Added

```text
docs/reports/phase_01_latex/reference.bib
docs/handoffs/handoff_012_phase01_citations_bibliography.md
```

## Main Changes

The report now uses BibTeX instead of a manually written `thebibliography` block.

Added packages:

```latex
\usepackage{cite}
\usepackage{url}
```

Added bibliography connection:

```latex
\clearpage
\phantomsection
\addcontentsline{toc}{section}{References}
\bibliographystyle{IEEEtran}
\bibliography{reference}
```

## References Added

```text
Van Trees — optimum array processing and ULA theory
Haykin — covariance/statistical signal-processing background
Duda, Hart, Stork — nearest-centroid and pattern classification
Gerstner and Kistler — spiking neuron and LIF modeling
Maass — spiking neural networks
Roy, Jaiswal, Panda — neuromorphic and spike-based machine intelligence
Molhem GitHub repo — reproducible Phase 1 implementation and artifacts
KSU EE 6900 project deliverable — course project context
```

## Citation Placement

Inline citations were added to the report sections covering:

```text
Purpose and Scope
Theoretical Background
Uniform Linear Array Signal Model
Sample Covariance Matrix
Beamspace Feature Extraction
Nearest-Centroid Classification
Rate-Based Spike Encoding
LIF-Inspired Temporal Inference
Stable-Decision Latency
Signal Model and Dataset
Engineering Interpretation
Conclusion
Appendix derivations
```

## Important Compile Note

Because the report now uses BibTeX, compile using this sequence from `docs/reports/phase_01_latex`:

```powershell
pdflatex phase_01_report.tex
bibtex phase_01_report
pdflatex phase_01_report.tex
pdflatex phase_01_report.tex
```

After compilation, remove temporary files and commit only the updated PDF:

```text
docs/reports/phase_01_latex/phase_01_report.pdf
```

Do not commit:

```text
*.aux
*.bbl
*.blg
*.log
*.out
*.toc
```
