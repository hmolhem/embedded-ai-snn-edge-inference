"""Adaptive fast-slow decision composition and metric utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .confidence_gate import CausalGateResult


@dataclass(frozen=True)
class AdaptiveDecisionResult:
    """Per-sample decisions and realized sensing/inference activity."""

    final_predictions: np.ndarray
    used_fallback: np.ndarray
    snapshots_used: np.ndarray
    lif_steps_used: np.ndarray
    spike_counts_used: np.ndarray


def compose_adaptive_decisions(
    gate: CausalGateResult,
    fallback_predictions: np.ndarray,
    shared_spikes: np.ndarray,
    initial_snapshot_budget: int = 32,
    full_snapshot_budget: int = 128,
) -> AdaptiveDecisionResult:
    """Accept gated predictions and defer all other samples to fallback."""

    fallback = np.asarray(fallback_predictions, dtype=int)
    spikes = np.asarray(shared_spikes)
    num_samples = gate.accepted.size
    if fallback.shape != (num_samples,):
        raise ValueError("fallback_predictions must have shape (num_samples,).")
    if spikes.ndim != 3 or spikes.shape[0] != num_samples:
        raise ValueError(
            "shared_spikes must have shape "
            "(num_samples, num_time_steps, num_features)."
        )
    if not np.all((spikes == 0) | (spikes == 1)):
        raise ValueError("shared_spikes must be binary.")
    if initial_snapshot_budget <= 0:
        raise ValueError("initial_snapshot_budget must be positive.")
    if full_snapshot_budget <= initial_snapshot_budget:
        raise ValueError(
            "full_snapshot_budget must exceed initial_snapshot_budget."
        )
    if np.any(gate.accepted & (gate.predicted_labels < 0)):
        raise ValueError("Every accepted sample must have a valid gate prediction.")

    max_time_steps = spikes.shape[1]
    if np.any(gate.accepted & (gate.decision_steps < 1)):
        raise ValueError("Every accepted sample must have a positive decision step.")
    if np.any(gate.decision_steps[gate.accepted] > max_time_steps):
        raise ValueError("A decision step exceeds the available spike sequence.")

    used_fallback = ~gate.accepted
    final_predictions = fallback.copy()
    final_predictions[gate.accepted] = gate.predicted_labels[gate.accepted]
    snapshots_used = np.where(
        gate.accepted,
        initial_snapshot_budget,
        full_snapshot_budget,
    ).astype(int)
    lif_steps_used = np.where(
        gate.accepted,
        gate.decision_steps,
        max_time_steps,
    ).astype(int)

    spikes_per_step = spikes.sum(axis=2, dtype=int)
    cumulative_spikes = np.cumsum(spikes_per_step, axis=1)
    row_index = np.arange(num_samples)
    spike_counts_used = cumulative_spikes[row_index, lif_steps_used - 1]

    return AdaptiveDecisionResult(
        final_predictions=final_predictions,
        used_fallback=used_fallback,
        snapshots_used=snapshots_used,
        lif_steps_used=lif_steps_used,
        spike_counts_used=spike_counts_used,
    )


def adaptive_metrics(
    true_labels: np.ndarray,
    gate: CausalGateResult,
    decisions: AdaptiveDecisionResult,
) -> dict[str, float | int]:
    """Compute accuracy, selective-decision, and realized-cost proxies."""

    truth = np.asarray(true_labels, dtype=int)
    if truth.shape != decisions.final_predictions.shape:
        raise ValueError("true_labels must match final_predictions.")
    num_samples = int(truth.size)
    accepted_count = int(np.sum(gate.accepted))
    correct_accepted = int(
        np.sum(gate.accepted & (gate.predicted_labels == truth))
    )
    incorrect_accepted = accepted_count - correct_accepted
    correct_final = int(np.sum(decisions.final_predictions == truth))

    return {
        "num_samples": num_samples,
        "accepted_count": accepted_count,
        "coverage": accepted_count / num_samples,
        "selective_accuracy": (
            correct_accepted / accepted_count if accepted_count else float("nan")
        ),
        "false_confidence_rate": (
            incorrect_accepted / accepted_count if accepted_count else float("nan")
        ),
        "false_acceptance_probability": incorrect_accepted / num_samples,
        "fallback_rate": float(np.mean(decisions.used_fallback)),
        "final_accuracy": correct_final / num_samples,
        "average_snapshots": float(np.mean(decisions.snapshots_used)),
        "average_lif_steps": float(np.mean(decisions.lif_steps_used)),
        "average_spike_count": float(np.mean(decisions.spike_counts_used)),
    }

