import re
from dataclasses import dataclass
from typing import List, Tuple

from .config import PipelineConfig


PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")
TAG_PATTERN = re.compile(r"<(/?)([a-zA-Z0-9]+)[^>]*>")


@dataclass
class QAResult:
    status: str  # "pass" or "fail"
    issues: List[str]
    length_ratio: float


def _extract_placeholders(text: str) -> List[str]:
    # Use finditer + group(0) so future changes to the regex (e.g., adding
    # capturing groups) do not silently change behavior.
    return [m.group(0) for m in PLACEHOLDER_PATTERN.finditer(text)]


def _check_placeholder_integrity(source: str, target: str, issues: List[str]) -> None:
    src_ph = _extract_placeholders(source)
    tgt_ph = _extract_placeholders(target)
    src_set = set(src_ph)
    tgt_set = set(tgt_ph)
    missing = src_set - tgt_set
    extra = tgt_set - src_set
    if missing:
        issues.append("placeholder_missing")
    if extra:
        issues.append("placeholder_extra")


def _extract_tags(text: str) -> List[Tuple[bool, str]]:
    tags: List[Tuple[bool, str]] = []
    for match in TAG_PATTERN.finditer(text):
        closing = bool(match.group(1))
        name = match.group(2).lower()
        tags.append((closing, name))
    return tags


def _check_tag_balance(source: str, target: str, issues: List[str]) -> None:
    # Very simple stack-based balance check for the target; we assume that
    # preserving the same set of tags as the source is handled by the
    # placeholder-like preservation in translation.
    stack: List[str] = []
    for closing, name in _extract_tags(target):
        if not closing:
            stack.append(name)
        else:
            if not stack or stack[-1] != name:
                issues.append("tag_mismatched")
                return
            stack.pop()
    if stack:
        issues.append("tag_unbalanced")


def run_qa(source: str, target: str, source_locale: str, target_locale: str, config: PipelineConfig) -> QAResult:
    issues: List[str] = []

    # Length ratio
    src_len = len(source) or 1
    tgt_len = len(target)
    ratio = tgt_len / src_len

    bounds = config.qa.length_ratio_bounds.get((source_locale, target_locale))
    if bounds is not None:
        if ratio < bounds.min_ratio or ratio > bounds.max_ratio:
            issues.append("length_ratio_out_of_bounds")

    _check_placeholder_integrity(source, target, issues)
    _check_tag_balance(source, target, issues)

    status = "pass" if not issues else "fail"
    return QAResult(status=status, issues=issues, length_ratio=ratio)
