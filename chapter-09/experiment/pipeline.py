import time
from typing import Dict, List, Tuple

from .config import (
    FORBIDDEN_FINANCIAL_PHRASES,
    REQUIRED_FINANCIAL_DISCLAIMERS,
    TOKEN_SEPARATORS,
)


def simple_tokenize(text: str) -> List[str]:
    """A very small, deterministic whitespace/punctuation tokenizer.

    This is intentionally naive but sufficient for counting tokens and
    simulating workload size.
    """

    tokens: List[str] = []
    current: List[str] = []
    for ch in text:
        if ch in TOKEN_SEPARATORS:
            if current:
                tokens.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def pseudo_localize(text: str, target_lang: str) -> str:
    """A trivial, reversible pseudo-localization function.

    For demonstration, we uppercase the text and append the target language
    code. This allows us to run identical logic in baseline and treatment
    while having a clear transformation step to surround with checks.
    """

    return f"{text.upper()} [LOC-{target_lang}]"


def redact_pii(text: str) -> Tuple[str, int]:
    """Redact very simple PII patterns.

    - Any token containing '@' is replaced with '<EMAIL>'.
    - Any token with 6 or more digits is replaced with '<ID>'.

    Returns the redacted text and the number of redactions applied.
    """

    tokens = simple_tokenize(text)
    redactions = 0
    redacted_tokens: List[str] = []

    for tok in tokens:
        if "@" in tok:
            redacted_tokens.append("<EMAIL>")
            redactions += 1
        elif sum(1 for ch in tok if ch.isdigit()) >= 6:
            redacted_tokens.append("<ID>")
            redactions += 1
        else:
            redacted_tokens.append(tok)

    # Reconstruct with spaces; this discards original punctuation but
    # that is acceptable for this simulation.
    return " ".join(redacted_tokens), redactions


def check_financial_compliance(text: str) -> Dict[str, int]:
    """Run simple rule-based financial compliance checks.

    Returns a dict with integer counters:
    - required_missing: count of missing required disclaimers.
    - forbidden_present: count of forbidden phrases found.
    """

    lower = text.lower()
    required_missing = 0
    for phrase in REQUIRED_FINANCIAL_DISCLAIMERS:
        if phrase not in lower:
            required_missing += 1

    forbidden_present = 0
    for phrase in FORBIDDEN_FINANCIAL_PHRASES:
        if phrase in lower:
            forbidden_present += 1

    return {
        "required_missing": required_missing,
        "forbidden_present": forbidden_present,
    }


def run_document_baseline(doc: Dict[str, str], target_lang: str) -> Dict[str, float]:
    """Run the baseline pipeline on a single document.

    Baseline performs:
    - pseudo-localization only.
    - no redaction.
    - a trivial length-based QA check (not logged in metrics).
    """

    text = doc["text"]

    # Approximate tokens before localization.
    tokens_before = len(simple_tokenize(text))

    # Simulate localization.
    _ = pseudo_localize(text, target_lang)

    # Very minor sleep-free processing; we just rely on function cost.

    # Metrics we can faithfully measure here.
    metrics: Dict[str, float] = {
        "tokens": float(tokens_before),
    }
    return metrics


def run_document_treatment(doc: Dict[str, str], target_lang: str, workload_id: str) -> Dict[str, float]:
    """Run the treatment pipeline on a single document.

    Treatment performs:
    - pre-localization PII redaction.
    - pseudo-localization.
    - simple post-localization compliance checks for financial workloads.

    All measurements are purely numeric counters or timings.
    """

    text = doc["text"]

    # Pre-localization redaction.
    redacted_text, redactions = redact_pii(text)

    # Token counts before and after redaction to simulate size/complexity.
    tokens_before = len(simple_tokenize(text))
    tokens_after = len(simple_tokenize(redacted_text))

    # Localization over redacted text.
    localized = pseudo_localize(redacted_text, target_lang)

    # Post-localization compliance for financial workload.
    required_missing = 0
    forbidden_present = 0
    if workload_id == "w2-financial-disclosures":
        compliance = check_financial_compliance(localized)
        required_missing = compliance["required_missing"]
        forbidden_present = compliance["forbidden_present"]

    metrics: Dict[str, float] = {
        "tokens": float(tokens_before),
        "tokens_after_redaction": float(tokens_after),
        "redactions": float(redactions),
        "financial_required_missing": float(required_missing),
        "financial_forbidden_present": float(forbidden_present),
    }
    return metrics


def run_pipeline_for_workload(
    workload_id: str,
    workload: Dict[str, object],
    variant: str,
) -> Tuple[bool, Dict[str, float]]:
    """Run either the baseline or treatment pipeline over an entire workload.

    Returns (success, metrics) where metrics aggregates simple numeric
    quantities across all documents and target languages within the workload.

    Aggregated metrics include:
    - tokens: total tokens processed.
    - processing_time_ms: filled by the caller.
    - Additional treatment-only counts such as total redactions.
    """

    docs: List[Dict[str, str]] = workload["documents"]  # type: ignore[assignment]
    target_langs: List[str] = workload["target_langs"]  # type: ignore[assignment]

    total_tokens = 0.0
    total_tokens_after_redaction = 0.0
    total_redactions = 0.0
    total_required_missing = 0.0
    total_forbidden_present = 0.0

    # Simulate traversal over all documents and target languages.
    for doc in docs:
        for tgt in target_langs:
            if variant == "baseline":
                m = run_document_baseline(doc, tgt)
                total_tokens += m.get("tokens", 0.0)
            else:
                m = run_document_treatment(doc, tgt, workload_id)
                total_tokens += m.get("tokens", 0.0)
                total_tokens_after_redaction += m.get("tokens_after_redaction", 0.0)
                total_redactions += m.get("redactions", 0.0)
                total_required_missing += m.get("financial_required_missing", 0.0)
                total_forbidden_present += m.get("financial_forbidden_present", 0.0)

    metrics: Dict[str, float] = {
        "tokens": float(total_tokens),
    }

    if variant == "treatment":
        metrics.update(
            {
                "tokens_after_redaction": float(total_tokens_after_redaction),
                "redactions": float(total_redactions),
            }
        )
        # Only meaningful for the financial workload, but still numeric for others.
        metrics["financial_required_missing"] = float(total_required_missing)
        metrics["financial_forbidden_present"] = float(total_forbidden_present)

    success = True
    return success, metrics
