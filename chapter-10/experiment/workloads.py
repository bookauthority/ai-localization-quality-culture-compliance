from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .core import Segment


@dataclass
class WorkloadConfig:
    workload_id: str
    description: str
    num_segments: int
    risk_level: str
    languages: List[str]
    channels: List[str]
    content_types: List[str]


def _make_segments(cfg: WorkloadConfig, rng: random.Random) -> List[Segment]:
    segments: List[Segment] = []
    for i in range(cfg.num_segments):
        language = rng.choice(cfg.languages)
        channel = rng.choice(cfg.channels)
        content_type = rng.choice(cfg.content_types)

        if cfg.workload_id == "WL1-high-risk-product-docs":
            text_len = rng.randint(100, 400)
        elif cfg.workload_id == "WL2-low-risk-marketing-and-ui":
            if content_type in {"cta_button", "tooltip"}:
                text_len = rng.randint(5, 15)
            else:
                text_len = rng.randint(20, 80)
        else:  # WL3
            # Mixed; vary widely
            text_len = rng.randint(10, 300)

        seg = Segment(
            segment_id=f"{cfg.workload_id}-seg-{i}",
            language=language,
            channel=channel,
            content_type=content_type,
            risk_level=cfg.risk_level,
            text_length=text_len,
        )
        segments.append(seg)
    return segments


def build_workloads(seed: int = 42) -> Dict[str, List[Segment]]:
    rng = random.Random(seed)

    wl1_cfg = WorkloadConfig(
        workload_id="WL1-high-risk-product-docs",
        description="High-risk product documentation and labeling.",
        num_segments=60,
        risk_level="high",
        languages=["fr-FR", "de-DE", "es-ES", "ja-JP"],
        channels=["product_docs", "regulatory_portal"],
        content_types=["labeling", "safety_info", "legal_disclosure"],
    )

    wl2_cfg = WorkloadConfig(
        workload_id="WL2-low-risk-marketing-and-ui",
        description="Low-risk marketing and product UI.",
        num_segments=120,
        risk_level="low_to_medium",
        languages=["fr-FR", "de-DE", "es-MX", "pt-BR", "zh-CN"],
        channels=["marketing_web", "product_ui"],
        content_types=["short_copy", "cta_button", "tooltip"],
    )

    wl3_cfg = WorkloadConfig(
        workload_id="WL3-peak-load-stress-test",
        description="Synthetic peak-load workload.",
        num_segments=200,
        risk_level="mixed",
        languages=[
            "en-GB",
            "fr-FR",
            "de-DE",
            "es-ES",
            "it-IT",
            "ja-JP",
            "ko-KR",
            "zh-CN",
        ],
        channels=["product_docs", "marketing_web", "support_kb"],
        content_types=["labeling", "short_copy", "mixed", "tooltip"],
    )

    workloads: Dict[str, List[Segment]] = {}
    for cfg in (wl1_cfg, wl2_cfg, wl3_cfg):
        workloads[cfg.workload_id] = _make_segments(cfg, rng)

    return workloads
