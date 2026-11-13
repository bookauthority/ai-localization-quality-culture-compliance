from __future__ import annotations

from typing import Dict, List, Tuple

from .assets import STYLE_EXAMPLES, VECTOR_TOP_K
from .utils import cosine_similarity


def embed_text(text: str) -> List[float]:
    """Deterministic toy embedding based on character statistics.

    This is not a real embedding model but provides a stable vector space for
    approximate similarity comparison within this constrained environment.
    """
    # Features: length, vowel count, consonant count, digit count, space count
    vowels = set("aeiouAEIOU")
    length = len(text)
    vowel_count = sum(1 for c in text if c in vowels)
    consonant_count = sum(1 for c in text if c.isalpha() and c not in vowels)
    digit_count = sum(1 for c in text if c.isdigit())
    space_count = sum(1 for c in text if c.isspace())

    # Normalize by length to keep numbers small and comparable
    if length == 0:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    return [
        float(length) / 100.0,
        float(vowel_count) / float(length),
        float(consonant_count) / float(length),
        float(digit_count) / float(length),
        float(space_count) / float(length),
    ]


class VectorIndex:
    def __init__(self) -> None:
        self._entries: List[Dict[str, object]] = []

    def build(self) -> None:
        self._entries = []
        for ex in STYLE_EXAMPLES:
            vec = embed_text(str(ex["source"]))
            entry = dict(ex)
            entry["vector"] = vec
            self._entries.append(entry)

    def query(
        self,
        language_pair: str,
        domain: str,
        text: str,
    ) -> List[Tuple[float, Dict[str, object]]]:
        """Return top-k style examples as (similarity, example_dict)."""
        if not self._entries:
            self.build()
        query_vec = embed_text(text)
        scored: List[Tuple[float, Dict[str, object]]] = []
        for entry in self._entries:
            if entry.get("language_pair") != language_pair:
                continue
            if entry.get("domain") != domain:
                continue
            vec = entry["vector"]  # type: ignore[assignment]
            sim = cosine_similarity(query_vec, vec)  # type: ignore[arg-type]
            scored.append((sim, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:VECTOR_TOP_K]


VECTOR_INDEX = VectorIndex()
