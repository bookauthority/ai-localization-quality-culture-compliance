from __future__ import annotations

from typing import Dict, List


def aggregate_numeric_metric(values: List[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / float(len(values)))


def compute_length_ratios(sources: List[str], translations: List[str]) -> float:
    ratios: List[float] = []
    for s, t in zip(sources, translations):
        if not s:
            continue
        ratios.append(len(t) / float(len(s)))
    return aggregate_numeric_metric(ratios)


def compute_terminology_accuracy(
    correct_counts: List[int], required_counts: List[int]
) -> float:
    required_total = sum(required_counts)
    if required_total == 0:
        return 0.0
    correct_total = sum(correct_counts)
    return float(100.0 * correct_total / float(required_total))


def compute_terminology_violation_rate(segments_with_violation: int, total_segments: int) -> float:
    if total_segments == 0:
        return 0.0
    return float(100.0 * segments_with_violation / float(total_segments))


def compute_percentage(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return float(100.0 * count / float(total))
