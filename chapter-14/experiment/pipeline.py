from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict

from .config import WorkloadConfig, variant_parameters
from .instrumentation import MetricRecorder, StructuredLogger, timed_stage


@dataclass
class PipelineResult:
    success: bool
    metrics: Dict[str, float]


class LocalizationPipeline:
    """Simulated localization pipeline with instrumentation.

    The goal is to provide deterministic yet distinct behavior for
    baseline vs treatment while exercising stage-level logging and
    metric collection.
    """

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def _stage_noise(self, scale: float) -> float:
        # Use a symmetric bounded noise around 0 with magnitude <= scale.
        return (self._rng.random() - 0.5) * 2.0 * scale

    def _bounded_quality(self, center: float) -> float:
        # Add small noise while keeping within [0, 1].
        q = center + self._stage_noise(0.03)
        return max(0.0, min(1.0, q))

    def run(
        self,
        workload: WorkloadConfig,
        variant: str,
        run_index: int,
    ) -> PipelineResult:
        params = variant_parameters(workload, variant)
        target_latency = params["target_latency_ms"]
        target_quality_mean = params["target_quality_mean"]
        target_cost = params["target_cost_cents"]

        correlation_id = f"{workload.workload_id}-{variant}-{run_index}"
        logger = StructuredLogger(correlation_id=correlation_id)
        recorder = MetricRecorder()

        total_latency = 0.0

        stages = [
            "ingestion",
            "analysis",
            "localization",
            "qa",
            "compliance",
            "delivery",
        ]

        # Stage weights approximate contribution to target latency.
        stage_weights = {
            "ingestion": 0.10,
            "analysis": 0.15,
            "localization": 0.40,
            "qa": 0.15,
            "compliance": 0.10,
            "delivery": 0.10,
        }

        for stage in stages:
            weight = stage_weights[stage]
            # Simulate a deterministic latency for this stage using the
            # seeded RNG rather than wall-clock timing.
            simulated_stage_latency = target_latency * weight + self._stage_noise(5.0)
            simulated_stage_latency = max(1.0, simulated_stage_latency)
            metric_name = f"simulated_{stage}_latency_ms"
            recorder.record(metric_name, simulated_stage_latency)
            total_latency += simulated_stage_latency

            with timed_stage(
                logger,
                recorder,
                stage,
                simulated_latency_ms=simulated_stage_latency,
            ):
                # We intentionally avoid significant computation here to
                # keep execution fast; all latency is represented by the
                # simulated value above.
                pass

        recorder.record("end_to_end_latency_ms", total_latency)

        # Simulated quality and cost.
        quality = self._bounded_quality(target_quality_mean)
        recorder.record("automated_quality_score", quality)

        # Treatment for high/medium risk may incur slightly higher cost
        # variability to reflect dynamic safeguards.
        cost_noise_scale = 0.25 if workload.risk_level in {"high", "medium"} else 0.15
        cost = max(0.0, target_cost + self._stage_noise(cost_noise_scale))
        recorder.record("cost_cents", cost)

        # Simple guardrail: mark run as failed if quality is too low
        # relative to workload risk.
        if workload.risk_level == "high":
            success_threshold = 0.90
        elif workload.risk_level == "medium":
            success_threshold = 0.85
        else:
            success_threshold = 0.80

        success = quality >= success_threshold
        recorder.record("success_indicator", 1.0 if success else 0.0)

        # Example risk indicator: very low quality at high risk.
        if workload.risk_level == "high" and quality < 0.85:
            logger.warning(
                "quality_below_high_risk_threshold",
                quality=quality,
                threshold=0.9,
            )

        return PipelineResult(success=success, metrics=recorder.metrics.copy())
