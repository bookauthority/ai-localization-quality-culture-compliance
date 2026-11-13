import json
import os
import sys
import platform
from pathlib import Path

from experiment.runner import run_all_workloads


CHAPTER = 10
EXPERIMENT_ID = "exp-ch10-routing-orchestration-cicd-001"


def main() -> None:
    # Determine evidence directory
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)

    # Run experiment
    runs, notes = run_all_workloads()

    evidence = {
        "chapter": CHAPTER,
        "experiment_id": EXPERIMENT_ID,
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
        },
        "runs": runs,
        "notes": notes,
    }

    output_file = evidence_path / "results.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=False)


if __name__ == "__main__":
    main()
