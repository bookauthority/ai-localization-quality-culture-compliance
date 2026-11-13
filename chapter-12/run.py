import json
import os
import platform
from pathlib import Path

from experiment.runner import run_all_variants


def main() -> None:
    # Determine evidence directory
    evidence_dir = Path(os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "results.json"

    # Run experiment variants and collect run records
    runs, notes = run_all_variants()

    evidence = {
        "chapter": 12,
        "experiment_id": "ch12-vendor-bakeoff-hybrid-sourcing-001",
        "environment": {
            "os": platform.platform(),
            "python": platform.python_version(),
        },
        "runs": runs,
        "notes": notes,
    }

    with evidence_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
