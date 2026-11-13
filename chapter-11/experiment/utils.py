from __future__ import annotations

from typing import Iterable, List
import hashlib


def simple_tokenize(text: str) -> List[str]:
    # Very simple whitespace tokenization for deterministic behavior.
    return [t for t in text.strip().split() if t]


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def levenshtein_distance(a: str, b: str) -> int:
    # Classic dynamic-programming Levenshtein distance implementation.
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    # Ensure a is the shorter string to keep memory smaller
    if len(a) > len(b):
        a, b = b, a
    previous_row = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current_row = [i]
        for j, cb in enumerate(b, start=1):
            insert_cost = current_row[j - 1] + 1
            delete_cost = previous_row[j] + 1
            replace_cost = previous_row[j - 1] + (0 if ca == cb else 1)
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        previous_row = current_row
    return previous_row[-1]


def normalized_similarity(a: str, b: str) -> float:
    """Return a similarity score in [0,1] based on Levenshtein distance.

    similarity = 1 - dist / max_len
    """
    if not a and not b:
        return 1.0
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(a, b)
    return max(0.0, 1.0 - dist / float(max_len))


def dot(a: Iterable[float], b: Iterable[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def l2_norm(a: Iterable[float]) -> float:
    from math import sqrt

    return sqrt(sum(x * x for x in a))


def cosine_similarity(a: List[float], b: List[float]) -> float:
    na = l2_norm(a)
    nb = l2_norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot(a, b) / (na * nb)
