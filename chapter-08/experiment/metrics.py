from __future__ import annotations

from typing import Iterable, List

from .pipelines import BaselineOutput, TreatmentOutput


def _length_ratio(src: str, tgt: str) -> float:
    if not src:
        return 1.0
    return len(tgt) / float(len(src))


def avg_length_ratio_baseline(outputs: Iterable[BaselineOutput]) -> float:
    ratios: List[float] = []
    for o in outputs:
        ratios.append(_length_ratio(o.source_text, o.target_text))
    return sum(ratios) / len(ratios) if ratios else 0.0


def avg_length_ratio_treatment(outputs: Iterable[TreatmentOutput]) -> float:
    ratios: List[float] = []
    for o in outputs:
        ratios.append(_length_ratio(o.source_text, o.target_text))
    return sum(ratios) / len(ratios) if ratios else 0.0


def avg_cultural_flags_treatment(outputs: Iterable[TreatmentOutput]) -> float:
    counts: List[float] = []
    for o in outputs:
        count = float(len(o.source_cultural_red_flags) + len(o.target_cultural_red_flags))
        counts.append(count)
    return sum(counts) / len(counts) if counts else 0.0


def avg_cultural_flags_baseline(outputs: Iterable[BaselineOutput]) -> float:
    # Baseline has no explicit cultural flags; this metric will reflect zero,
    # but we implement it for symmetry and to show relative improvement.
    counts: List[float] = []
    for _ in outputs:
        counts.append(0.0)
    return sum(counts) / len(counts) if counts else 0.0
