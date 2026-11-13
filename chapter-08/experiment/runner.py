from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .data import SourceItem, load_all_source_items
from .metrics import (
    avg_cultural_flags_baseline,
    avg_cultural_flags_treatment,
    avg_length_ratio_baseline,
    avg_length_ratio_treatment,
)
from .pipelines import BaselineOutput, TreatmentOutput, run_baseline_pipeline, run_treatment_pipeline
from .utils import set_deterministic_seed


def _group_by_workload(items: List[SourceItem]) -> Dict[str, List[SourceItem]]:
    grouped: Dict[str, List[SourceItem]] = defaultdict(list)
    for it in items:
        grouped[it.workload].append(it)
    return grouped


def run_experiment() -> List[Dict]:
    """Run baseline and treatment for each workload and return evidence runs list."""

    set_deterministic_seed(42)
    items = load_all_source_items()
    grouped = _group_by_workload(items)

    runs: List[Dict] = []

    for workload_id, wl_items in sorted(grouped.items(), key=lambda kv: kv[0]):
        # Baseline
        baseline_outputs: List[BaselineOutput] = run_baseline_pipeline(wl_items)
        bl_len_ratio = avg_length_ratio_baseline(baseline_outputs)
        bl_flags = avg_cultural_flags_baseline(baseline_outputs)

        runs.append(
            {
                "variant": "baseline",
                "workload_id": workload_id,
                "run_id": f"baseline-{workload_id}-1",
                "success": True,
                "metrics": {
                    "avg_length_ratio": float(bl_len_ratio),
                    "avg_cultural_flags": float(bl_flags),
                },
            }
        )

        # Treatment
        treatment_outputs: List[TreatmentOutput] = run_treatment_pipeline(wl_items)
        tr_len_ratio = avg_length_ratio_treatment(treatment_outputs)
        tr_flags = avg_cultural_flags_treatment(treatment_outputs)

        runs.append(
            {
                "variant": "treatment",
                "workload_id": workload_id,
                "run_id": f"treatment-{workload_id}-1",
                "success": True,
                "metrics": {
                    "avg_length_ratio": float(tr_len_ratio),
                    "avg_cultural_flags": float(tr_flags),
                },
            }
        )

    return runs
