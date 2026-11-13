from __future__ import annotations

from typing import Any, Dict, List

import random

from .assets import (
    TM_MATCH_THRESHOLDS,
    VECTOR_SIMILARITY_THRESHOLD,
)
from .metrics import (
    compute_length_ratios,
    compute_terminology_accuracy,
    compute_terminology_violation_rate,
    compute_percentage,
)
from .terminology import enforce_glossary, terminology_check
from .tm import tm_lookup
from .vectorstore import VECTOR_INDEX


# --- Pseudo-translation helpers -------------------------------------------------


def pseudo_translate_baseline(text: str, seed: int) -> str:
    """Deterministic 'translation' that does not use assets.

    It reverses characters in each word and randomly uppercases some letters,
    controlled by the given seed. Non-alphabetical characters are preserved.
    """
    rng = random.Random(seed)
    words = text.split(" ")
    out_words: List[str] = []
    for w in words:
        rev = list(w[::-1])
        for i, ch in enumerate(rev):
            if ch.isalpha() and rng.random() < 0.2:
                rev[i] = ch.upper()
        out_words.append("".join(rev))
    return " ".join(out_words)


def pseudo_translate_treatment(
    source: str,
    language_pair: str,
    domain: str,
    seed: int,
    use_tm: bool,
    use_glossary: bool,
    use_vector: bool,
) -> Dict[str, Any]:
    """Treatment translation uses TM, glossary, and style hints when enabled.

    Returns a dict with keys:
      - translation: str
      - used_tm: bool
      - tm_similarity: float
      - used_vector: bool
      - vector_max_similarity: float
    """
    rng = random.Random(seed)

    used_tm = False
    tm_similarity = 0.0
    tm_candidate = None

    if use_tm:
        tm_res = tm_lookup(language_pair, source, domain)
        if tm_res.match is not None:
            used_tm = True
            tm_similarity = tm_res.similarity
            tm_candidate = tm_res.match["target"]

    used_vector = False
    vector_max_similarity = 0.0

    if use_vector:
        results = VECTOR_INDEX.query(language_pair, domain, source)
        if results:
            vector_max_similarity = max(score for score, _ in results)
            if vector_max_similarity >= VECTOR_SIMILARITY_THRESHOLD:
                used_vector = True

    if tm_candidate is not None and tm_similarity >= TM_MATCH_THRESHOLDS["high_fuzzy_min"]:
        draft = tm_candidate
    else:
        # Create a more fluent-looking pseudo-translation compared to baseline
        words = source.split(" ")
        out_words: List[str] = []
        for w in words:
            if w in ("CloudSync", "CloudSync Pro"):
                out_words.append(w)
            else:
                shuffled = list(w)
                rng.shuffle(shuffled)
                out_words.append("".join(shuffled))
        draft = " ".join(out_words)

    if use_glossary:
        draft = enforce_glossary(language_pair, source, draft)

    return {
        "translation": draft,
        "used_tm": used_tm,
        "tm_similarity": tm_similarity,
        "used_vector": used_vector,
        "vector_max_similarity": vector_max_similarity,
    }


# --- Workload runners -----------------------------------------------------------


def run_baseline_for_workload(workload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the baseline pipeline for one workload.

    Returns dict with at least a `metrics` sub-dict of numeric values.
    """
    language_pair = workload["language_pair"]
    segments = workload["segments"]

    sources: List[str] = []
    translations: List[str] = []
    # For terminology metrics we still run checks, though no enforcement is
    # applied. This allows us to compare baseline vs treatment.
    term_correct_counts: List[int] = []
    term_required_counts: List[int] = []
    segments_with_violation = 0

    for idx, seg in enumerate(segments):
        source = seg["source"]
        domain = seg.get("domain", "")
        seed = hash((workload["id"], "baseline", idx)) & 0xFFFFFFFF
        translation = pseudo_translate_baseline(source, seed)

        sources.append(source)
        translations.append(translation)

        # terminology check
        c, r, v = terminology_check(language_pair, source, translation)
        term_correct_counts.append(c)
        term_required_counts.append(r)
        if v > 0:
            segments_with_violation += 1

    avg_len_ratio = compute_length_ratios(sources, translations)
    term_acc = compute_terminology_accuracy(term_correct_counts, term_required_counts)
    term_violation_rate = compute_terminology_violation_rate(
        segments_with_violation, len(segments)
    )

    metrics: Dict[str, float] = {
        "avg_length_ratio": float(avg_len_ratio),
        "terminology_accuracy": float(term_acc),
        "terminology_violation_rate": float(term_violation_rate),
        # Asset hit rates are by design 0 in baseline.
        "asset_hit_rate_tm": 0.0,
        "asset_hit_rate_termbase": 0.0,
        "asset_hit_rate_vector": 0.0,
    }

    return {
        "success": True,
        "metrics": metrics,
    }


def run_treatment_for_workload(workload: Dict[str, Any]) -> Dict[str, Any]:
    """Run the treatment pipeline for one workload.

    Treatment uses TM, glossary enforcement, and vector search.
    """
    language_pair = workload["language_pair"]
    segments = workload["segments"]

    sources: List[str] = []
    translations: List[str] = []
    term_correct_counts: List[int] = []
    term_required_counts: List[int] = []
    segments_with_violation = 0

    tm_hit_count = 0
    termbase_hit_segments = 0
    vector_hit_segments = 0

    for idx, seg in enumerate(segments):
        source = seg["source"]
        domain = seg.get("domain", "")
        seed = hash((workload["id"], "treatment", idx)) & 0xFFFFFFFF

        result = pseudo_translate_treatment(
            source=source,
            language_pair=language_pair,
            domain=domain,
            seed=seed,
            use_tm=True,
            use_glossary=True,
            use_vector=True,
        )
        translation = result["translation"]
        used_tm = bool(result["used_tm"])
        used_vector = bool(result["used_vector"])

        sources.append(source)
        translations.append(translation)

        if used_tm:
            tm_hit_count += 1
        if used_vector:
            vector_hit_segments += 1

        c, r, v = terminology_check(language_pair, source, translation)
        term_correct_counts.append(c)
        term_required_counts.append(r)
        if r > 0:
            termbase_hit_segments += 1
        if v > 0:
            segments_with_violation += 1

    avg_len_ratio = compute_length_ratios(sources, translations)
    term_acc = compute_terminology_accuracy(term_correct_counts, term_required_counts)
    term_violation_rate = compute_terminology_violation_rate(
        segments_with_violation, len(segments)
    )
    asset_hit_rate_tm = compute_percentage(tm_hit_count, len(segments))
    asset_hit_rate_termbase = compute_percentage(termbase_hit_segments, len(segments))
    asset_hit_rate_vector = compute_percentage(vector_hit_segments, len(segments))

    metrics: Dict[str, float] = {
        "avg_length_ratio": float(avg_len_ratio),
        "terminology_accuracy": float(term_acc),
        "terminology_violation_rate": float(term_violation_rate),
        "asset_hit_rate_tm": float(asset_hit_rate_tm),
        "asset_hit_rate_termbase": float(asset_hit_rate_termbase),
        "asset_hit_rate_vector": float(asset_hit_rate_vector),
    }

    return {
        "success": True,
        "metrics": metrics,
    }
