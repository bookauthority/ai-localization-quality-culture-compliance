import json
import os
import sys
import time
from typing import Any, Dict, List

from experiment.config import (
    CHAPTER_NUMBER,
    EXPERIMENT_ID,
    WORKLOADS,
)
from experiment.metrics import RunRecord
from experiment.pipeline import run_pipeline_for_workload


def detect_environment() -> Dict[str, str]:
    import platform

    return {
        "os": platform.platform(),
        "python": sys.version.split()[0],
    }


def get_evidence_path() -> str:
    """Return the path to the evidence results.json file.

    Rules:
    - Use BOOKMAS_EVIDENCE_DIR if set; otherwise default to /evidence/results.json.
    - If BOOKMAS_EVIDENCE_DIR is a directory, append results.json.
    - If it looks like a file path (endswith .json), use as-is.
    """

    env = os.getenv("BOOKMAS_EVIDENCE_DIR")
    if not env:
        # default directory and filename
        directory = "/evidence"
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, "results.json")

    # If env points to an existing directory or doesn't have .json suffix,
    # treat it as directory.
    if env.endswith(".json"):
        directory = os.path.dirname(env) or "."
        if directory:
            os.makedirs(directory, exist_ok=True)
        return env
    else:
        directory = env
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, "results.json")


def main() -> None:
    # Collect run records for all workloads and variants
    run_records: List[RunRecord] = []

    for workload in WORKLOADS:
        workload_id = workload["id"]

        # Baseline and treatment variants must both be run per workload
        for variant in ("baseline", "treatment"):
            run_id = f"{workload_id}-{variant}-run1"

            start = time.perf_counter()
            success, metrics = run_pipeline_for_workload(
                workload_id=workload_id,
                workload=workload,
                variant=variant,
            )
            end = time.perf_counter()

            # Ensure processing_time_ms exists and is numeric
            processing_time_ms = (end - start) * 1000.0
            metrics.setdefault("processing_time_ms", processing_time_ms)
            metrics["processing_time_ms"] = float(metrics["processing_time_ms"])

            record: RunRecord = {
                "variant": variant,
                "workload_id": workload_id,
                "run_id": run_id,
                "success": bool(success),
                "metrics": metrics,
            }
            run_records.append(record)

    evidence: Dict[str, Any] = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": detect_environment(),
        "runs": run_records,
        "notes": (
            "Synthetic, fully offline simulation of baseline vs. treatment "
            "compliance-aware localization pipelines. Metrics are limited to "
            "token counts and processing time due to sandbox constraints."
        ),
    }

    evidence_path = get_evidence_path()
    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)


if __name__ == "__main__":  # pragma: no cover
    main()
