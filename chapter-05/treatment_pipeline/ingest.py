import csv
from dataclasses import dataclass
from typing import List


@dataclass
class Segment:
    segment_id: str
    source_text: str
    source_locale: str
    content_type: str


def ingest_csv(path: str) -> List[Segment]:
    segments: List[Segment] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append(
                Segment(
                    segment_id=row["id"],
                    source_text=row["source_text"],
                    source_locale=row.get("source_locale", "en-US") or "en-US",
                    content_type=row.get("content_type", "unknown") or "unknown",
                )
            )
    segments.sort(key=lambda s: s.segment_id)
    return segments
