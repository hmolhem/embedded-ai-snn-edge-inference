"""Create report-ready Day 6 figures and tables from frozen Day 5 outputs.

This module performs descriptive analysis only. It does not train a model,
change the pre-registered gate, or select a new operating point.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "embedded_ai_matplotlib"),
)

import matplotlib.pyplot as plt
import numpy as np


PACKAGE_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = PACKAGE_ROOT / "results"
FIGURES_DIR = PACKAGE_ROOT / "figures"

PER_SEED_PATH = RESULTS_DIR / "day_05_per_seed_metrics.csv"
AGGREGATE_PATH = RESULTS_DIR / "day_05_aggregate_metrics.csv"
DAY_05_SUMMARY_PATH = RESULTS_DIR / "day_05_stress_test_summary.json"
DAY_05_CONFIG_PATH = PACKAGE_ROOT / "day_05_stress_config.json"

METHOD_ORDER = ("always_fast", "always_continuous", "adaptive")
METHOD_LABELS = {
    "always_fast": "Always fast",
    "always_continuous": "Always continuous",
    "adaptive": "Adaptive",
}
METHOD_COLORS = {
    "always_fast": "#D97706",
    "always_continuous": "#2563EB",
    "adaptive": "#059669",
}
METHOD_MARKERS = {
    "always_fast": "o",
    "always_continuous": "s",
    "adaptive": "^",
}

NUMERIC_METRICS = (
    "accuracy",
    "coverage",
    "selective_accuracy",
    "false_confidence_rate",
    "false_acceptance_probability",
    "fallback_rate",
    "average_snapshots",
    "average_lif_steps",
    "average_spike_count",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _as_float(row: Mapping[str, str], key: str) -> float:
    return float(row[key])


def _parse_condition(condition: str) -> float:
    mismatch_order = {
        "nominal": 0.0,
        "mild": 1.0,
        "moderate": 2.0,
        "severe": 3.0,
    }
    if condition in mismatch_order:
        return mismatch_order[condition]
    return float(condition.replace("_db", "").replace("_deg", ""))


def _single_row(
    rows: Iterable[Mapping[str, str]],
    experiment: str,
    condition: str,
    method: str,
) -> Mapping[str, str]:
    matches = [
        row
        for row in rows
        if row["experiment"] == experiment
        and row["condition"] == condition
        and row["method"] == method
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one aggregate row for {experiment}/{condition}/{method}; "
            f"found {len(matches)}."
        )
    return matches[0]


def _ordered_rows(
    rows: Iterable[Mapping[str, str]],
    experiment: str,
    method: str,
) -> list[Mapping[str, str]]:
    selected = [
        row
        for row in rows
        if row["experiment"] == experiment and row["method"] == method
    ]
    return sorted(selected, key=lambda row: _parse_condition(row["condition"]))


def _validate_inputs(
    per_seed: list[Mapping[str, str]],
    aggregate: list[Mapping[str, str]],
    config: Mapping[str, object],
    day_05_summary: Mapping[str, object],
) -> dict[str, bool]:
    expected_conditions = {
        "snr": 8,
        "array_mismatch": 4,
        "boundary_offset": 10,
    }
    expected_rows = sum(count * len(METHOD_ORDER) for count in expected_conditions.values())
    aggregate_shape_ok = len(aggregate) == expected_rows

    groups: dict[tuple[str, str, str], list[Mapping[str, str]]] = defaultdict(list)
    for row in per_seed:
        groups[(row["experiment"], row["condition"], row["method"])].append(row)

    group_count_ok = len(groups) == expected_rows
    five_seeds_ok = all(len(group_rows) == 5 for group_rows in groups.values())
    methods_ok = {
        row["method"] for row in aggregate
    } == set(METHOD_ORDER)

    aggregates_match = True
    tolerance = 1e-12
    for row in aggregate:
        group = groups[(row["experiment"], row["condition"], row["method"])]
        for metric in NUMERIC_METRICS:
            values = np.asarray([float(item[metric]) for item in group], dtype=float)
            finite = values[np.isfinite(values)]
            observed_mean = float(row[f"{metric}_mean"])
            observed_std = float(row[f"{metric}_std"])
            if finite.size == 0:
                if not (np.isnan(observed_mean) and np.isnan(observed_std)):
                    aggregates_match = False
            else:
                expected_mean = float(np.mean(finite))
                expected_std = float(np.std(finite, ddof=1)) if finite.size > 1 else 0.0
                if not np.isclose(observed_mean, expected_mean, atol=tolerance, rtol=0.0):
                    aggregates_match = False
                if not np.isclose(observed_std, expected_std, atol=tolerance, rtol=0.0):
                    aggregates_match = False

    gate = config["gate"]
    operating_point = day_05_summary["pre_registered_operating_point"]
    operating_point_frozen = (
        float(gate["threshold"]) == float(operating_point["threshold"])
        and int(gate["persistence"]) == int(operating_point["persistence"])
        and int(config["snapshot_budgets"]["fast"]) == int(operating_point["fast_budget"])
        and int(config["snapshot_budgets"]["full"]) == int(operating_point["full_budget"])
        and int(config["lif"]["t_max"]) == int(operating_point["t_max"])
        and float(config["lif"]["leak"]) == float(operating_point["leak"])
    )

    checks = {
        "day_05_summary_passed": bool(day_05_summary["all_checks_pass"]),
        "aggregate_row_count": aggregate_shape_ok,
        "per_seed_group_count": group_count_ok,
        "five_rows_per_group": five_seeds_ok,
        "all_three_methods_present": methods_ok,
        "aggregate_statistics_reproduce": aggregates_match,
        "operating_point_matches_frozen_config": operating_point_frozen,
        "descriptive_analysis_only": True,
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"Day 6 input validation failed: {failed}")
    return checks


def _style_axis(axis: plt.Axes, ylabel: str) -> None:
    axis.set_ylabel(ylabel)
    axis.grid(axis="y", alpha=0.22, linewidth=0.8)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def _save_figure(figure: plt.Figure, stem: str) -> list[Path]:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [FIGURES_DIR / f"{stem}.png", FIGURES_DIR / f"{stem}.pdf"]
    figure.savefig(
        outputs[0],
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Phase 2 Day 6 visualization pipeline"},
    )
    figure.savefig(
        outputs[1],
        bbox_inches="tight",
        facecolor="white",
        metadata={
            "Creator": "Phase 2 Day 6 visualization pipeline",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    plt.close(figure)
    return outputs


def _nominal_figure(aggregate: list[Mapping[str, str]]) -> list[Path]:
    rows = {
        method: _single_row(aggregate, "array_mismatch", "nominal", method)
        for method in METHOD_ORDER
    }
    labels = [METHOD_LABELS[method] for method in METHOD_ORDER]
    colors = [METHOD_COLORS[method] for method in METHOD_ORDER]
    x = np.arange(len(METHOD_ORDER))

    figure, axes = plt.subplots(1, 2, figsize=(10.2, 4.0), constrained_layout=True)
    accuracy = [_as_float(rows[method], "accuracy_mean") for method in METHOD_ORDER]
    accuracy_std = [_as_float(rows[method], "accuracy_std") for method in METHOD_ORDER]
    axes[0].bar(x, accuracy, yerr=accuracy_std, capsize=4, color=colors, width=0.68)
    axes[0].set_xticks(x, labels)
    axes[0].set_ylim(0.0, 1.0)
    _style_axis(axes[0], "Accuracy")
    axes[0].set_title("Five-seed nominal accuracy")
    for index, value in enumerate(accuracy):
        axes[0].text(index, value + accuracy_std[index] + 0.025, f"{value:.3f}", ha="center")

    snapshots = [
        _as_float(rows[method], "average_snapshots_mean") for method in METHOD_ORDER
    ]
    snapshot_std = [
        _as_float(rows[method], "average_snapshots_std") for method in METHOD_ORDER
    ]
    axes[1].bar(x, snapshots, yerr=snapshot_std, capsize=4, color=colors, width=0.68)
    axes[1].set_xticks(x, labels)
    axes[1].set_ylim(0.0, 140.0)
    axes[1].axhline(128.0, color="#64748B", linestyle="--", linewidth=1.1)
    _style_axis(axes[1], "Average snapshots")
    axes[1].set_title("Realized sensing cost")
    for index, value in enumerate(snapshots):
        axes[1].text(index, value + snapshot_std[index] + 4.0, f"{value:.1f}", ha="center")

    figure.suptitle(
        "Day 5 nominal result: accuracy is preserved, but fallback dominates\n"
        "Error bars show +/- 1 SD across five seed pairs",
        fontsize=12,
        fontweight="bold",
    )
    return _save_figure(figure, "day_06_nominal_accuracy_and_cost")


def _stress_figure(
    aggregate: list[Mapping[str, str]],
    experiment: str,
    stem: str,
    title: str,
    xlabel: str,
    tick_labels: list[str] | None = None,
) -> list[Path]:
    figure, axes = plt.subplots(3, 1, figsize=(8.4, 9.0), sharex=True, constrained_layout=True)

    x_values: np.ndarray | None = None
    for method in METHOD_ORDER:
        rows = _ordered_rows(aggregate, experiment, method)
        x = np.asarray([_parse_condition(row["condition"]) for row in rows], dtype=float)
        mean = np.asarray([_as_float(row, "accuracy_mean") for row in rows])
        std = np.asarray([_as_float(row, "accuracy_std") for row in rows])
        x_values = x
        axes[0].plot(
            x,
            mean,
            label=METHOD_LABELS[method],
            color=METHOD_COLORS[method],
            marker=METHOD_MARKERS[method],
            linewidth=2.0,
            markersize=5,
        )
        axes[0].fill_between(x, mean - std, mean + std, color=METHOD_COLORS[method], alpha=0.12)

    adaptive_rows = _ordered_rows(aggregate, experiment, "adaptive")
    adaptive_x = np.asarray(
        [_parse_condition(row["condition"]) for row in adaptive_rows], dtype=float
    )
    coverage = np.asarray([_as_float(row, "coverage_mean") for row in adaptive_rows])
    coverage_std = np.asarray([_as_float(row, "coverage_std") for row in adaptive_rows])
    snapshots = np.asarray(
        [_as_float(row, "average_snapshots_mean") for row in adaptive_rows]
    )
    snapshots_std = np.asarray(
        [_as_float(row, "average_snapshots_std") for row in adaptive_rows]
    )

    axes[1].plot(adaptive_x, coverage, color=METHOD_COLORS["adaptive"], marker="o", linewidth=2.0)
    axes[1].fill_between(
        adaptive_x,
        np.maximum(coverage - coverage_std, 0.0),
        np.minimum(coverage + coverage_std, 1.0),
        color=METHOD_COLORS["adaptive"],
        alpha=0.14,
    )
    axes[2].plot(adaptive_x, snapshots, color=METHOD_COLORS["adaptive"], marker="o", linewidth=2.0)
    axes[2].fill_between(
        adaptive_x,
        snapshots - snapshots_std,
        snapshots + snapshots_std,
        color=METHOD_COLORS["adaptive"],
        alpha=0.14,
    )
    axes[2].axhline(128.0, color="#64748B", linestyle="--", linewidth=1.1, label="Full fallback")

    axes[0].set_ylim(0.0, 1.0)
    axes[1].set_ylim(0.0, max(0.12, float(np.max(coverage + coverage_std)) * 1.25))
    axes[2].set_ylim(110.0, 130.0)
    _style_axis(axes[0], "Accuracy")
    _style_axis(axes[1], "Adaptive coverage")
    _style_axis(axes[2], "Average snapshots")
    axes[0].legend(ncol=3, frameon=False, loc="lower right")
    axes[2].legend(frameon=False, loc="lower right")
    axes[2].set_xlabel(xlabel)
    axes[0].set_title("Performance")
    axes[1].set_title("Gate acceptance")
    axes[2].set_title("Realized sensing cost")
    if tick_labels is not None and x_values is not None:
        axes[2].set_xticks(x_values, tick_labels)
    figure.suptitle(
        title + "\nShaded bands show +/- 1 SD across five seed pairs",
        fontsize=12,
        fontweight="bold",
    )
    return _save_figure(figure, stem)


def _markdown_value(mean: float, std: float, digits: int = 4) -> str:
    if not np.isfinite(mean):
        return "N/A"
    if not np.isfinite(std):
        return f"{mean:.{digits}f}"
    return f"{mean:.{digits}f} +/- {std:.{digits}f}"


def _write_tables(
    aggregate: list[Mapping[str, str]],
    input_hashes: Mapping[str, str],
) -> Path:
    nominal = {
        method: _single_row(aggregate, "array_mismatch", "nominal", method)
        for method in METHOD_ORDER
    }
    severe = {
        method: _single_row(aggregate, "array_mismatch", "severe", method)
        for method in METHOD_ORDER
    }

    lines = [
        "# Day 6 Frozen-Result Tables",
        "",
        "These tables are generated only from the fixed Day 5 outputs. No threshold,",
        "persistence, model parameter, or operating point is reselected here.",
        "",
        "## Frozen input hashes",
        "",
        "| Input | SHA-256 |",
        "|---|---|",
    ]
    for name, digest in input_hashes.items():
        lines.append(f"| `{name}` | `{digest}` |")

    lines.extend(
        [
            "",
            "## Nominal five-seed summary",
            "",
            "| Method | Accuracy | Coverage | Selective accuracy | Fallback rate | Avg. snapshots | Avg. LIF steps |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for method in METHOD_ORDER:
        row = nominal[method]
        lines.append(
            "| "
            + METHOD_LABELS[method]
            + " | "
            + _markdown_value(_as_float(row, "accuracy_mean"), _as_float(row, "accuracy_std"))
            + " | "
            + _markdown_value(_as_float(row, "coverage_mean"), _as_float(row, "coverage_std"))
            + " | "
            + _markdown_value(
                _as_float(row, "selective_accuracy_mean"),
                _as_float(row, "selective_accuracy_std"),
            )
            + " | "
            + _markdown_value(_as_float(row, "fallback_rate_mean"), _as_float(row, "fallback_rate_std"))
            + " | "
            + _markdown_value(
                _as_float(row, "average_snapshots_mean"),
                _as_float(row, "average_snapshots_std"),
                digits=2,
            )
            + " | "
            + _markdown_value(
                _as_float(row, "average_lif_steps_mean"),
                _as_float(row, "average_lif_steps_std"),
                digits=2,
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Selected stress endpoints",
            "",
            "| Stress condition | Method | Accuracy | Coverage | Avg. snapshots |",
            "|---|---|---:|---:|---:|",
        ]
    )
    endpoints = [
        ("SNR -15 dB", "snr", "-15_db"),
        ("SNR 0 dB", "snr", "0_db"),
        ("SNR 20 dB", "snr", "20_db"),
        ("Boundary -0.5 deg", "boundary_offset", "-0.5_deg"),
        ("Boundary +0.5 deg", "boundary_offset", "+0.5_deg"),
        ("Boundary -10 deg", "boundary_offset", "-10_deg"),
        ("Boundary +10 deg", "boundary_offset", "+10_deg"),
    ]
    for label, experiment, condition in endpoints:
        for method in ("always_continuous", "adaptive"):
            row = _single_row(aggregate, experiment, condition, method)
            lines.append(
                f"| {label} | {METHOD_LABELS[method]} | "
                f"{_markdown_value(_as_float(row, 'accuracy_mean'), _as_float(row, 'accuracy_std'))} | "
                f"{_markdown_value(_as_float(row, 'coverage_mean'), _as_float(row, 'coverage_std'))} | "
                f"{_markdown_value(_as_float(row, 'average_snapshots_mean'), _as_float(row, 'average_snapshots_std'), digits=2)} |"
            )

    lines.extend(
        [
            "",
            "## Array-mismatch endpoint",
            "",
            "| Method | Nominal accuracy | Severe accuracy | Drop |",
            "|---|---:|---:|---:|",
        ]
    )
    for method in METHOD_ORDER:
        nominal_accuracy = _as_float(nominal[method], "accuracy_mean")
        severe_accuracy = _as_float(severe[method], "accuracy_mean")
        lines.append(
            f"| {METHOD_LABELS[method]} | {nominal_accuracy:.4f} | "
            f"{severe_accuracy:.4f} | {nominal_accuracy - severe_accuracy:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "- The adaptive method preserves the continuous-baseline accuracy within the observed five-seed uncertainty.",
            "- The fixed gate accepts only a small fraction of cases, so average snapshots remain close to 128.",
            "- Low SNR and close boundary offsets are the dominant difficulty regimes.",
            "- Fixed array mismatch causes a smaller accuracy loss than low SNR or boundary proximity in this experiment.",
            "- These results describe the frozen Day 5 operating point; they do not justify gate retuning on the validation set.",
            "",
        ]
    )
    output = RESULTS_DIR / "day_06_report_tables.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def _key_findings(aggregate: list[Mapping[str, str]]) -> dict[str, object]:
    nominal_adaptive = _single_row(
        aggregate, "array_mismatch", "nominal", "adaptive"
    )
    nominal_continuous = _single_row(
        aggregate, "array_mismatch", "nominal", "always_continuous"
    )
    severe_adaptive = _single_row(
        aggregate, "array_mismatch", "severe", "adaptive"
    )
    low_snr_adaptive = _single_row(aggregate, "snr", "-15_db", "adaptive")
    return {
        "nominal_adaptive_accuracy": _as_float(nominal_adaptive, "accuracy_mean"),
        "nominal_continuous_accuracy": _as_float(
            nominal_continuous, "accuracy_mean"
        ),
        "nominal_adaptive_coverage": _as_float(nominal_adaptive, "coverage_mean"),
        "nominal_adaptive_fallback_rate": _as_float(
            nominal_adaptive, "fallback_rate_mean"
        ),
        "nominal_adaptive_average_snapshots": _as_float(
            nominal_adaptive, "average_snapshots_mean"
        ),
        "snapshot_reduction_fraction": 1.0
        - _as_float(nominal_adaptive, "average_snapshots_mean") / 128.0,
        "low_snr_minus_15_db_accuracy": _as_float(
            low_snr_adaptive, "accuracy_mean"
        ),
        "low_snr_minus_15_db_coverage": _as_float(
            low_snr_adaptive, "coverage_mean"
        ),
        "adaptive_accuracy_drop_nominal_to_severe_mismatch": _as_float(
            nominal_adaptive, "accuracy_mean"
        )
        - _as_float(severe_adaptive, "accuracy_mean"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    per_seed = _read_csv(PER_SEED_PATH)
    aggregate = _read_csv(AGGREGATE_PATH)
    config = json.loads(DAY_05_CONFIG_PATH.read_text(encoding="utf-8"))
    day_05_summary = json.loads(DAY_05_SUMMARY_PATH.read_text(encoding="utf-8"))

    input_paths = (
        PER_SEED_PATH,
        AGGREGATE_PATH,
        DAY_05_SUMMARY_PATH,
        DAY_05_CONFIG_PATH,
    )
    input_hashes = {path.name: _sha256(path) for path in input_paths}
    checks = _validate_inputs(per_seed, aggregate, config, day_05_summary)

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "figure.dpi": 120,
        }
    )

    output_files: list[Path] = []
    output_files.extend(_nominal_figure(aggregate))
    output_files.extend(
        _stress_figure(
            aggregate,
            experiment="snr",
            stem="day_06_snr_stress",
            title="SNR stress: low SNR collapses confidence coverage",
            xlabel="SNR (dB)",
        )
    )
    output_files.extend(
        _stress_figure(
            aggregate,
            experiment="boundary_offset",
            stem="day_06_boundary_stress",
            title="Sector-boundary stress: ambiguity dominates near zero offset",
            xlabel="Signed offset from sector boundary (deg)",
        )
    )
    output_files.extend(
        _stress_figure(
            aggregate,
            experiment="array_mismatch",
            stem="day_06_array_mismatch_stress",
            title="Fixed-device array mismatch: degradation is modest",
            xlabel="Mismatch severity",
            tick_labels=["Nominal", "Mild", "Moderate", "Severe"],
        )
    )

    table_path = _write_tables(aggregate, input_hashes)
    output_files.append(table_path)
    output_hashes = {
        str(path.relative_to(PACKAGE_ROOT)): _sha256(path) for path in output_files
    }

    summary = {
        "checkpoint": "day_06_results_visualization",
        "analysis_policy": (
            "descriptive visualization of frozen Day 5 outputs; no retraining, "
            "threshold sweep, persistence sweep, or operating-point reselection"
        ),
        "frozen_operating_point": day_05_summary["pre_registered_operating_point"],
        "input_sha256": input_hashes,
        "output_sha256": output_hashes,
        "key_findings": _key_findings(aggregate),
        "validation": checks,
        "all_checks_pass": all(checks.values()),
    }
    summary_path = RESULTS_DIR / "day_06_results_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"Day 6 generated {len(output_files)} figure/table artifacts.")
    print(f"Summary: {summary_path}")
    print("All checks passed.")


if __name__ == "__main__":
    main()
