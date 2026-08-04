"""Validate the common progressive-snapshot dataset checkpoint.

Run from the repository root with:

    python -m phase_02_confidence_aware_fast_slow_doa.run_day_02_progressive_snapshot_validation
"""

from __future__ import annotations

import json
import platform
from pathlib import Path

import numpy as np

from phase_01_python_prototype.src.dataset import (
    DOAConfig,
    generate_doa_dataset,
    stratified_train_test_split_by_snr_and_class,
)
from phase_02_confidence_aware_fast_slow_doa.src.progressive_dataset import (
    DEFAULT_SNAPSHOT_BUDGETS,
    generate_progressive_doa_dataset,
    normalize_progressive_train_test,
)


REFERENCE_COMMIT = "e2f8af33fd9046d5152d4c58f6f8e8f2cf76031f"


def main() -> None:
    """Run reproducibility, alignment, and Phase 1 compatibility checks."""

    config = DOAConfig()
    progressive = generate_progressive_doa_dataset(config, DEFAULT_SNAPSHOT_BUDGETS)
    repeated = generate_progressive_doa_dataset(config, DEFAULT_SNAPSHOT_BUDGETS)
    phase_1 = generate_doa_dataset(config)

    train_index, test_index, _ = stratified_train_test_split_by_snr_and_class(
        labels=progressive.labels,
        snr_db=progressive.snr_db,
        snr_values=config.snr_db_values,
        num_classes=config.num_classes,
        train_fraction=0.70,
        random_seed=config.random_seed,
    )
    normalized = normalize_progressive_train_test(progressive, train_index, test_index)

    phase_1_features = np.asarray(phase_1["features"], dtype=float)
    full_features = np.asarray(progressive.features_by_budget[config.num_snapshots])
    metadata_match = {
        "labels": bool(np.array_equal(progressive.labels, phase_1["labels"])),
        "theta_deg": bool(np.array_equal(progressive.theta_deg, phase_1["theta_deg"])),
        "snr_db": bool(np.array_equal(progressive.snr_db, phase_1["snr_db"])),
    }
    repeatability = {
        str(budget): bool(
            np.array_equal(
                progressive.features_by_budget[budget],
                repeated.features_by_budget[budget],
            )
        )
        for budget in progressive.snapshot_budgets
    }
    mean_absolute_delta_from_full = {
        str(budget): float(
            np.mean(np.abs(progressive.features_by_budget[budget] - full_features))
        )
        for budget in progressive.snapshot_budgets
    }

    validation = {
        "checkpoint": "day_02_progressive_snapshot_validation",
        "source_reference_commit": REFERENCE_COMMIT,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "random_seed": config.random_seed,
        "snapshot_budgets": list(progressive.snapshot_budgets),
        "num_samples": progressive.num_samples,
        "num_features": config.num_features,
        "train_samples": int(train_index.size),
        "test_samples": int(test_index.size),
        "feature_shapes": {
            str(budget): list(progressive.features_by_budget[budget].shape)
            for budget in progressive.snapshot_budgets
        },
        "phase_1_metadata_exact_match": metadata_match,
        "phase_1_m128_max_abs_feature_error": float(
            np.max(np.abs(full_features - phase_1_features))
        ),
        "repeatability_exact_match": repeatability,
        "mean_absolute_feature_delta_from_m128": mean_absolute_delta_from_full,
        "normalization": {
            "statistics_source": "training split only, separately for each snapshot budget",
            "train_range_by_budget": {
                str(budget): [
                    float(np.min(normalized.train_features_by_budget[budget])),
                    float(np.max(normalized.train_features_by_budget[budget])),
                ]
                for budget in progressive.snapshot_budgets
            },
            "test_range_by_budget": {
                str(budget): [
                    float(np.min(normalized.test_features_by_budget[budget])),
                    float(np.max(normalized.test_features_by_budget[budget])),
                ]
                for budget in progressive.snapshot_budgets
            },
        },
    }

    all_checks_pass = (
        all(metadata_match.values())
        and all(repeatability.values())
        and validation["phase_1_m128_max_abs_feature_error"] <= 1e-12
        and progressive.num_samples == 2800
        and train_index.size == 1960
        and test_index.size == 840
    )
    validation["all_checks_pass"] = bool(all_checks_pass)

    phase_dir = Path(__file__).resolve().parent
    results_dir = phase_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "day_02_progressive_snapshot_validation.json"
    output_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(validation, indent=2))
    print(f"Saved validation record to: {output_path}")
    if not all_checks_pass:
        raise SystemExit("Progressive-snapshot validation failed.")


if __name__ == "__main__":
    main()

