import json
import os
import platform
from pathlib import Path

from experiment.randomization import GLOBAL_RANDOM
from experiment.simulation import generate_workload_segments, simulate_pipeline_run
from experiment.metrics import aggregate_run_metrics


EXPERIMENT_ID = "ch06-operationalizing-quality-metrics-eval-feedback-v1"
CHAPTER = 6


def get_evidence_dir() -> Path:
    """Return the directory where evidence should be written.

    Defaults to /evidence if BOOKMAS_EVIDENCE_DIR is not set.
    """
    env_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    path = Path(env_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> None:
    # Ensure deterministic behavior from the start
    GLOBAL_RANDOM.seed(42)

    workloads = [
        "w1-ui_product_strings",
        "w2-marketing_pages",
        "w3-high_risk_regulated_docs",
    ]

    variants = ["baseline", "treatment"]

    runs = []

    # For each workload and variant we perform a single simulated run.
    for workload_id in workloads:
        segments = generate_workload_segments(workload_id)
        for variant in variants:
            run_id = f"{workload_id}-{variant}-seed42"
            sim_results = simulate_pipeline_run(
                workload_id=workload_id,
                variant=variant,
                segments=segments,
            )
            metrics = aggregate_run_metrics(sim_results)
            # success is True iff simulation produced at least one metricable segment
            success = sim_results.num_segments > 0
            runs.append(
                {
                    "variant": variant,
                    "workload_id": workload_id,
                    "run_id": run_id,
                    "success": bool(success),
                    "metrics": metrics,
                }
            )

    evidence = {
        "chapter": CHAPTER,
        "experiment_id": EXPERIMENT_ID,
        "environment": {
            "os": platform.system(),
            "python": platform.python_version(),
        },
        "runs": runs,
        "notes": (
            "Synthetic, fully offline simulation of baseline vs. treatment "
            "localization quality pipelines. Metrics are deterministic and "
            "derived from simulated segment quality, functional checks, and "
            "pseudo-latency; no external services or real human evaluations "
            "were used."
        ),
    }

    evidence_dir = get_evidence_dir()
    output_path = evidence_dir / "results.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=False)


if __name__ == "__main__":
    main()
