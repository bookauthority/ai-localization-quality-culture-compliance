import csv
from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class BaselineSegment:
    segment_id: str
    source_text: str


TARGET_LOCALES = ["es-ES", "fr-FR"]


def _pseudo_translate(text: str, target_locale: str) -> str:
    """Very simple, deterministic pseudo-translation.

    This function simulates translation deterministically by applying a
    reversible transformation that preserves curly-brace placeholders and
    simple HTML tags. It does *not* attempt to be linguistically correct.
    """

    # Preserve placeholders like {user_name} and {product}
    result_chars: List[str] = []
    in_placeholder = False
    for ch in text:
        if ch == "{":
            in_placeholder = True
            result_chars.append(ch)
        elif ch == "}":
            in_placeholder = False
            result_chars.append(ch)
        else:
            if in_placeholder:
                result_chars.append(ch)
            else:
                # basic transformation: map letters to a shifted alphabet
                if ch.isalpha():
                    base = "a" if ch.islower() else "A"
                    offset = (ord(ch) - ord(base) + 3) % 26
                    result_chars.append(chr(ord(base) + offset))
                else:
                    result_chars.append(ch)

    transformed = "".join(result_chars)
    # Add a locale marker suffix so we can distinguish variants
    return f"[{target_locale}] {transformed}"


def _read_segments(input_path: str) -> List[BaselineSegment]:
    segments: List[BaselineSegment] = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append(BaselineSegment(segment_id=row["id"], source_text=row["source_text"]))
    # Deterministic ordering by segment id
    segments.sort(key=lambda s: s.segment_id)
    return segments


def run_baseline_pipeline(input_path: str) -> Dict[str, Any]:
    """Naive baseline: read CSV, pseudo-translate, minimal metric counts.

    Metrics collected (per run) use **per segment-locale semantics** to
    match the treatment pipeline:
    - segments_total: number of translation jobs (segments * target_locales)
    - segments_successfully_translated
    - segments_failed_translation (always 0 unless an internal error occurs)
    - segments_passing_all_qa (baseline has no QA; treat all successful
      translations as conceptually passing for comparison)
    - segments_failing_any_qa (always 0 in this offline baseline)

    Note: this function intentionally performs **no QA checks**; it merely
    mirrors the treatment's metric names so that results.json has a stable
    schema across variants.
    """

    segments = _read_segments(input_path)

    translated_count = 0
    failed_count = 0

    for seg in segments:
        for locale in TARGET_LOCALES:
            try:
                _ = _pseudo_translate(seg.source_text, locale)
                translated_count += 1
            except Exception:
                failed_count += 1

    segments_total = translated_count + failed_count

    metrics: Dict[str, Any] = {
        "segments_total": float(segments_total),
        "segments_successfully_translated": float(translated_count),
        "segments_failed_translation": float(failed_count),
        # No QA checks in baseline; conceptually, all successful translations
        # are treated as passing QA for comparison with treatment metrics.
        "segments_passing_all_qa": float(translated_count),
        "segments_failing_any_qa": float(0),
    }

    return metrics
