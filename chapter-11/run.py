import json
import os
import sys
from typing import Any, Dict, List

from experiment.config import WORKLOADS, CHAPTER_NUMBER, EXPERIMENT_ID
from experiment.pipeline import run_baseline_for_workload, run_treatment_for_workload


def detect_environment() -> Dict[str, str]:
    import platform

    return {
        "os": platform.platform(),
        "python": sys.version.split()[0],
    }


def main() -> None:
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    runs: List[Dict[str, Any]] = []

    # Execute baseline and treatment for each workload
    for workload in WORKLOADS:
        workload_id = workload["id"]

        baseline_run_id = f"baseline_{workload_id}_v1"
        treatment_run_id = f"treatment_{workload_id}_v1"

        # Baseline
        baseline_result = run_baseline_for_workload(workload)
        runs.append(
            {
                "variant": "baseline",
                "workload_id": workload_id,
                "run_id": baseline_run_id,
                "success": bool(baseline_result.get("success", True)),
                "metrics": baseline_result.get("metrics", {}),
            }
        )

        # Treatment
        treatment_result = run_treatment_for_workload(workload)
        runs.append(
            {
                "variant": "treatment",
                "workload_id": workload_id,
                "run_id": treatment_run_id,
                "success": bool(treatment_result.get("success", True)),
                "metrics": treatment_result.get("metrics", {}),
            }
        )

    evidence: Dict[str, Any] = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": detect_environment(),
        "runs": runs,
        "notes": (
            "This is a deterministic offline simulation of baseline vs. "
            "treatment pipelines with translation memories, termbases, "
            "and vector-based example retrieval. Metrics are computed "
            "from pseudo-translations and toy assets; BLEU/COMET/human "
            "metrics are intentionally omitted due to environment "
            "constraints."
        ),
    }

    output_path = os.path.join(evidence_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
