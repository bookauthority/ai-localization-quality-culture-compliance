from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


CHAPTER = 14
EXPERIMENT_ID = "exp-ch14-scaling-observability-continuous-improvement-v1"


@dataclass(frozen=True)
class WorkloadConfig:
    """Configuration for a synthetic workload.

    The parameters below control how the simulated pipeline behaves per
    baseline vs treatment for each workload.
    """

    workload_id: str
    description: str
    risk_level: str  # "high", "medium", "low"
    # Number of jobs per variant for this experiment (kept small for speed).
    jobs_per_variant: int
    # Base latency (ms) and quality/cost parameters for baseline and treatment.
    baseline_latency_ms: float
    treatment_latency_ms: float
    baseline_quality_mean: float
    treatment_quality_mean: float
    baseline_cost_cents: float
    treatment_cost_cents: float


# Define three workloads as per specification labels. These values are
# intentionally simple but distinct to give meaningful, deterministic
# differences between baseline and treatment.

WORKLOADS: List[WorkloadConfig] = [
    WorkloadConfig(
        workload_id="workload-pharma-high-risk-labeling",
        description=(
            "High-risk pharmaceutical labeling and patient information "
            "content with strong compliance and quality requirements."
        ),
        risk_level="high",
        jobs_per_variant=10,
        baseline_latency_ms=220.0,
        treatment_latency_ms=260.0,  # treatment slightly slower
        baseline_quality_mean=0.88,
        treatment_quality_mean=0.93,  # higher quality
        baseline_cost_cents=7.5,
        treatment_cost_cents=9.0,  # more expensive model
    ),
    WorkloadConfig(
        workload_id="workload-finance-medium-risk-disclosures-marketing",
        description=(
            "Regulated financial content mixing disclosures and marketing "
            "copy where both accuracy and conversion matter."
        ),
        risk_level="medium",
        jobs_per_variant=12,
        baseline_latency_ms=200.0,
        treatment_latency_ms=210.0,
        baseline_quality_mean=0.86,
        treatment_quality_mean=0.90,
        baseline_cost_cents=6.0,
        treatment_cost_cents=6.5,
    ),
    WorkloadConfig(
        workload_id="workload-saas-low-risk-ui-support",
        description=(
            "B2B SaaS / consumer-tech UI strings and knowledge base "
            "articles optimized for latency and throughput."
        ),
        risk_level="low",
        jobs_per_variant=15,
        baseline_latency_ms=150.0,
        treatment_latency_ms=145.0,  # treatment slightly faster
        baseline_quality_mean=0.82,
        treatment_quality_mean=0.84,
        baseline_cost_cents=3.5,
        treatment_cost_cents=3.7,
    ),
]


def variant_parameters(workload: WorkloadConfig, variant: str) -> Dict[str, float]:
    """Return variant-specific parameters for the simulator.

    Parameters are intentionally simple: they are used by the pipeline
    to determine overall latency, cost, and central tendency of
    automated quality.
    """

    if variant not in {"baseline", "treatment"}:
        raise ValueError(f"Unsupported variant: {variant}")

    if variant == "baseline":
        return {
            "target_latency_ms": workload.baseline_latency_ms,
            "target_quality_mean": workload.baseline_quality_mean,
            "target_cost_cents": workload.baseline_cost_cents,
        }
    else:
        return {
            "target_latency_ms": workload.treatment_latency_ms,
            "target_quality_mean": workload.treatment_quality_mean,
            "target_cost_cents": workload.treatment_cost_cents,
        }
