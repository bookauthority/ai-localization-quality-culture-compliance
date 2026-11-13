# Chapter 5 – Baseline AI Localization Pipeline (Offline Experiment)

This project implements a **self-contained, offline** experiment approximating:

> *"A Baseline AI Localization Pipeline in Code" – minimal but realistic, with baseline vs. improved treatment pipelines, deterministic behavior, and evidence output suitable for later governance layers.*

Because the sandbox is offline and cannot call real MT/LLM APIs, the project uses **deterministic, rule-based pseudo-translation** to simulate translation behavior. Both the **baseline** and **treatment** pipelines share the same core pseudo-translator so that structural and QA improvements, not MT quality, differentiate them.

The experiment writes evidence to `/evidence/results.json` following a strict schema consumed by external validators.

## Layout

- `run.py` – orchestrates the experiment runs (baseline and treatment, two workloads) and writes `/evidence/results.json`.
- `baseline_pipeline.py` – naive baseline script-like pipeline implementation.
- `treatment_pipeline/` – modular, production-shaped treatment pipeline:
  - `config.py` – simple configuration model.
  - `ingest.py` – CSV ingestion and parsing.
  - `language_detection.py` – deterministic language detection.
  - `translation.py` – pseudo-translation with glossary hints.
  - `qa.py` – length ratio, placeholder, and tag integrity QA checks.
  - `export.py` – TMS-like CSV export.
  - `logging_utils.py` – simple structured logging helpers.
  - `metrics.py` – metric collection helpers.
- `data/` – small, deterministic CSV datasets and a glossary:
  - `sample_customer_support_en.csv`
  - `sample_marketing_snippets_en.csv`
  - `glossary_en_es_fr.csv`
- `tests/` – unit tests and schema checks for the experiment output.
- `requirements.txt` – intentionally contains **no runtime dependencies**; the code uses only the Python standard library.

## Running the Experiment

From the project root:

```bash
python run.py
```

This will:

1. Run the **baseline** pipeline on both workloads.
2. Run the **treatment** pipeline on both workloads.
3. Capture simple, numeric metrics for each run:
   - `segments_total`
   - `segments_successfully_translated`
   - `segments_failed_translation`
   - `segments_passing_all_qa`
   - `segments_failing_any_qa`

The results are written to `/evidence/results.json` with the schema:

```jsonc
{
  "chapter": 5,
  "experiment_id": "exp-ch05-baseline-ai-localization-pipeline-v1",
  "environment": {"os": "…", "python": "…"},
  "runs": [
    {
      "variant": "baseline" | "treatment",
      "workload_id": "sample_customer_support_tickets" | "sample_marketing_snippets",
      "run_id": "<unique string>",
      "success": true | false,
      "metrics": {
        "segments_total": <number>,
        "segments_successfully_translated": <number>,
        "segments_failed_translation": <number>,
        "segments_passing_all_qa": <number>,
        "segments_failing_any_qa": <number>
      }
    }
  ],
  "notes": "… additional non-metric context …"
}
```

**Important:** The snippet above is **illustrative only**. All numeric metric values must come directly from instrumented execution of `run.py` in this sandbox. Contributors **must not** copy or handcraft `/evidence/results.json`; instead, always run the experiment to regenerate it.

All metric values are **numbers**, never strings or other types.

### Metric semantics (normalized across baseline and treatment)

To keep baseline/treatment comparisons interpretable, this offline experiment adopts **per segment–locale pair** semantics for all core counters:

- `segments_total` – number of translation jobs executed: `num_source_segments * num_target_locales`.
- `segments_successfully_translated` – count of segment–locale pairs for which a target text was produced.
- `segments_failed_translation` – count of segment–locale pairs where translation failed due to an internal error.
- `segments_passing_all_qa` – count of segment–locale pairs that pass all QA checks.
  - **Baseline note:** the baseline implementation performs **no actual QA checks**. For comparison purposes only, it reports `segments_passing_all_qa == segments_successfully_translated` and `segments_failing_any_qa == 0`, reflecting that every successful translation is *treated as if* it passed QA even though no QA logic was executed.
- `segments_failing_any_qa` – count of segment–locale pairs that fail at least one QA check.

The baseline computes metrics with the same per segment–locale semantics as the treatment to allow direct comparison, while still remaining QA-unaware internally.

## Runtime Evidence vs. Full Spec

The chapter-level experiment specification describes a **richer metrics and evidence schema** (including `qa_failure_rate`, timing metrics, `run_record`/`segment_record` objects, and per-locale breakdowns). In this offline sandbox implementation:

- `/evidence/results.json` emits **only** the aggregate count metrics listed above per run.
- Metrics such as `qa_failure_rate`, `placeholder_integrity_violation_rate`, `tag_integrity_violation_rate`, `length_ratio_out_of_bounds_rate`, `pipeline_end_to_end_time`, `avg_translation_latency_per_segment`, and `hard_failure_indicator` are **not currently measured or emitted**.
- Detailed `run_record` and `segment_record` objects from the descriptive spec are **not written**; instead, the treatment pipeline exports a simpler TMS-like CSV per input file under `outputs/`.

These richer structures and metrics should be treated as **descriptive, forward-looking design targets**, not as part of the enforced runtime contract for this offline project. Validators and governance tooling consuming this repository must:

- Treat missing spec-level metrics as **absent**, not as zero.
- Avoid inferring or reconstructing `run_record` / `segment_record` objects from `/evidence/results.json` alone.

Any future extension of metrics must ensure that values are **directly measured during execution**, not inferred or fabricated.

## Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The test suite verifies:

- The experiment result file exists and satisfies the required schema.
- At least one baseline and one treatment run exist per workload.
- All metrics values are finite numbers.

## Design Notes

- **Offline translation**: A reproducible, deterministic pseudo-translation transforms English strings into a reversible variant in the target language codes (e.g., `es-ES`, `fr-FR`), preserving placeholders and tags as much as possible.
- **Baseline vs. treatment**:
  - Baseline: Single-function, script-style processing with minimal structure; only basic counting and **no explicit QA or glossary use**. QA-related metrics in baseline are conceptual mirrors of the treatment’s counters and do **not** imply real QA checks.
  - Treatment: Modular pipeline with explicit stages (ingest → detect_language → translate → qa → export) and QA checks:
    - Length ratio bounds.
    - Placeholder integrity (missing, extra).
    - Simple HTML tag balance.
- **Safety and determinism**:
  - No network or subprocess usage.
  - Standard library only.
  - Small fixed datasets in `data/` for bounded runtime.

This offline implementation focuses on structure, observability, and QA behavior rather than real MT/LLM quality, while still mirroring the experiment specification at a reduced, sandbox-friendly scale.
