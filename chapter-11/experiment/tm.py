from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .assets import TMS, TM_MATCH_THRESHOLDS
from .utils import normalized_similarity


class TMLookupResult:
    def __init__(self, match: Optional[Dict[str, str]], similarity: float) -> None:
        self.match = match
        self.similarity = similarity


def tm_lookup(language_pair: str, source: str, domain: str) -> TMLookupResult:
    """Return best TM match for given source and domain.

    Similarity is a normalized score in [0,1]. Matches below low_fuzzy_min
    are treated as no-match (match=None, similarity=0).
    """
    entries = TMS.get(language_pair, [])
    best_sim = 0.0
    best_entry: Optional[Dict[str, str]] = None

    for entry in entries:
        if entry.get("domain") != domain:
            continue
        sim = normalized_similarity(source, entry.get("source", ""))
        if sim > best_sim:
            best_sim = sim
            best_entry = entry

    if best_sim < TM_MATCH_THRESHOLDS["low_fuzzy_min"]:
        return TMLookupResult(None, 0.0)
    return TMLookupResult(best_entry, best_sim)
