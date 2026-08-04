"""Causal normalized-margin and winner-persistence confidence gate."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CausalGateResult:
    """Per-sample outputs of an online confidence gate."""

    accepted: np.ndarray
    predicted_labels: np.ndarray
    decision_steps: np.ndarray
    confidence_at_decision: np.ndarray
    winner_history: np.ndarray
    normalized_margin_history: np.ndarray


def normalized_top_two_margin(
    score_history: np.ndarray,
    eps: float = 1e-12,
) -> np.ndarray:
    """Return the proposal's normalized top-two margin at every time step."""

    scores = np.asarray(score_history, dtype=float)
    if scores.ndim != 3:
        raise ValueError(
            "score_history must have shape "
            "(num_samples, num_time_steps, num_classes)."
        )
    if scores.shape[2] < 2:
        raise ValueError("At least two classes are required for a top-two margin.")
    if not np.all(np.isfinite(scores)):
        raise ValueError("score_history must contain only finite values.")
    if eps <= 0.0:
        raise ValueError("eps must be positive.")

    top_two = np.partition(scores, kth=scores.shape[2] - 2, axis=2)[:, :, -2:]
    top_1 = top_two[:, :, 1]
    top_2 = top_two[:, :, 0]
    denominator = np.abs(top_1) + np.abs(top_2) + eps
    return (top_1 - top_2) / denominator


def causal_margin_persistence_gate(
    score_history: np.ndarray,
    threshold: float,
    persistence: int,
    eps: float = 1e-12,
) -> CausalGateResult:
    """Accept the first decision meeting margin and winner persistence.

    A sample is accepted at time t only when the same winning class has held a
    normalized margin at least threshold for persistence consecutive observed
    time steps. The loop stops at the first accepted step and never inspects
    future states to revise that decision.
    """

    scores = np.asarray(score_history, dtype=float)
    margins = normalized_top_two_margin(scores, eps=eps)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must lie in [0, 1].")
    if isinstance(persistence, bool) or not isinstance(persistence, (int, np.integer)):
        raise TypeError("persistence must be an integer.")
    if persistence <= 0:
        raise ValueError("persistence must be positive.")

    winners = np.argmax(scores, axis=2).astype(int)
    num_samples, num_time_steps = margins.shape
    accepted = np.zeros(num_samples, dtype=bool)
    predicted_labels = np.full(num_samples, -1, dtype=int)
    decision_steps = np.full(num_samples, -1, dtype=int)
    confidence_at_decision = np.full(num_samples, np.nan, dtype=float)

    for sample_index in range(num_samples):
        run_length = 0
        previous_winner = -1

        for time_index in range(num_time_steps):
            current_winner = int(winners[sample_index, time_index])
            current_margin = float(margins[sample_index, time_index])

            if current_margin >= threshold:
                if current_winner == previous_winner:
                    run_length += 1
                else:
                    run_length = 1
                previous_winner = current_winner
            else:
                run_length = 0
                previous_winner = -1

            if run_length >= persistence:
                accepted[sample_index] = True
                predicted_labels[sample_index] = current_winner
                decision_steps[sample_index] = time_index + 1
                confidence_at_decision[sample_index] = current_margin
                break

    return CausalGateResult(
        accepted=accepted,
        predicted_labels=predicted_labels,
        decision_steps=decision_steps,
        confidence_at_decision=confidence_at_decision,
        winner_history=winners,
        normalized_margin_history=margins,
    )

