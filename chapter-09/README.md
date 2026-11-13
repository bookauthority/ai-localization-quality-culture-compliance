# Chapter 9 Experiment: Embedding Regulatory and Legal Compliance into Pipelines

Experiment ID: `exp-ch09-compliance-pipeline-prepost-v1`

This self-contained Python 3.11+ project simulates a baseline vs. treatment
localization workflow for regulated content (pharma, finance, PII-heavy
support tickets, and low-risk marketing). The treatment pipeline adds
rule-based "compliance" checks and redaction logic around a stubbed
localization step. The goal is to demonstrate how pre- and post-localization
checks can be embedded and how to collect reproducible, audit-ready
experimental evidence.

Because this environment is offline and restricted, the implementation uses
pure-Python deterministic logic and small synthetic workloads instead of real
NLP/ML models or external MT services. However, the structure mirrors a real
system: separate baseline and treatment variants, document-level runs
across workloads, timing measurements, and a structured evidence artifact.

## Contents

- `run.py` – Main entrypoint. Runs the experiment and writes
  `/evidence/results.json` (path configurable via `BOOKMAS_EVIDENCE_DIR`).
- `experiment/__init__.py` – Package marker.
- `experiment/config.py` – Static experiment configuration, synthetic
  workloads, and pipeline parameters.
- `experiment/pipeline.py` – Baseline and treatment pipeline implementations,
  including deterministic pseudo-localization and compliance checks.
- `experiment/metrics.py` – Instrumentation utilities to capture timings and
  construct run records.
- `tests/test_experiment.py` – Unit tests validating evidence schema and
  basic behavioral properties using `unittest`.
- `requirements.txt` – Empty of external runtime dependencies; uses only
  the Python standard library.

## Running the Experiment

From the project root:

```bash
python run.py
``

This will:

1. Load the synthetic workloads defined in `experiment/config.py`.
2. For each workload (`w1-pharma-ifus`, `w2-financial-disclosures`,
   `w3-support-tickets-pii`, `w4-lowrisk-marketing`), execute both:
   - A **baseline** pipeline with minimal checks.
   - A **treatment** pipeline with additional redaction and rule checks.
3. Record at least one numeric metric per run; in this implementation:
   - `tokens` – approximate token count of processed text (very simple
     whitespace-based heuristic).
   - `processing_time_ms` – measured processing time in milliseconds
     (using `time.perf_counter`).
4. Persist the evidence file with the required schema:

```json
{
  "chapter": 9,
  "experiment_id": "exp-ch09-compliance-pipeline-prepost-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline" or "treatment",
      "workload_id": "w1-pharma-ifus" | ...,
      "run_id": "string",
      "success": true,
      "metrics": {
        "tokens": 123.0,
        "processing_time_ms": 0.42
      }
    }
  ],
  "notes": "..."
}
```

The output path is determined by the `BOOKMAS_EVIDENCE_DIR` environment
variable. If unset, the script writes to `/evidence/results.json`.

> Note: The evaluator may mount `/evidence` as a writable directory at
> runtime. The project never writes outside `/tmp`, `/tmp/work`, and
> `/evidence`.

## Running Tests

Use the Python standard library `unittest` runner:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests assert that:

- `run.py` can be imported and executed without raising.
- The evidence file exists after a run.
- The evidence JSON conforms to the required schema:
  - `chapter` integer.
  - Correct `experiment_id`.
  - `environment` with `os` and `python` strings.
  - `runs` is a non-empty list of run objects.
  - At least one baseline and one treatment run per workload ID.
  - Each `metrics` mapping contains only finite numeric values.

## Design Notes

### Baseline vs. Treatment Pipelines

- **Baseline** simulates:
  - Simple ingestion of source text.
  - A naive "localization" step that transforms text in a reversible,
    deterministic way (e.g., uppercasing and appending a language code).
  - Very limited compliance logic (a length check and a placeholder for
    manual-only legal review).

- **Treatment** adds:
  - A pre-localization PII redaction pass: simple pattern-based masking of
    email-like and digit-heavy tokens.
  - A pre- and post-localization compliance pass:
    - Flags forbidden phrases (e.g., "guaranteed return").
    - Ensures required disclaimers appear in the text.
  - Additional bookkeeping that *would* map naturally to real regulators,
    but implemented here with trivial rules.

Both variants share the same synthetic data and approximate token counting,
ensuring a fair comparison and deterministic results.

### Metrics and Limitations

Because the environment disallows external services and large dependencies,
this project cannot measure realistic latency, detection rates, or human
review times. The only quantitative metrics recorded are:

- `tokens` – proxy for workload size.
- `processing_time_ms` – approximated over the pure-Python simulation.

Other metrics from the full chapter specification (e.g., false positive
rates, PII leakage rates against human labels) must be omitted here to
respect the instruction that all metrics come from actual instrumented
execution.

Comments in the code indicate where and how to extend the prototype to a
more realistic stack (e.g., spaCy, transformers, external MT) in a
non-restricted environment.

## Reproducibility

- No external network access is required.
- No non-standard libraries are used.
- All random decisions (where present) are seeded via `random.seed(90909)`.
- The synthetic workloads are hard-coded and stable.

This ensures that repeated runs under the same Python version and OS should
produce identical `tokens` and very similar `processing_time_ms` values
(minor fluctuations possible due to scheduler timing).
