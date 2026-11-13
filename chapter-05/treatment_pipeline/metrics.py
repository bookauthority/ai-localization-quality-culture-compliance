from dataclasses import dataclass


@dataclass
class AggregatedMetrics:
    segments_total: float
    segments_successfully_translated: float
    segments_failed_translation: float
    segments_passing_all_qa: float
    segments_failing_any_qa: float


def empty_metrics() -> AggregatedMetrics:
    return AggregatedMetrics(
        segments_total=0.0,
        segments_successfully_translated=0.0,
        segments_failed_translation=0.0,
        segments_passing_all_qa=0.0,
        segments_failing_any_qa=0.0,
    )


def to_dict(m: AggregatedMetrics) -> dict:
    return {
        "segments_total": float(m.segments_total),
        "segments_successfully_translated": float(m.segments_successfully_translated),
        "segments_failed_translation": float(m.segments_failed_translation),
        "segments_passing_all_qa": float(m.segments_passing_all_qa),
        "segments_failing_any_qa": float(m.segments_failing_any_qa),
    }
