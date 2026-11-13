from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

from .config import WorkloadConfig, WORKLOADS
from .pipeline import LocalizationPipeline


@dataclass
class ExperimentRunner:
    experiment_id: str
    chapter: int
    workloads: List[WorkloadConfig]

    def run_all(self) -> List[Dict]:
        """Run a small controlled experiment across all workloads.

        For each workload we ensure at least one baseline and one treatment
        run exist. Randomization uses a fixed seed for reproducibility while
        still varying assignment across runs.
        """

        global_seed = 1729
        rng = random.Random(global_seed)

        runs: List[Dict] = []

        for w_index, workload in enumerate(self.workloads):
            # Each workload uses its own seed derived from the global seed
            # to keep behavior stable yet workload-specific.
            pipeline = LocalizationPipeline(seed=global_seed + w_index)

            # Determine how many jobs we will run in total for this workload.
            total_jobs = workload.jobs_per_variant * 2

            # Pre-generate variant assignments with at least one of each.
            assignments: List[str] = []
            # Start with one guaranteed baseline and treatment each.
            assignments.extend(["baseline", "treatment"])
            for _ in range(total_jobs - 2):
                assignments.append("baseline" if rng.random() < 0.5 else "treatment")
            rng.shuffle(assignments)

            baseline_seen = False
            treatment_seen = False

            for job_index in range(total_jobs):
                variant = assignments[job_index]
                if variant == "baseline":
                    baseline_seen = True
                elif variant == "treatment":
                    treatment_seen = True
                else:  # Defensive programming; should never happen
                    raise ValueError(f"Unexpected variant label in schedule: {variant!r}")

                result = pipeline.run(workload, variant, job_index)

                run_record = {
                    "variant": variant,
                    "workload_id": workload.workload_id,
                    "run_id": f"{variant}-{job_index}",
                    "success": bool(result.success),
                    "metrics": result.metrics,
                }
                runs.append(run_record)

            # Safety check: if our randomized schedule somehow missed a
            # variant (should not happen), we inject one minimal extra job.
            if not baseline_seen:
                extra_result = pipeline.run(workload, "baseline", total_jobs)
                runs.append(
                    {
                        "variant": "baseline",
                        "workload_id": workload.workload_id,
                        "run_id": f"baseline-{total_jobs}",
                        "success": bool(extra_result.success),
                        "metrics": extra_result.metrics,
                    }
                )
            if not treatment_seen:
                extra_result = pipeline.run(workload, "treatment", total_jobs + 1)
                runs.append(
                    {
                        "variant": "treatment",
                        "workload_id": workload.workload_id,
                        "run_id": f"treatment-{total_jobs+1}",
                        "success": bool(extra_result.success),
                        "metrics": extra_result.metrics,
                    }
                )

        return runs
