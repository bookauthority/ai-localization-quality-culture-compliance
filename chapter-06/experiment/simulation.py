from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .randomization import randint, uniform


@dataclass
class Segment:
    """Represents a synthetic source segment.

    Attributes:
        id: Stable segment identifier within the workload.
        length: Approximate token length of the segment.
        has_placeholders: Whether the segment contains placeholders/tags.
        risk: Low/medium/high risk flag derived from workload.
    """

    id: str
    length: int
    has_placeholders: bool
    risk: str


@dataclass
class SegmentSimulationResult:
    segment: Segment
    quality_score: float
    functional_error: bool
    latency_ms: float


@dataclass
class RunSimulationResult:
    workload_id: str
    variant: str
    segments_results: List[SegmentSimulationResult]

    @property
    def num_segments(self) -> int:
        return len(self.segments_results)


def generate_workload_segments(workload_id: str) -> List[Segment]:
    """Create deterministic synthetic segments per workload.

    We differentiate workloads primarily by typical segment length and risk.
    This function does not use randomness for the number of segments or
    their base properties, to keep runs very fast and predictable.
    """

    segments: List[Segment] = []

    if workload_id == "w1-ui_product_strings":
        # Many short UI strings with frequent placeholders; medium risk
        count = 60
        for i in range(count):
            seg_id = f"ui-{i:03d}"
            # Alternate between very short and medium labels
            base_len = 3 if i % 3 == 0 else 8
            has_placeholders = i % 2 == 0
            segments.append(
                Segment(
                    id=seg_id,
                    length=base_len,
                    has_placeholders=has_placeholders,
                    risk="medium",
                )
            )

    elif workload_id == "w2-marketing_pages":
        # Fewer but longer marketing paragraphs; low/medium risk
        count = 24
        for i in range(count):
            seg_id = f"mkt-{i:03d}"
            base_len = 80 if i % 2 == 0 else 160
            has_placeholders = i % 4 == 0
            risk = "medium" if i % 5 == 0 else "low"
            segments.append(
                Segment(
                    id=seg_id,
                    length=base_len,
                    has_placeholders=has_placeholders,
                    risk=risk,
                )
            )

    elif workload_id == "w3-high_risk_regulated_docs":
        # High-risk, longer segments simulating complex regulated passages
        count = 20
        for i in range(count):
            seg_id = f"reg-{i:03d}"
            base_len = 220 if i % 2 == 0 else 320
            has_placeholders = i % 3 == 0
            segments.append(
                Segment(
                    id=seg_id,
                    length=base_len,
                    has_placeholders=has_placeholders,
                    risk="high",
                )
            )
    else:
        raise ValueError(f"Unknown workload_id: {workload_id}")

    return segments


def _simulate_segment_baseline(seg: Segment) -> SegmentSimulationResult:
    """Simulate baseline translation and QA for a single segment.

    Baseline has:
    - Lower expected quality score, especially for longer/high-risk segments.
    - Higher functional error probability when placeholders exist.
    - Lower and simpler latency cost model.
    """

    # Base quality decreases with length and risk
    base_quality = 70.0
    if seg.risk == "medium":
        base_quality -= 5.0
    elif seg.risk == "high":
        base_quality -= 10.0

    length_penalty = min(seg.length / 50.0, 10.0)  # up to -10 points
    noise = uniform(-3.0, 3.0)
    quality = max(0.0, min(100.0, base_quality - length_penalty + noise))

    # Functional error probability
    func_error_prob = 0.03
    if seg.has_placeholders:
        func_error_prob += 0.07
    if seg.risk == "high":
        func_error_prob += 0.05

    # Draw error occurrence
    functional_error = uniform(0.0, 1.0) < func_error_prob

    # Latency: simple linear in length with small noise
    latency_ms = seg.length * 0.8 + uniform(0.0, 1.0) * 2.0

    return SegmentSimulationResult(
        segment=seg,
        quality_score=quality,
        functional_error=functional_error,
        latency_ms=latency_ms,
    )


def _simulate_segment_treatment(seg: Segment) -> SegmentSimulationResult:
    """Simulate treatment pipeline for a single segment.

    Treatment:
    - Higher expected quality due to enhanced checks and routing.
    - Lower functional error rate, especially with placeholders.
    - Slightly increased latency cost relative to baseline.
    """

    base_quality = 80.0
    if seg.risk == "medium":
        base_quality -= 2.0
    elif seg.risk == "high":
        base_quality -= 4.0

    length_penalty = min(seg.length / 60.0, 8.0)
    noise = uniform(-2.0, 2.0)
    quality = max(0.0, min(100.0, base_quality - length_penalty + noise))

    # Functional error probability reduced vs baseline
    func_error_prob = 0.015
    if seg.has_placeholders:
        func_error_prob += 0.03
    if seg.risk == "high":
        func_error_prob += 0.03

    functional_error = uniform(0.0, 1.0) < func_error_prob

    # Latency slightly higher than baseline per token, plus small overhead
    latency_ms = seg.length * 1.1 + 3.0 + uniform(0.0, 1.0) * 2.0

    return SegmentSimulationResult(
        segment=seg,
        quality_score=quality,
        functional_error=functional_error,
        latency_ms=latency_ms,
    )


def simulate_pipeline_run(
    workload_id: str,
    variant: str,
    segments: List[Segment],
) -> RunSimulationResult:
    """Simulate a full pipeline run over all segments for a given variant.

    Args:
        workload_id: The workload identifier.
        variant: "baseline" or "treatment".
        segments: The list of segments to process.

    Returns:
        RunSimulationResult with per-segment quality and latency outcomes.
    """

    results: List[SegmentSimulationResult] = []

    for seg in segments:
        if variant == "baseline":
            seg_result = _simulate_segment_baseline(seg)
        elif variant == "treatment":
            seg_result = _simulate_segment_treatment(seg)
        else:
            raise ValueError(f"Unknown variant: {variant}")
        results.append(seg_result)

    return RunSimulationResult(
        workload_id=workload_id,
        variant=variant,
        segments_results=results,
    )
