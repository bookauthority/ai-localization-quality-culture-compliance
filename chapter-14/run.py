import json
import os
import platform
from pathlib import Path

from experiment.config import EXPERIMENT_ID, CHAPTER, WORKLOADS
from experiment.experiment_runner import ExperimentRunner


def main() -> None:
    """Execute the experiment and write evidence JSON.

    Evidence is always written to BOOKMAS_EVIDENCE_DIR/results.json,
    defaulting to /evidence when the environment variable is unset.
    """

    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    results_file = evidence_path / "results.json"

    runner = ExperimentRunner(
        experiment_id=EXPERIMENT_ID,
        chapter=CHAPTER,
        workloads=WORKLOADS,
    )

    runs = runner.run_all()

    environment_info = {
        "os": platform.platform(),
        "python": platform.python_version(),
    }

    evidence = {
        "chapter": CHAPTER,
        "experiment_id": EXPERIMENT_ID,
        "environment": environment_info,
        "runs": runs,
        "notes": (
            "Simulated localization pipeline runs with baseline vs treatment "
            "variants across three workloads. Metrics are synthetic but "
            "derived from instrumented execution within this sandbox. "
            "Logs are written only to stdout and are never parsed into this "
            "evidence object. Stage-level durations are simulated using a "
            "seeded PRNG for determinism rather than wall-clock timing."
        ),
    }

    with results_file.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
