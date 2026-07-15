# Handoff 022 — Phase 2 Proposal Technical Rewrite

## Branch

```text
rewrite-phase02-proposal-technical-depth
```

## Objective

Replace the initial weak Phase 2 proposal text with a technically rigorous graduate-level proposal that remains a direct continuation of the completed Phase 1 DOA-sector inference project.

The rewrite preserves the existing LaTeX template and changes only project-specific front matter and proposal content. No `setup/` files, template macros, title-page structure, or bibliography configuration were modified in this branch.

## Scientific Continuity

Phase 2 is not a separate radar or SNN project. It begins from the completed Phase 1 reference pipeline:

```text
ULA snapshot simulation
→ sample covariance estimation
→ nine-point beamspace feature extraction
→ training-set normalization
→ nearest-centroid classification
→ Bernoulli rate encoding
→ LIF-inspired temporal class accumulation
```

Phase 1 established feasibility with the following documented reference results:

```text
Nearest-centroid overall accuracy: 86.90%
Best Phase 1 LIF accuracy:         84.17%
Accuracy retention:                approximately 96.8%
```

Phase 2 moves from feasibility to robustness and comparative evaluation.

## Central Research Problem

```text
How robust is the completed Phase 1 spike-based DOA-sector inference
pipeline to low SNR, sector-boundary ambiguity, and modest array-model
mismatch, and how does its accuracy–latency behavior compare with
classical and continuous-valued inference references evaluated on the
same data?
```

## Phase 2 Stress Factors

The proposal defines a controlled stress vector

```text
eta = [SNR, boundary distance, gain-error standard deviation,
       phase-error standard deviation]
```

The planned stress mechanisms are:

1. Extended low-SNR evaluation, including a new `-15 dB` condition.
2. Controlled angular offsets from the internal sector boundaries at `-30°`, `0°`, and `30°`.
3. Test-time element-level gain and phase mismatch while the inference and beamspace models remain nominal.

## Comparable Inference Paths

All methods are evaluated on identical test samples:

1. Bartlett spatial-spectrum peak mapped to a Phase 1 sector.
2. Continuous nearest-centroid classification on normalized beamspace features.
3. Rate-coded LIF-inspired temporal inference using centroid-derived class weights and biases.

The proposal does not claim that the spike-based path must outperform the classical or continuous paths in raw accuracy. Its engineering value is evaluated through accuracy retention, stable-decision latency, spike activity, temporal controllability, and suitability for later hardware-oriented implementation.

## Research Questions and Hypotheses

The proposal defines four research questions:

1. Low-SNR robustness.
2. Sector-boundary ambiguity.
3. Array-model mismatch.
4. Accuracy–latency retention under stress.

The corresponding hypotheses predict lower accuracy and longer LIF stabilization at low SNR, increased error near sector boundaries, measurable degradation under gain/phase mismatch, and partial recovery through longer temporal windows and stronger membrane retention.

## Experimental Plan

The proposal defines six numbered runs:

```text
Run 001 — Phase 1 Reference Reproduction
Run 002 — Extended Low-SNR Evaluation
Run 003 — Sector-Boundary Stress Test
Run 004 — Array-Model Mismatch Evaluation
Run 005 — LIF Operating-Point Sweep Under Stress
Run 006 — Integrated Phase 2 Case Study
```

Each run must preserve configuration values, fixed or explicitly recorded random seeds, source-code revision, numerical outputs, figures, and console summaries.

## Metrics

The proposal requires the following metrics where applicable:

```text
overall accuracy
balanced accuracy
accuracy versus SNR
accuracy versus boundary distance
confusion matrices
mean and distributional stable-decision latency
mean spike count
mean firing rate
relative degradation from nominal performance
LIF-to-continuous accuracy-retention ratio
```

Stable-decision latency remains an algorithmic time-step proxy and is not reported as measured FPGA or processor execution time.

## Technical Method Alignment

The rewritten methodology was checked against the actual Phase 1 implementation.

The LIF class templates remain

```text
w_c = 2 mu_c
b_c = -||mu_c||^2
```

and the temporal state update remains

```text
v_c[t] = alpha v_c[t-1] + w_c^T z[t] + b_c
```

The rate encoder remains Bernoulli encoding of normalized feature values in `[0, 1]`.

Training-set statistics alone are used for normalization, centroid fitting, and class-template construction. Test-set information must not enter these fitting stages.

## Success Criteria

The proposal defines measurable completion criteria, including:

- reproduction of Phase 1 nearest-centroid and LIF accuracies within one percentage point;
- reproduction of Phase 1 mean latency within 10 percent under the same configuration;
- common-sample comparison of Bartlett, continuous, and LIF paths;
- at least three nonzero array-mismatch levels;
- a boundary-distance analysis;
- a Pareto-relevant LIF operating point for later fixed-point, PYNQ, or Vitis HLS work;
- traceability of every reported result to a named run and stored artifact.

## Files Rewritten

```text
docs/reports/phase_02_latex/proposal/frontmatter/objective.tex
docs/reports/phase_02_latex/proposal/frontmatter/abstract.tex

docs/reports/phase_02_latex/proposal/content/01_introduction.tex
docs/reports/phase_02_latex/proposal/content/02_background_and_phase_01_summary.tex
docs/reports/phase_02_latex/proposal/content/03_problem_statement.tex
docs/reports/phase_02_latex/proposal/content/04_proposed_phase_02_scope.tex
docs/reports/phase_02_latex/proposal/content/05_technical_objectives.tex
docs/reports/phase_02_latex/proposal/content/06_methodology.tex
docs/reports/phase_02_latex/proposal/content/07_experimental_plan.tex
docs/reports/phase_02_latex/proposal/content/08_expected_results_and_deliverables.tex
docs/reports/phase_02_latex/proposal/content/09_project_timeline.tex
docs/reports/phase_02_latex/proposal/content/10_risks_and_limitations.tex
docs/reports/phase_02_latex/proposal/content/11_conclusion.tex
```

## LaTeX and Overleaf Workflow

The established workflow for this project is:

```text
1. Make and review text changes on a GitHub feature branch.
2. Pull the branch into the local repository.
3. Copy only the changed `.tex` files from local into Overleaf.
4. Compile and inspect the complete PDF in Overleaf.
5. Return corrections to the same GitHub feature branch.
6. Create the handoff and index entry.
7. Open, review, and merge the pull request.
8. Synchronize local `main` after merge.
```

This workflow is preferred over local bibliography compilation because the local Biber process is unreliable, while Overleaf successfully compiles the established `biblatex`/Biber configuration.

## Quality-Control Note

During the rewrite, two files were detected as truncated after remote writes:

```text
content/03_problem_statement.tex
content/06_methodology.tex
```

Both were immediately rewritten in full and re-read from the branch to verify complete contents before this handoff was created.

## Scope Boundaries

Phase 2 does not claim:

- a new high-resolution DOA algorithm;
- a complete radar signal chain;
- measured real-hardware robustness;
- measured power or energy savings;
- biologically detailed SNN behavior;
- completed FPGA, PYNQ, or Vitis HLS deployment.

The output of Phase 2 is a controlled robustness benchmark and a justified operating point for later embedded implementation.

## Current Status

```text
Phase 2 scientific proposal rewrite: complete
Overleaf content review: completed by the user
Handoff 022: created
Handoff index: to be updated in the same branch
Next repository action: open and merge the proposal-rewrite pull request
```

## Next Technical Step After Merge

Begin Phase 2 Run 001 by reproducing the Phase 1 reference point inside the Phase 2 experiment structure before adding any new stress model.