"""Calibration diagnostics for confidence-aware fast-slow DOA inference.

This module is deliberately analysis-only. It summarizes whether a scalar
confidence signal separates correct and incorrect fast-path decisions and
evaluates causal gate operating points, but it does not select a gate or touch
the sealed holdout seeds.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

import numpy as np

from .adaptive_controller import adaptive_metrics, compose_adaptive_decisions
from .confidence_gate import (
    causal_margin_persistence_gate,
    normalized_top_two_margin,
)


def winner_run_lengths(winner_history: np.ndarray) -> np.ndarray:
    """Return the causal consecutive-run length of each winning class."""

    winners = np.asarray(winner_history)
    if winners.ndim != 2:
        raise ValueError("winner_history must have shape (samples, time_steps).")
    if winners.shape[1] <= 0:
        raise ValueError("winner_history must contain at least one time step.")

    run_lengths = np.ones(winners.shape, dtype=int)
    for time_index in range(1, winners.shape[1]):
        same_winner = winners[:, time_index] == winners[:, time_index - 1]
        run_lengths[:, time_index] = np.where(
            same_winner,
            run_lengths[:, time_index - 1] + 1,
            1,
        )
    return run_lengths


def stable_winner_step(winner_history: np.ndarray) -> np.ndarray:
    """Return the first one-indexed step after which the final winner is stable."""

    winners = np.asarray(winner_history)
    if winners.ndim != 2 or winners.shape[1] <= 0:
        raise ValueError(
            "winner_history must have shape (samples, positive_time_steps)."
        )
    final_winner = winners[:, -1]
    stable_step = np.full(winners.shape[0], winners.shape[1], dtype=int)
    for sample_index in range(winners.shape[0]):
        matches_final = winners[sample_index] == final_winner[sample_index]
        for time_index in range(winners.shape[1]):
            if np.all(matches_final[time_index:]):
                stable_step[sample_index] = time_index + 1
                break
    return stable_step


def sample_confidence_diagnostics(
    score_history: np.ndarray,
    shared_spikes: np.ndarray,
    true_labels: np.ndarray,
) -> dict[str, np.ndarray]:
    """Extract per-sample margin, persistence, timing, and activity signals."""

    scores = np.asarray(score_history, dtype=float)
    spikes = np.asarray(shared_spikes)
    truth = np.asarray(true_labels, dtype=int)
    if scores.ndim != 3:
        raise ValueError("score_history must have shape (samples, time, classes).")
    if spikes.ndim != 3 or spikes.shape[:2] != scores.shape[:2]:
        raise ValueError("shared_spikes must align with score_history samples/time.")
    if truth.shape != (scores.shape[0],):
        raise ValueError("true_labels must have shape (samples,).")
    if scores.shape[0] <= 0 or scores.shape[1] <= 0:
        raise ValueError("At least one sample and one time step are required.")
    if not np.all((spikes == 0) | (spikes == 1)):
        raise ValueError("shared_spikes must be binary.")

    winners = np.argmax(scores, axis=2).astype(int)
    margins = normalized_top_two_margin(scores)
    persistence = winner_run_lengths(winners)
    cumulative_spikes = np.cumsum(spikes.sum(axis=2, dtype=int), axis=1)
    final_prediction = winners[:, -1]

    return {
        "final_prediction": final_prediction,
        "fast_correct": final_prediction == truth,
        "final_margin": margins[:, -1],
        "maximum_margin": np.max(margins, axis=1),
        "final_winner_persistence": persistence[:, -1],
        "maximum_winner_persistence": np.max(persistence, axis=1),
        "stable_winner_step": stable_winner_step(winners),
        "final_spike_count": cumulative_spikes[:, -1],
        "mean_firing_rate": spikes.mean(axis=(1, 2)),
    }


def reliability_rows(
    confidence: np.ndarray,
    correct: np.ndarray,
    bin_edges: Sequence[float],
) -> list[dict[str, float | int]]:
    """Return equal-width reliability rows for a bounded confidence signal."""

    values = np.asarray(confidence, dtype=float)
    outcomes = np.asarray(correct, dtype=bool)
    edges = np.asarray(tuple(bin_edges), dtype=float)
    if values.ndim != 1 or outcomes.shape != values.shape or values.size <= 0:
        raise ValueError("confidence and correct must be aligned non-empty vectors.")
    if not np.all(np.isfinite(values)) or np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("confidence must contain finite values in [0, 1].")
    if edges.ndim != 1 or edges.size < 2 or not np.all(np.diff(edges) > 0.0):
        raise ValueError("bin_edges must be a strictly increasing vector.")
    if not np.isclose(edges[0], 0.0) or not np.isclose(edges[-1], 1.0):
        raise ValueError("bin_edges must span [0, 1].")

    rows: list[dict[str, float | int]] = []
    for bin_index, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        if bin_index == edges.size - 2:
            mask = (values >= lower) & (values <= upper)
        else:
            mask = (values >= lower) & (values < upper)
        count = int(np.sum(mask))
        rows.append(
            {
                "bin_index": bin_index,
                "lower": float(lower),
                "upper": float(upper),
                "count": count,
                "mean_confidence": float(np.mean(values[mask])) if count else float("nan"),
                "observed_accuracy": float(np.mean(outcomes[mask])) if count else float("nan"),
            }
        )
    if sum(int(row["count"]) for row in rows) != values.size:
        raise RuntimeError("Reliability bins did not account for every sample.")
    return rows


def expected_calibration_error(
    rows: Sequence[Mapping[str, float | int]],
) -> float:
    """Compute count-weighted absolute reliability error."""

    total = sum(int(row["count"]) for row in rows)
    if total <= 0:
        raise ValueError("Reliability rows must contain at least one sample.")
    error = 0.0
    for row in rows:
        count = int(row["count"])
        if count:
            error += count * abs(
                float(row["mean_confidence"])
                - float(row["observed_accuracy"])
            )
    return error / total


def risk_coverage_rows(
    confidence: np.ndarray,
    correct: np.ndarray,
    requested_coverages: Iterable[float],
) -> list[dict[str, float | int]]:
    """Rank samples by confidence and compute descriptive selective risk."""

    values = np.asarray(confidence, dtype=float)
    outcomes = np.asarray(correct, dtype=bool)
    requested = tuple(float(value) for value in requested_coverages)
    if values.ndim != 1 or outcomes.shape != values.shape or values.size <= 0:
        raise ValueError("confidence and correct must be aligned non-empty vectors.")
    if not np.all(np.isfinite(values)):
        raise ValueError("confidence must be finite.")
    if not requested or any(value <= 0.0 or value > 1.0 for value in requested):
        raise ValueError("requested_coverages must lie in (0, 1].")
    if any(requested[index + 1] <= requested[index] for index in range(len(requested) - 1)):
        raise ValueError("requested_coverages must be strictly increasing.")

    # Stable sorting makes ties deterministic without inventing tie-breaking
    # information from labels.
    order = np.argsort(-values, kind="mergesort")
    rows: list[dict[str, float | int]] = []
    for requested_coverage in requested:
        selected_count = min(
            values.size,
            max(1, int(np.ceil(requested_coverage * values.size))),
        )
        selected = order[:selected_count]
        selective_accuracy = float(np.mean(outcomes[selected]))
        rows.append(
            {
                "requested_coverage": requested_coverage,
                "realized_coverage": selected_count / values.size,
                "selected_count": selected_count,
                "confidence_cutoff": float(values[order[selected_count - 1]]),
                "selective_accuracy": selective_accuracy,
                "selective_risk": 1.0 - selective_accuracy,
            }
        )
    return rows


def binary_auroc(confidence: np.ndarray, correct: np.ndarray) -> float:
    """Return tie-aware AUROC for confidence predicting fast correctness."""

    values = np.asarray(confidence, dtype=float)
    outcomes = np.asarray(correct, dtype=bool)
    if values.ndim != 1 or outcomes.shape != values.shape or values.size <= 0:
        raise ValueError("confidence and correct must be aligned non-empty vectors.")
    if not np.all(np.isfinite(values)):
        raise ValueError("confidence must be finite.")
    positive_count = int(np.sum(outcomes))
    negative_count = int(values.size - positive_count)
    if positive_count == 0 or negative_count == 0:
        return float("nan")

    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(values.size, dtype=float)
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and sorted_values[stop] == sorted_values[start]:
            stop += 1
        average_rank = 0.5 * ((start + 1) + stop)
        ranks[order[start:stop]] = average_rank
        start = stop
    positive_rank_sum = float(np.sum(ranks[outcomes]))
    return (
        positive_rank_sum - positive_count * (positive_count + 1) / 2.0
    ) / (positive_count * negative_count)


def evaluate_causal_operating_point(
    score_history: np.ndarray,
    shared_spikes: np.ndarray,
    true_labels: np.ndarray,
    fallback_predictions: np.ndarray,
    threshold: float,
    persistence: int,
    fast_budget: int,
    full_budget: int,
) -> dict[str, float | int]:
    """Evaluate one causal gate without selecting or calibrating it."""

    gate = causal_margin_persistence_gate(
        score_history,
        threshold=threshold,
        persistence=persistence,
    )
    decisions = compose_adaptive_decisions(
        gate,
        fallback_predictions,
        shared_spikes,
        initial_snapshot_budget=fast_budget,
        full_snapshot_budget=full_budget,
    )
    return {
        "threshold": float(threshold),
        "persistence": int(persistence),
        **adaptive_metrics(true_labels, gate, decisions),
    }


def validate_seed_protocol(config: Mapping[str, object]) -> dict[str, bool]:
    """Validate calibration/holdout separation and Day 5 non-reuse."""

    def pairs(key: str) -> tuple[tuple[int, int], ...]:
        raw = config[key]
        return tuple(
            (int(item["dataset_seed"]), int(item["spike_seed"]))
            for item in raw
        )

    frozen = pairs("frozen_day_05_seed_pairs")
    calibration = pairs("calibration_seed_pairs")
    holdout = pairs("holdout_seed_pairs")
    frozen_dataset = {item[0] for item in frozen}
    frozen_spike = {item[1] for item in frozen}
    calibration_dataset = {item[0] for item in calibration}
    calibration_spike = {item[1] for item in calibration}
    holdout_dataset = {item[0] for item in holdout}
    holdout_spike = {item[1] for item in holdout}

    checks = {
        "five_unique_calibration_pairs": (
            len(calibration) == 5
            and len(set(calibration)) == 5
            and len(calibration_dataset) == 5
            and len(calibration_spike) == 5
        ),
        "five_unique_holdout_pairs": (
            len(holdout) == 5
            and len(set(holdout)) == 5
            and len(holdout_dataset) == 5
            and len(holdout_spike) == 5
        ),
        "calibration_holdout_disjoint": (
            calibration_dataset.isdisjoint(holdout_dataset)
            and calibration_spike.isdisjoint(holdout_spike)
        ),
        "day_05_seeds_not_reused": (
            frozen_dataset.isdisjoint(calibration_dataset | holdout_dataset)
            and frozen_spike.isdisjoint(calibration_spike | holdout_spike)
        ),
        "holdout_policy_is_sealed": (
            str(config["holdout_policy"]) == "sealed_until_day_09"
        ),
    }
    if not all(checks.values()):
        failed = ", ".join(key for key, passed in checks.items() if not passed)
        raise ValueError(f"Invalid Day 7 seed protocol: {failed}")
    return checks
