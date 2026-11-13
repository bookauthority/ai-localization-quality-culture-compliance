from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple

from .core import BaselineProcessor, TreatmentOrchestrator, compute_latency_metrics, compute_throughput
from .workloads import build_workloads


def _run_variant_for_workload(
    variant: str,
    workload_id: str,
    seed: int,
) -> Tuple[Dict[str, float], bool]:
    """Run a single variant (baseline/treatment) for one workload.

    Returns (metrics_dict, success_flag).
    """

    workloads = build_workloads(seed=seed)
    segments = workloads[workload_id]

    rng = random.Random(seed + (0 if variant == "baseline" else 1000))

    if variant == "baseline":
        processor = BaselineProcessor(rng=rng)
        results = processor.process(workload_id=workload_id, segments=segments, variant=variant)
    else:
        orchestrator = TreatmentOrchestrator(rng=rng, num_workers=4)
        results = orchestrator.process(workload_id=workload_id, segments=segments, variant=variant)

    p50, p95 = compute_latency_metrics(results)
    throughput = compute_throughput(results)

    metrics = {
        "end_to_end_latency_p50": float(p50),
        "end_to_end_latency_p95": float(p95),
        "throughput": float(throughput),
    }

    # In this synthetic simulation, consider the run successful if we
    # processed all segments and metrics are finite positive numbers.
    success = (
        len(results) == len(segments)
        and all(math.isfinite(v) for v in metrics.values())
        and throughput > 0.0
    )

    return metrics, success


def run_all_workloads() -> Tuple[List[Dict], str]:
    """Run all workloads for both baseline and treatment variants.

    Returns (runs_list, notes_string).
    """

    workloads = build_workloads(seed=42)
    workload_ids = sorted(workloads.keys())

    runs: List[Dict] = []
    seed_base = 42

    for workload_id in workload_ids:
        for variant in ("baseline", "treatment"):
            metrics, success = _run_variant_for_workload(
                variant=variant,
                workload_id=workload_id,
                seed=seed_base,
            )
            run_id = f"{workload_id}-{variant}-run-1"
            runs.append(
                {
                    "variant": variant,
                    "workload_id": workload_id,
                    "run_id": run_id,
                    "success": bool(success),
                    "metrics": metrics,
                }
            )

    notes = (
        "This evidence file contains synthetic metrics for baseline and treatment "
        "variants across three workloads. Only latency percentiles and throughput "
        "are measured; other metrics from the full experimental specification "
        "(e.g., cost, error_rate, incidents) are not included because they cannot "
        "be meaningfully observed in this offline, simulated environment."
    )

    return runs, notes
