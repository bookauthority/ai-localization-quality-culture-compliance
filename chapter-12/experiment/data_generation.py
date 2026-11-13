from __future__ import annotations

"""Deterministic synthetic data generation for workloads and language pairs.

This offline experiment cannot call real vendor APIs or load real localization
corpora. Instead, we generate simple synthetic "source" segments that are
sufficient to exercise the experiment harness and metric calculations.

Each segment is represented as a small dictionary with a stable `segment_id`
constructed from the workload id, language pair, and an index. The `source`
text is a deterministic string based on those fields.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List

from .config import Workload


@dataclass
class Segment:
    """A single synthetic source segment.

    Attributes
    ----------
    segment_id:
        Stable identifier combining workload, language pair, and index.
    workload_id:
        Identifier for the workload this segment belongs to.
    source_lang:
        Source language code (always "en" in this simplified experiment).
    target_lang:
        Target language code (e.g., "de", "fr").
    source_text:
        Deterministic source text; not used for actual translation but helps
        mimic real segments.
    """

    segment_id: str
    workload_id: str
    source_lang: str
    target_lang: str
    source_text: str


def _make_segment_id(workload_id: str, lang_pair: str, index: int) -> str:
    return f"{workload_id}::{lang_pair}::seg{index:04d}"


def generate_segments_for_workload(
    workload: Workload,
    per_lang_pair_segments: int = 10,
) -> List[Segment]:
    """Generate a small, deterministic set of synthetic segments.

    Parameters
    ----------
    workload:
        Workload configuration object.
    per_lang_pair_segments:
        Number of segments to generate per language pair. In a real experiment
        this would match the actual corpus size; here we keep it small for
        bounded execution.
    """

    segments: List[Segment] = []

    for lang_pair in workload.language_pairs:
        src, tgt = lang_pair.split("->", 1)
        for i in range(per_lang_pair_segments):
            seg_id = _make_segment_id(workload.workload_id, lang_pair, i)
            text = (
                f"Synthetic source text {i} for {workload.workload_id} "
                f"{src}->{tgt}."
            )
            segments.append(
                Segment(
                    segment_id=seg_id,
                    workload_id=workload.workload_id,
                    source_lang=src,
                    target_lang=tgt,
                    source_text=text,
                )
            )
    return segments


def generate_all_segments(
    workloads: Iterable[Workload],
    per_lang_pair_segments: int = 10,
) -> Dict[str, List[Segment]]:
    """Generate synthetic segments for all workloads.

    Returns a mapping from workload_id to list of segments.
    """

    result: Dict[str, List[Segment]] = {}
    for wl in workloads:
        result[wl.workload_id] = generate_segments_for_workload(
            wl, per_lang_pair_segments=per_lang_pair_segments
        )
    return result


def iter_segments_for_workload(
    segments_by_workload: Dict[str, List[Segment]], workload_id: str
) -> Iterator[Segment]:
    """Yield segments for a given workload id in deterministic order."""

    for seg in segments_by_workload.get(workload_id, []):
        yield seg
