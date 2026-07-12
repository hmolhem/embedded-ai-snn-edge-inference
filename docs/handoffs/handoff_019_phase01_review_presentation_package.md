# Handoff 019 — Phase 1 Review and Presentation Package

## Branch

```text
phase-01-review-presentation-package
```

## Objective

Prepare a submission-ready Phase 1 review and presentation package for Dr. Feng based on the finalized Phase 1 report.

## Final Deliverable Interpretation

After review, the appropriate paper-style deliverable for Dr. Feng is the existing IEEE-style paper rather than the separately added paper-review memo. The IEEE paper is the stronger deliverable because it uses IEEE conference format, includes the core Phase 1 results, and reports the generated figures.

The paper/review component of the package should therefore be interpreted as:

```text
docs/reports/phase_01_latex/phase_01_ieee_paper.tex
docs/reports/phase_01_latex/phase_01_ieee_paper.pdf
```

The separately added files below were later identified as redundant and scheduled for cleanup in Handoff 020:

```text
docs/reports/phase_01_latex/phase_01_paper_review.tex
docs/reports/phase_01_latex/phase_01_paper_review.pdf
```

## Presentation Deliverables Added

```text
docs/reports/phase_01_latex/phase_01_final_presentation.tex
docs/reports/phase_01_latex/phase_01_final_presentation.pdf
docs/reports/phase_01_latex/phase_01_final_presentation_transcript.tex
docs/reports/phase_01_latex/phase_01_final_presentation_transcript.pdf
```

## IEEE Paper Component

The IEEE-style paper summarizes the Phase 1 technical contribution in conference-paper format. It includes:

- embedded-AI motivation,
- ULA signal model,
- covariance and beamspace feature formulation,
- nearest-centroid baseline,
- rate-based spike encoding,
- LIF-inspired temporal inference,
- accuracy and latency results,
- generated figures,
- engineering interpretation of the spike-based path.

The central interpretation is that the spike-based path is not an accuracy-improving replacement for the continuous baseline. Its value is architectural: sparse temporal inference, measurable stable-decision latency, and tunable accuracy--latency behavior.

## Final Presentation

The final presentation is designed for a minimum 15-minute delivery. It contains 20 technical frames plus the title frame. The slide sequence covers:

- motivation,
- problem statement,
- technical objective,
- DOA sector inference rationale,
- end-to-end pipeline,
- ULA signal model,
- covariance and beamspace features,
- baseline classifier,
- spike encoding,
- LIF-inspired temporal inference,
- dataset configuration,
- baseline results,
- LIF results,
- Run 005 parameter sweep,
- accuracy--latency trade-off,
- engineering interpretation,
- limitations,
- prior FPGA/HLS SCM connection,
- conclusion,
- next steps.

## Transcript

The transcript provides slide-by-slide speaking notes for the final presentation. The planned speaking time is approximately 15--17 minutes, assuming an average delivery pace of about 130--145 words per minute with short transitions between slides.

## Key Technical Message

The nearest-centroid baseline achieved 86.90 percent accuracy. The fixed LIF-inspired configuration achieved 82.50 percent accuracy with a mean stable-decision latency of 6.423810 time steps. The best LIF parameter-sweep configuration achieved 84.17 percent accuracy at T=40 and leak=0.99. Therefore, the spike-based path should not be presented as an accuracy-improving replacement for the continuous baseline. Its value is architectural: sparse temporal inference, measurable stable-decision latency, and tunable accuracy--latency behavior.

## Scope

This branch adds review and presentation deliverables only. It does not change Python code, experimental data, model logic, or previously reported numerical results.
