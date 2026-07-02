"""Phase 1 DOA Python reference-model runner.

Run from the repository root with:

    python phase_01_python_prototype/run_phase_01.py

The current step generates the physics-based ULA/DOA dataset and saves a
summary file. Spike encoding and LIF inference will be added in the next steps.
"""

from __future__ import annotations

from pathlib import Path

from .dataset import DOAConfig, dataset_summary, generate_doa_dataset


def main() -> None:
    """Generate the first physics-based DOA dataset and save a summary."""

    phase_dir = Path(__file__).resolve().parents[1]
    results_dir = phase_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    config = DOAConfig()
    dataset = generate_doa_dataset(config)
    summary = dataset_summary(dataset)

    summary_path = results_dir / "run_001_dataset_summary.txt"
    summary_path.write_text(summary + "\n", encoding="utf-8")

    print(summary)
    print("")
    print(f"Saved dataset summary to: {summary_path}")
    print("")
    print("Step 1 complete: physics-based ULA/DOA dataset generation is working.")
    print("Next step: implement spike encoding and baseline/LIF inference.")


if __name__ == "__main__":
    main()
