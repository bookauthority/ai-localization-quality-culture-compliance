from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .data import SourceItem


@dataclass
class BaselineOutput:
    source_id: str
    workload: str
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    market: str
    channel: str
    topic: str
    risk_level: str
    generic_qa_flags: List[str]


@dataclass
class TreatmentOutput:
    source_id: str
    workload: str
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    market: str
    channel: str
    topic: str
    risk_level: str
    cultural_risk_score: float
    source_cultural_red_flags: List[str]
    target_cultural_red_flags: List[str]
    imagery_metaphor_actions: List[Dict[str, str]]
    routing_decision: str


# --- Helper functions used by both pipelines ---


def _simple_translate(text: str, target_language: str) -> str:
    """Mock translation: add a language tag and make minimal changes.

    The goal is to be deterministic, not realistic.
    """

    return f"[{target_language}] " + text


def _detect_placeholders(text: str) -> bool:
    """Check for simple {{placeholder}}-style markers."""

    return "{{" in text and "}}" in text


def _generic_qa(text: str, translated: str) -> List[str]:
    flags: List[str] = []

    if abs(len(text) - len(translated)) > len(text) * 0.5:
        flags.append("length_mismatch")

    if _detect_placeholders(text) and not _detect_placeholders(translated):
        flags.append("placeholder_missing")

    # Very simple toxicity flag based on specific words
    toxic_tokens = ["stupid", "idiot"]
    if any(tok in translated.lower() for tok in toxic_tokens):
        flags.append("potential_toxicity")

    return flags


def _cultural_risk_score(item: SourceItem) -> float:
    base = 0.1
    if item.risk_level == "high":
        base = 0.8
    elif item.risk_level == "medium":
        base = 0.4

    if item.channel in {"patient_leaflet_pdf", "patient_education_web"}:
        base += 0.1

    if item.topic in {"disease_education", "side_effects_and_warnings"}:
        base += 0.1

    return max(0.0, min(1.0, base))


_CULTURAL_FLAG_KEYWORDS = {
    "religious_reference": ["god", "allah", "church", "temple"],
    "mental_health": ["depression", "self-harm", "suicide"],
    "reproductive_health": ["reproductive", "pregnancy", "fertility"],
    "shame_stigma": ["ashamed", "shame", "stigma"],
    "sports_metaphor": ["slam dunk", "home run", "touchdown"],
    "work_culture": ["burn the midnight oil"],
}


def _detect_cultural_red_flags(text: str) -> List[str]:
    lowered = text.lower()
    flags: List[str] = []
    for flag, keywords in _CULTURAL_FLAG_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in lowered:
                flags.append(flag)
                break
    return flags


def _apply_cultural_adaptations(item: SourceItem, text: str) -> (str, List[Dict[str, str]]):
    """Apply simple rule-based 'adaptations' for metaphors and tone.

    Returns the adapted text and a list of recorded actions.
    """

    actions: List[Dict[str, str]] = []
    adapted = text

    replacements = [
        ("slam dunk", "clear success"),
        ("home run", "great success"),
        ("touchdown", "major achievement"),
        ("burn the midnight oil", "work late"),
        ("game changer", "significant improvement"),
    ]

    for src, tgt in replacements:
        if src in adapted:
            adapted = adapted.replace(src, tgt)
            actions.append({
                "type": "metaphor_replaced",
                "source_snippet": src,
                "target_snippet": tgt,
            })

    # Market-specific softening / politeness tweaks
    if item.market in {"ja-JP", "es-MX", "ar-SA", "hi-IN"}:
        if "please" not in adapted.lower():
            adapted = adapted + " Please."  # naive politeness
            actions.append({
                "type": "politeness_added",
                "source_snippet": "",
                "target_snippet": "Please.",
            })

    return adapted, actions


def run_baseline_pipeline(items: List[SourceItem]) -> List[BaselineOutput]:
    outputs: List[BaselineOutput] = []
    for item in items:
        translated = _simple_translate(item.source_text, item.target_language)
        qa_flags = _generic_qa(item.source_text, translated)
        outputs.append(
            BaselineOutput(
                source_id=item.source_id,
                workload=item.workload,
                source_text=item.source_text,
                target_text=translated,
                source_language=item.source_language,
                target_language=item.target_language,
                market=item.market,
                channel=item.channel,
                topic=item.topic,
                risk_level=item.risk_level,
                generic_qa_flags=qa_flags,
            )
        )
    return outputs


def run_treatment_pipeline(items: List[SourceItem]) -> List[TreatmentOutput]:
    outputs: List[TreatmentOutput] = []
    for item in items:
        translated = _simple_translate(item.source_text, item.target_language)

        # Apply cultural adaptations on top of simple translation
        adapted_text, actions = _apply_cultural_adaptations(item, translated)

        src_flags = _detect_cultural_red_flags(item.source_text)
        tgt_flags = _detect_cultural_red_flags(adapted_text)
        score = _cultural_risk_score(item)

        if score >= 0.7 or len(src_flags) + len(tgt_flags) >= 2:
            routing = "cultural_review_required"
        elif score >= 0.4:
            routing = "sample_review"
        else:
            routing = "no_cultural_review"

        outputs.append(
            TreatmentOutput(
                source_id=item.source_id,
                workload=item.workload,
                source_text=item.source_text,
                target_text=adapted_text,
                source_language=item.source_language,
                target_language=item.target_language,
                market=item.market,
                channel=item.channel,
                topic=item.topic,
                risk_level=item.risk_level,
                cultural_risk_score=score,
                source_cultural_red_flags=src_flags,
                target_cultural_red_flags=tgt_flags,
                imagery_metaphor_actions=actions,
                routing_decision=routing,
            )
        )
    return outputs
