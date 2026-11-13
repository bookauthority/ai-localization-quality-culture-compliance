from __future__ import annotations

"""Experiment harness orchestrating baseline and treatment runs.

This module wires together configuration, synthetic data generation, vendor
adapters, and metrics aggregation to produce the `runs` list expected in the
final evidence JSON written by `run.py`.

Each run corresponds to a specific (variant, workload_id) pair, where variant
is either `baseline` or `treatment`. For each pair we:

- Generate synthetic segments for that workload.
- Select and invoke vendors (single or hybrid policy).
- Aggregate metrics across all segments.
- Produce a run record with numeric metrics only.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from . import config
from .config import WORKLOADS
from .data_generation import Segment, generate_all_segments, iter_segments_for_workload
from .metrics import AggregatedMetrics, aggregate_metrics, metrics_to_dict
from .vendors import (
    TranslationResult,
    make_baseline_vendor,
    make_hybrid_vendors,
    select_vendor_for_segment,
)


@dataclass
class RunRecord:
    variant: str
    workload_id: str
    run_id: str
    success: bool
    metrics: Dict[str, float]


def _run_baseline_for_workload(
    workload_id: str, segments: List[Segment]
) -> RunRecord:
    baseline_vendor = make_baseline_vendor()

    results: List[TranslationResult] = []
    for seg in segments:
        res = baseline_vendor.translate(seg)
        results.append(res)

    agg: AggregatedMetrics = aggregate_metrics(results)
    metrics_dict = metrics_to_dict(agg)

    return RunRecord(
        variant="baseline",
        workload_id=workload_id,
        run_id=f"baseline_{workload_id}",
        success=True,
        metrics=metrics_dict,
    )


def _run_treatment_for_workload(
    workload_id: str, segments: List[Segment]
) -> RunRecord:
    vendors = make_hybrid_vendors()

    results: List[TranslationResult] = []
    for seg in segments:
        vendor = select_vendor_for_segment(seg, vendors)
        res = vendor.translate(seg)
        results.append(res)

    agg: AggregatedMetrics = aggregate_metrics(results)
    metrics_dict = metrics_to_dict(agg)

    return RunRecord(
        variant="treatment",
        workload_id=workload_id,
        run_id=f"treatment_{workload_id}",
        success=True,
        metrics=metrics_dict,
    )


def run_all_variants() -> Tuple[List[Dict[str, object]], str]:
    """Run baseline and treatment for all workloads.

    Returns
    -------
    runs:
        List of run dictionaries ready for JSON serialization in the evidence
        file.
    notes:
        Human-readable notes string summarizing key aspects of this run.
    """

    # Generate synthetic segments for all workloads once to ensure that
    # baseline and treatment see identical inputs.
    segments_by_workload = generate_all_segments(WORKLOADS.values(), per_lang_pair_segments=10)

    run_records: List[RunRecord] = []

    for workload_id, workload in WORKLOADS.items():
        segments = list(iter_segments_for_workload(segments_by_workload, workload_id))

        # Baseline run
        baseline_record = _run_baseline_for_workload(workload_id, segments)
        run_records.append(baseline_record)

        # Treatment run
        treatment_record = _run_treatment_for_workload(workload_id, segments)
        run_records.append(treatment_record)

    runs_dicts: List[Dict[str, object]] = []
    for r in run_records:
        runs_dicts.append(
            {
                "variant": r.variant,
                "workload_id": r.workload_id,
                "run_id": r.run_id,
                "success": bool(r.success),
                "metrics": r.metrics,
            }
        )

    notes = (
        "Offline simulation of a chapter 12 multi-vendor bake-off. "
        "Baseline uses a single vendor; treatment uses a simple hybrid "
        "routing policy across two additional vendors. Metrics are "
        "synthetic but derived from actual instrumented execution over "
        "deterministic segments."
    )

    return runs_dicts, notes
