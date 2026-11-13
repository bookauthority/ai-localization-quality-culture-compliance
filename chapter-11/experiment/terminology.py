from __future__ import annotations

from typing import Dict, List, Tuple

from .assets import TERMBASE, FORBIDDEN_TERMS, NON_TRANSLATABLES
from .utils import simple_tokenize


def get_glossary_for_pair(language_pair: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for entry in TERMBASE:
        if entry.get("language_pair") == language_pair and entry.get("status") == "preferred":
            src = str(entry.get("source_term"))
            tgt = str(entry.get("target_term"))
            mapping[src] = tgt
    return mapping


def get_forbidden_for_pair(language_pair: str) -> List[str]:
    forbidden: List[str] = []
    for entry in FORBIDDEN_TERMS:
        if entry.get("language_pair") == language_pair and entry.get("forbidden_flag") == "1":
            forbidden.append(str(entry.get("target_term")))
    return forbidden


def enforce_glossary(
    language_pair: str,
    source: str,
    draft_translation: str,
) -> str:
    """Apply a very simple glossary-based post-edit.

    For each glossary entry whose source term appears in the source, ensure
    that the preferred target term appears at least once in the translation.
    If missing, we append it near the end.

    Non-translatable items are left unchanged by design because our
    pseudo-translation functions already preserve them.
    """
    glossary = get_glossary_for_pair(language_pair)
    translation = draft_translation

    for src, tgt in glossary.items():
        if src in source:
            if tgt not in translation:
                if translation and not translation.endswith(" "):
                    translation += " "
                translation += tgt
    return translation


def terminology_check(
    language_pair: str,
    source: str,
    translation: str,
) -> Tuple[int, int, int]:
    """Return (correct_count, required_count, violations_count).

    - required_count: number of required glossary terms that should appear
      based on the source.
    - correct_count: number of those whose preferred target actually appears.
    - violations_count: number of forbidden target terms appearing.
    """
    glossary = get_glossary_for_pair(language_pair)
    forbidden = get_forbidden_for_pair(language_pair)

    lower_translation = translation.lower()
    required_count = 0
    correct_count = 0

    for src, tgt in glossary.items():
        if src in source:
            required_count += 1
            if tgt.lower() in lower_translation:
                correct_count += 1

    violations_count = 0
    for ft in forbidden:
        if ft.lower() in lower_translation:
            violations_count += 1

    return correct_count, required_count, violations_count


def count_non_translatables(source: str, translation: str) -> Tuple[int, int]:
    """Return (present_in_source_and_translation, present_in_source_total)."""
    present_source = [nt for nt in NON_TRANSLATABLES if nt in source]
    present_translation = [nt for nt in present_source if nt in translation]
    return len(present_translation), len(present_source)
