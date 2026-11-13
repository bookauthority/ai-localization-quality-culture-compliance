import os
import uuid
from typing import Dict

from .config import default_config
from .export import ExportRecord, export_to_csv
from .ingest import ingest_csv
from .language_detection import detect_language
from .logging_utils import log_json
from .metrics import AggregatedMetrics, empty_metrics, to_dict
from .qa import run_qa
from .translation import load_glossary, translate_with_glossary


def run_treatment_pipeline(input_path: str) -> Dict[str, float]:
    """Run the modular treatment pipeline on the given CSV.

    Returns a dict of aggregate numeric metrics suitable for evidence.

    Metrics use per segment-locale semantics: segments_total is the number
    of translation jobs attempted (segments * target_locales), and the
    other counters are over the same universe.
    """

    config = default_config()

    segments = ingest_csv(input_path)
    metrics: AggregatedMetrics = empty_metrics()

    glossary_path = os.path.join("data", "glossary_en_es_fr.csv")
    glossary = load_glossary(glossary_path)

    run_id = str(uuid.uuid4())

    output_records = []

    for segment in segments:
        detected_lang, _confidence = detect_language(segment.source_text)
        source_locale = segment.source_locale or detected_lang

        for target_locale in config.target_locales:
            metrics.segments_total += 1.0
            try:
                translated = translate_with_glossary(segment.source_text, target_locale, glossary)
                metrics.segments_successfully_translated += 1.0
                qa_result = run_qa(segment.source_text, translated, source_locale, target_locale, config)
                if qa_result.status == "pass":
                    metrics.segments_passing_all_qa += 1.0
                else:
                    metrics.segments_failing_any_qa += 1.0

                output_records.append(
                    ExportRecord(
                        segment_id=segment.segment_id,
                        source_locale=source_locale,
                        target_locale=target_locale,
                        source_text=segment.source_text,
                        target_text=translated,
                        content_type=segment.content_type,
                        qa_status=qa_result.status,
                        qa_issues=qa_result.issues,
                        length_ratio=qa_result.length_ratio,
                        glossary_applied=True,
                        run_id=run_id,
                    )
                )

            except Exception:
                metrics.segments_failed_translation += 1.0

    # Export TMS-like CSV (not used by tests but aligns with chapter intent)
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(out_dir, f"{base_name}_treatment_export.csv")
    export_to_csv(output_path, output_records)

    log_json(
        "treatment_pipeline_completed",
        input_path=input_path,
        run_id=run_id,
        metrics=to_dict(metrics),
    )

    return to_dict(metrics)
