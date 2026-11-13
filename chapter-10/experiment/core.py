from __future__ import annotations

import math
import random
import threading
import time
from dataclasses import dataclass
from queue import Queue, Empty
from statistics import median
from typing import Callable, Dict, Iterable, List, Optional, Tuple


@dataclass
class Segment:
    """Represents a single localization segment in the simulation."""

    segment_id: str
    language: str
    channel: str
    content_type: str
    risk_level: str
    text_length: int


@dataclass
class SegmentResult:
    segment_id: str
    variant: str
    workload_id: str
    start_time: float
    end_time: float

    @property
    def latency(self) -> float:
        return self.end_time - self.start_time


class BaselineProcessor:
    """Monolithic, synchronous baseline processor with hard-coded routing.

    This class simulates a simplistic pipeline where routing decisions are
    embedded directly in code and processing is performed sequentially.
    """

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def _processing_time_for_segment(self, segment: Segment) -> float:
        """Return synthetic processing time in seconds for a segment.

        The function encodes simple assumptions:
        - High-risk content is slower.
        - Longer text is slower.
        - Different channels add small overhead.
        """

        base = 0.002  # base cost per segment
        length_factor = 0.00001 * segment.text_length

        risk_multiplier = 1.0
        if segment.risk_level == "high":
            risk_multiplier = 3.0
        elif segment.risk_level == "mixed":
            risk_multiplier = 1.5

        channel_overhead = 0.0
        if segment.channel == "product_docs":
            channel_overhead = 0.001
        elif segment.channel == "marketing_web":
            channel_overhead = 0.0005

        noise = self._rng.uniform(-0.0005, 0.0005)
        total = max(0.0, (base + length_factor + channel_overhead) * risk_multiplier + noise)
        return total

    def process(self, workload_id: str, segments: Iterable[Segment], variant: str) -> List[SegmentResult]:
        results: List[SegmentResult] = []
        for seg in segments:
            start = time.perf_counter()

            # Hard-coded routing logic: emulate a simple if/else tree.
            if seg.risk_level == "high":
                # High-risk: always perform heavy human review path.
                sleep_time = self._processing_time_for_segment(seg) * 1.5
            elif seg.channel == "product_ui":
                # UI strings: assume lighter processing.
                sleep_time = self._processing_time_for_segment(seg) * 0.8
            else:
                sleep_time = self._processing_time_for_segment(seg)

            time.sleep(sleep_time)
            end = time.perf_counter()

            results.append(
                SegmentResult(
                    segment_id=seg.segment_id,
                    variant=variant,
                    workload_id=workload_id,
                    start_time=start,
                    end_time=end,
                )
            )
        return results


class RoutingRuleEngine:
    """Simple configuration-driven routing rules used by the treatment.

    In a real system this might be driven by YAML/JSON. Here we hard-code
    rules in Python but keep them data-oriented and easily replaceable.
    """

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def select_route(self, segment: Segment) -> str:
        """Return a symbolic route name for the segment."""

        # High-risk always goes through a heavy route.
        if segment.risk_level == "high":
            return "high_risk_full_review"

        # Canary: for WL2-like low/medium risk marketing or UI, 20% go to a new route.
        if segment.channel in {"marketing_web", "product_ui"} and segment.risk_level in {"low", "low_to_medium"}:
            if self._rng.random() < 0.2:
                return "low_risk_canary_v2"
            return "low_risk_standard"

        # Mixed workload: differentiate by content type and length.
        if segment.risk_level == "mixed":
            if segment.content_type in {"labeling", "safety_info", "legal_disclosure"}:
                return "mixed_docs_review"
            if segment.text_length < 80:
                return "mixed_light_ui"
            return "mixed_default"

        return "default_route"


class TreatmentOrchestrator:
    """Queue-based orchestrator with configurable routing and worker pool.

    This simulates:
    - A routing layer that maps segments to routes.
    - Multiple workers consuming from a queue in parallel.
    - Different processing profiles depending on route.
    """

    def __init__(self, rng: random.Random, num_workers: int = 4) -> None:
        self._rng = rng
        self._rules = RoutingRuleEngine(seed=123)
        self._num_workers = max(1, num_workers)

    def _processing_time_for_route(self, segment: Segment, route: str) -> float:
        base = 0.0015
        length_factor = 0.000008 * segment.text_length

        multiplier = 1.0
        if route == "high_risk_full_review":
            multiplier = 3.5
        elif route == "low_risk_canary_v2":
            multiplier = 1.1
        elif route == "low_risk_standard":
            multiplier = 0.9
        elif route == "mixed_docs_review":
            multiplier = 2.0
        elif route == "mixed_light_ui":
            multiplier = 0.7

        noise = self._rng.uniform(-0.0004, 0.0004)
        return max(0.0, (base + length_factor) * multiplier + noise)

    def process(self, workload_id: str, segments: Iterable[Segment], variant: str) -> List[SegmentResult]:
        queue: "Queue[Tuple[Segment, float]]" = Queue()
        results: List[SegmentResult] = []
        results_lock = threading.Lock()
        stop_sentinel = object()

        def worker() -> None:
            while True:
                try:
                    item = queue.get(timeout=0.1)
                except Empty:
                    continue
                if item is stop_sentinel:  # type: ignore[comparison-overlap]
                    break
                seg, start_time = item  # type: ignore[misc]
                route = self._rules.select_route(seg)
                sleep_time = self._processing_time_for_route(seg, route)
                time.sleep(sleep_time)
                end_time = time.perf_counter()
                with results_lock:
                    results.append(
                        SegmentResult(
                            segment_id=seg.segment_id,
                            variant=variant,
                            workload_id=workload_id,
                            start_time=start_time,
                            end_time=end_time,
                        )
                    )
                queue.task_done()

        threads: List[threading.Thread] = []
        for _ in range(self._num_workers):
            t = threading.Thread(target=worker, daemon=True)
            t.start()
            threads.append(t)

        # Enqueue segments
        for seg in segments:
            start = time.perf_counter()
            queue.put((seg, start))

        queue.join()

        # Stop workers
        for _ in threads:
            queue.put(stop_sentinel)  # type: ignore[arg-type]
        for t in threads:
            t.join()

        return results


def compute_latency_metrics(results: List[SegmentResult]) -> Tuple[float, float]:
    """Compute p50 and p95 latency from a list of results.

    Returns (p50, p95) in seconds.
    """

    if not results:
        return 0.0, 0.0
    latencies = sorted(r.latency for r in results)
    p50 = median(latencies)
    # p95 index
    idx = int(math.ceil(0.95 * len(latencies))) - 1
    idx = max(0, min(idx, len(latencies) - 1))
    p95 = latencies[idx]
    return p50, p95


def compute_throughput(results: List[SegmentResult]) -> float:
    """Compute segments per second based on first/last timestamps."""

    if not results:
        return 0.0
    start = min(r.start_time for r in results)
    end = max(r.end_time for r in results)
    duration = max(end - start, 1e-9)
    return len(results) / duration
