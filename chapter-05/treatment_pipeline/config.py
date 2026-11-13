from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class LengthRatioBounds:
    min_ratio: float
    max_ratio: float


@dataclass
class QAConfig:
    length_ratio_bounds: Dict[Tuple[str, str], LengthRatioBounds]


@dataclass
class PipelineConfig:
    target_locales: tuple
    qa: QAConfig


def default_config() -> PipelineConfig:
    # For simplicity, configure the same bounds for en->es and en->fr
    bounds = LengthRatioBounds(min_ratio=0.5, max_ratio=2.0)
    qa_cfg = QAConfig(length_ratio_bounds={("en-US", "es-ES"): bounds, ("en-US", "fr-FR"): bounds})
    return PipelineConfig(target_locales=("es-ES", "fr-FR"), qa=qa_cfg)
