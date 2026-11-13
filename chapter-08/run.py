import json
import os
from pathlib import Path

from experiment.runner import run_experiment
from experiment.utils import get_environment_metadata


def main() -> None:
    chapter = 8
    experiment_id = "exp-ch08-cultural-adaptation-workflow-v1"

    # Run the simulated experiment
    runs = run_experiment()

    env_meta = get_environment_metadata()

    evidence = {
        "chapter": chapter,
        "experiment_id": experiment_id,
        "environment": env_meta,
        "runs": runs,
        "notes": (
            "Synthetic, fully offline simulation of baseline vs cultural-adaptation "
            "treatment pipelines for three workloads. Metrics are derived from "
            "deterministic rule-based processing; no external services or real "
            "user data are used."
        ),
    }

    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    out_dir = Path(evidence_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
