from __future__ import annotations

"""Simulated vendor adapters and hybrid routing logic.

Real-world deployments would implement HTTP clients and domain/model selection
for each vendor. Here we simulate vendors with deterministic pseudo-translation
and quality/latency characteristics.

The design goal is to mirror a vendor-agnostic adapter layer: upstream code
calls `translate` on a `Vendor` instance with normalized inputs and receives a
normalized response.
"""

import math
import time
from dataclasses import dataclass
from typing import Dict, Tuple

from .config import (
    BASELINE_VENDOR_ID,
    HYBRID_ROUTING_POLICY,
    VENDOR_A_ID,
    VENDOR_B_ID,
)
from .data_generation import Segment


@dataclass
class TranslationResult:
    """Result of a simulated vendor translation call.

    Attributes
    ----------
    output_text:
        Pseudo-translation of the input source text.
    latency_ms:
        Simulated latency in milliseconds for this call.
    quality_score:
        Synthetic per-segment quality score in [0, 1]. In a real system this
        would come from BLEU/COMET or human/machine judgments.
    """

    output_text: str
    latency_ms: float
    quality_score: float


class Vendor:
    """Abstract base class for all vendor adapters."""

    vendor_id: str

    def __init__(self, vendor_id: str) -> None:
        self.vendor_id = vendor_id

    def translate(self, segment: Segment) -> TranslationResult:
        """Translate a segment and return a simulated result.

        Subclasses may override latency and quality behavior to emulate
        different profiles. The base implementation provides deterministic
        pseudo-translation and neutral scores.
        """

        start = time.perf_counter()

        # Pseudo-translation: prepend vendor id and target language so we can
        # see which vendor handled the request in any debug prints.
        output = f"[{self.vendor_id}:{segment.target_lang}] {segment.source_text}"

        # Base latency and quality; subclasses adjust.
        base_latency_ms = 10.0
        base_quality = 0.75

        latency_ms = base_latency_ms
        quality = base_quality

        end = time.perf_counter()
        measured_ms = (end - start) * 1000.0
        # Use the maximum of measured time and synthetic latency to ensure
        # strictly positive numbers while staying deterministic-ish.
        latency_ms = max(latency_ms, measured_ms)

        return TranslationResult(
            output_text=output,
            latency_ms=latency_ms,
            quality_score=quality,
        )


class BaselineVendor(Vendor):
    """Single-vendor baseline with conservative, uniform characteristics."""

    def __init__(self) -> None:
        super().__init__(BASELINE_VENDOR_ID)

    def translate(self, segment: Segment) -> TranslationResult:  # type: ignore[override]
        start = time.perf_counter()
        output = f"[{self.vendor_id}:{segment.target_lang}] {segment.source_text}"

        # Baseline is reasonably fast but not specialized.
        synthetic_latency_ms = 12.0
        base_quality = 0.78

        # Adjust quality slightly by workload / language to create variance.
        modifier = _quality_modifier(
            self.vendor_id, segment.workload_id, segment.target_lang
        )
        quality = max(0.0, min(1.0, base_quality + modifier))

        end = time.perf_counter()
        measured_ms = (end - start) * 1000.0
        latency_ms = max(synthetic_latency_ms, measured_ms)

        return TranslationResult(output, latency_ms, quality)


class VendorA(Vendor):
    """Simulated MT vendor A with strengths in European languages."""

    def __init__(self) -> None:
        super().__init__(VENDOR_A_ID)

    def translate(self, segment: Segment) -> TranslationResult:  # type: ignore[override]
        start = time.perf_counter()
        output = f"[{self.vendor_id}:{segment.target_lang}] {segment.source_text}"

        # Vendor A is slightly faster overall.
        synthetic_latency_ms = 9.0
        base_quality = 0.80

        modifier = _quality_modifier(
            self.vendor_id, segment.workload_id, segment.target_lang
        )
        quality = max(0.0, min(1.0, base_quality + modifier))

        end = time.perf_counter()
        measured_ms = (end - start) * 1000.0
        latency_ms = max(synthetic_latency_ms, measured_ms)

        return TranslationResult(output, latency_ms, quality)


class VendorB(Vendor):
    """Simulated LLM-like vendor B with strengths in Asian languages."""

    def __init__(self) -> None:
        super().__init__(VENDOR_B_ID)

    def translate(self, segment: Segment) -> TranslationResult:  # type: ignore[override]
        start = time.perf_counter()
        output = f"[{self.vendor_id}:{segment.target_lang}] {segment.source_text}"

        # Vendor B is a bit slower but can be higher quality on some pairs.
        synthetic_latency_ms = 15.0
        base_quality = 0.82

        modifier = _quality_modifier(
            self.vendor_id, segment.workload_id, segment.target_lang
        )
        quality = max(0.0, min(1.0, base_quality + modifier))

        end = time.perf_counter()
        measured_ms = (end - start) * 1000.0
        latency_ms = max(synthetic_latency_ms, measured_ms)

        return TranslationResult(output, latency_ms, quality)


def _quality_modifier(vendor_id: str, workload_id: str, target_lang: str) -> float:
    """Deterministic modifier that varies by vendor/workload/language.

    This is not intended to reflect reality—only to create non-trivial but
    fully deterministic variation so metrics differ between vendors and
    workloads.
    """

    # Hash-like deterministic mapping based on strings.
    key = f"{vendor_id}|{workload_id}|{target_lang}"
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    # Map to a small range around zero, e.g. [-0.05, 0.05].
    return ((h % 1000) / 1000.0 - 0.5) * 0.1


def make_baseline_vendor() -> BaselineVendor:
    return BaselineVendor()


def make_hybrid_vendors() -> Dict[str, Vendor]:
    """Construct all vendors used in the hybrid treatment."""

    return {
        BASELINE_VENDOR_ID: BaselineVendor(),
        VENDOR_A_ID: VendorA(),
        VENDOR_B_ID: VendorB(),
    }


def select_vendor_for_segment(
    segment: Segment, vendors: Dict[str, Vendor]
) -> Vendor:
    """Select a vendor for the given segment using the hybrid routing policy.

    The routing policy is defined by workload and target language; if no
    explicit entry exists, we fall back to the baseline vendor.
    """

    wl_policy = HYBRID_ROUTING_POLICY.get(segment.workload_id, {})
    vendor_id = wl_policy.get(segment.target_lang, BASELINE_VENDOR_ID)
    return vendors[vendor_id]
