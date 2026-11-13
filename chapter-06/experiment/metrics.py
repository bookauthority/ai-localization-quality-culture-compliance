from __future__ import annotations

from typing import Dict

from .simulation import RunSimulationResult


def aggregate_run_metrics(run: RunSimulationResult) -> Dict[str, float]:
    """Aggregate numeric metrics for a simulated run.

    The returned values are all finite numbers, suitable for inclusion in the
    evidence JSON `metrics` object.

    Metrics:
        - avg_quality_score: mean quality score over segments (0–100).
        - functional_error_rate: proportion of segments with a functional error.
        - avg_latency_ms: average simulated latency per segment in milliseconds.
    """

    n = run.num_segments
    if n == 0:
        # Should not normally occur, but keep schema-valid defaults.
        return {
            "avg_quality_score": 0.0,
            "functional_error_rate": 0.0,
            "avg_latency_ms": 0.0,
        }

    total_quality = 0.0
    total_latency = 0.0
    func_errors = 0

    for seg_result in run.segments_results:
        total_quality += float(seg_result.quality_score)
        total_latency += float(seg_result.latency_ms)
        if seg_result.functional_error:
            func_errors += 1

    avg_quality = total_quality / n
    avg_latency = total_latency / n
    functional_error_rate = func_errors / n

    return {
        "avg_quality_score": avg_quality,
        "functional_error_rate": functional_error_rate,
        "avg_latency_ms": avg_latency,
    }
