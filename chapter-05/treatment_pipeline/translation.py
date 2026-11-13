from dataclasses import dataclass
from typing import Dict, List


@dataclass
class GlossaryEntry:
    source: str
    target_es: str
    target_fr: str


def load_glossary(path: str) -> Dict[str, GlossaryEntry]:
    import csv

    entries: Dict[str, GlossaryEntry] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = GlossaryEntry(
                source=row["source"],
                target_es=row["es-ES"],
                target_fr=row["fr-FR"],
            )
            entries[entry.source] = entry
    return entries


def _pseudo_translate_preserving_placeholders(text: str, target_locale: str) -> str:
    """Pseudo-translate while preserving placeholders and basic tags.

    - Curly-brace placeholders are preserved verbatim.
    - Text content is transformed deterministically.
    """

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
                if ch.isalpha():
                    base = "a" if ch.islower() else "A"
                    offset = (ord(ch) - ord(base) + 5) % 26
                    result_chars.append(chr(ord(base) + offset))
                else:
                    result_chars.append(ch)
    return f"[{target_locale}] {''.join(result_chars)}"


def apply_glossary(text: str, glossary: Dict[str, GlossaryEntry], target_locale: str) -> str:
    # Very naive glossary application: direct string replacement for keys
    for source_term, entry in glossary.items():
        if source_term in text:
            if target_locale == "es-ES":
                text = text.replace(source_term, entry.target_es)
            elif target_locale == "fr-FR":
                text = text.replace(source_term, entry.target_fr)
    return text


def translate_with_glossary(text: str, target_locale: str, glossary: Dict[str, GlossaryEntry]) -> str:
    base_translation = _pseudo_translate_preserving_placeholders(text, target_locale)
    return apply_glossary(base_translation, glossary, target_locale)
