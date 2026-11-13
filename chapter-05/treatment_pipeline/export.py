import csv
from dataclasses import dataclass
from typing import List


@dataclass
class ExportRecord:
    segment_id: str
    source_locale: str
    target_locale: str
    source_text: str
    target_text: str
    content_type: str
    qa_status: str
    qa_issues: List[str]
    length_ratio: float
    glossary_applied: bool
    run_id: str


def export_to_csv(path: str, records: List[ExportRecord]) -> None:
    fieldnames = [
        "segment_id",
        "source_locale",
        "target_locale",
        "source_text",
        "target_text",
        "content_type",
        "qa_status",
        "qa_issues",
        "length_ratio",
        "glossary_applied",
        "run_id",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "segment_id": rec.segment_id,
                    "source_locale": rec.source_locale,
                    "target_locale": rec.target_locale,
                    "source_text": rec.source_text,
                    "target_text": rec.target_text,
                    "content_type": rec.content_type,
                    "qa_status": rec.qa_status,
                    "qa_issues": ";".join(rec.qa_issues),
                    # Represent length_ratio in a numeric-friendly format
                    # (string here because CSV has no native numeric type).
                    "length_ratio": f"{rec.length_ratio:.4f}",
                    # Use 1/0 so downstream readers can trivially map to bool.
                    "glossary_applied": 1 if rec.glossary_applied else 0,
                    "run_id": rec.run_id,
                }
            )
