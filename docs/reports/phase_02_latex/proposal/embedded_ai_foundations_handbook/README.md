# Embedded AI Foundations Handbook LaTeX Package

This package adapts the maintained EE 6900 Phase 2 proposal LaTeX template into a standalone technical handbook:

**Embedded AI and Autonomous Robotics: A Systems View from Sensing to Decision**

## Structure

```text
main.tex
references.bib
frontmatter/
  titlepage.tex
  objective.tex
  abstract.tex
content/
  00_report_body.tex
  01_embedded_ai_worldview.tex
  ...
  14_conclusion_learning_path.tex
figures/
  TikZ source figures
appendices/
  appendix_glossary.tex
  appendix_paper_review_template.tex
```

The package intentionally reuses the shared template configuration from the parent proposal directory:

```latex
\input{../setup/01_packages}
...
\input{../setup/08_theme}
```

Compile `main.tex` with pdfLaTeX and Biber from the `embedded_ai_foundations_handbook` directory. In Overleaf, keep the package under the same parent proposal project or copy the shared `setup/` folder beside it and adjust the relative paths.

## Scope

The handbook is written in English and provides:

- the complete sensing-to-decision systems map;
- foundational definitions for sensors, modalities, measurements, and representations;
- calibration, synchronization, and data association;
- data-, feature-, decision-, state-, and runtime-level sensor fusion;
- loose and tight coupling, odometry, localization, and SLAM;
- CNN, GNN, asynchronous GNN, transformer, attention, and SNN foundations;
- embedded constraints and hardware--algorithm co-design;
- robustness, uncertainty, fault tolerance, and safety;
- a detailed comparative chapter for all six Week 7 papers;
- a reusable paper-review method and worksheet.
