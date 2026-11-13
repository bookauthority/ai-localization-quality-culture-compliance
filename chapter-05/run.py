import json
import os
import platform
import sys
import uuid
from typing import Dict, Any, List

from baseline_pipeline import run_baseline_pipeline
from treatment_pipeline.pipeline import run_treatment_pipeline


EXPERIMENT_ID = "exp-ch05-baseline-ai-localization-pipeline-v1"
CHAPTER_NUMBER = 5


def ensure_evidence_dir() -> str:
    """Return the evidence directory, creating it if needed.

    The environment variable BOOKMAS_EVIDENCE_DIR points to the writable
    evidence directory; default to "/evidence" if unset.
    """

    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    return evidence_dir


def run_experiment() -> Dict[str, Any]:
    """Run baseline and treatment variants on both workloads.

    Returns the full evidence payload (not yet written to disk).
    """

    workloads = [
        {
            "workload_id": "sample_customer_support_tickets",
            "input_path": os.path.join("data", "sample_customer_support_en.csv"),
        },
        {
            "workload_id": "sample_marketing_snippets",
            "input_path": os.path.join("data", "sample_marketing_snippets_en.csv"),
        },
    ]

    runs: List[Dict[str, Any]] = []

    # Baseline and treatment share datasets but use separate implementations.
    for workload in workloads:
        workload_id = workload["workload_id"]
        input_path = workload["input_path"]

        # Baseline run
        baseline_run_id = f"baseline-{uuid.uuid4()}"
        try:
            baseline_metrics = run_baseline_pipeline(input_path=input_path)
            baseline_success = True
        except Exception:
            # In a real system, we would log the traceback; here we only
            # record failure and omit metrics (no fabricated numbers).
            baseline_metrics = {}
            baseline_success = False

        runs.append(
            {
                "variant": "baseline",
                "workload_id": workload_id,
                "run_id": baseline_run_id,
                "success": bool(baseline_success),
                "metrics": baseline_metrics,
            }
        )

        # Treatment run
        treatment_run_id = f"treatment-{uuid.uuid4()}"
        try:
            treatment_metrics = run_treatment_pipeline(input_path=input_path)
            treatment_success = True
        except Exception:
            treatment_metrics = {}
            treatment_success = False

        runs.append(
            {
                "variant": "treatment",
                "workload_id": workload_id,
                "run_id": treatment_run_id,
                "success": bool(treatment_success),
                "metrics": treatment_metrics,
            }
        )

    environment = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
    }

    evidence: Dict[str, Any] = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": environment,
        "runs": runs,
        "notes": (
            "Offline sandbox run of baseline vs treatment localization "
            "pipelines with deterministic pseudo-translation. Metrics "
            "use per segment-locale semantics and are derived directly "
            "from in-process execution over the small CSV datasets in data/. "
            "Spec-level timing and rate metrics are intentionally not emitted "
            "in this offline implementation."
        ),
    }

    return evidence


def main() -> None:
    evidence_dir = ensure_evidence_dir()
    evidence = run_experiment()
    output_path = os.path.join(evidence_dir, "results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=False)


if __name__ == "__main__":
    main()
