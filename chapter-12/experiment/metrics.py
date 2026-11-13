from __future__ import annotations

"""Metric instrumentation utilities for the offline experiment.

Instead of real BLEU/COMET, this module computes simple numeric aggregates from
per-segment synthetic quality scores and measured/simulated latencies.

All metrics are kept numeric and finite, as required by the evidence schema.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List

from .vendors import TranslationResult


@dataclass
class AggregatedMetrics:
    """Aggregated metrics for a single run over a workload.

    Attributes
    ----------
    segments_processed:
        Total number of segments successfully translated.
    avg_quality_score:
        Mean synthetic quality score across all segments (0-1 range).
    latency_ms_avg:
        Average latency in milliseconds across segments.
    latency_ms_p95:
        95th percentile latency in milliseconds.
    throughput_segs_per_s:
        Estimated throughput measured as segments per second, derived from
        latencies assuming sequential processing.
    """

    segments_processed: int
    avg_quality_score: float
    latency_ms_avg: float
    latency_ms_p95: float
    throughput_segs_per_s: float


def aggregate_metrics(results: Iterable[TranslationResult]) -> AggregatedMetrics:
    latencies: List[float] = []
    qualities: List[float] = []

    for r in results:
        latencies.append(float(r.latency_ms))
        qualities.append(float(r.quality_score))

    n = len(latencies)
    if n == 0:
        return AggregatedMetrics(0, 0.0, 0.0, 0.0, 0.0)

    total_latency = sum(latencies)
    avg_latency = total_latency / n
    avg_quality = sum(qualities) / n

    sorted_lat = sorted(latencies)
    # Simple 95th percentile: index at ceil(0.95 * n) - 1
    idx = max(0, min(n - 1, int(0.95 * n + 0.9999) - 1))
    p95 = sorted_lat[idx]

    # Throughput (segments per second) assuming sequential execution and
    # approximating total wall time as sum of per-segment latency.
    # latencies are in ms, so convert to seconds.
    total_seconds = total_latency / 1000.0 if total_latency > 0 else 0.0
    throughput = (n / total_seconds) if total_seconds > 0 else 0.0

    return AggregatedMetrics(
        segments_processed=n,
        avg_quality_score=avg_quality,
        latency_ms_avg=avg_latency,
        latency_ms_p95=p95,
        throughput_segs_per_s=throughput,
    )


def metrics_to_dict(metrics: AggregatedMetrics) -> Dict[str, float]:
    """Convert AggregatedMetrics into a plain dict of numeric values.

    This form is directly serializable into the evidence JSON under the
    `metrics` field for each run.
    """

    return {
        "segments_processed": float(metrics.segments_processed),
        "avg_quality_score": float(metrics.avg_quality_score),
        "latency_ms_avg": float(metrics.latency_ms_avg),
        "latency_ms_p95": float(metrics.latency_ms_p95),
        "throughput_segs_per_s": float(metrics.throughput_segs_per_s),
    }
