# Chapter 08 – Cultural Adaptation as a First-Class Workflow

This is a **self-contained, offline Python 3.11+ experiment project** for:

- **Chapter**: 8
- **Title**: Cultural Adaptation as a First-Class Workflow
- **Experiment ID**: `exp-ch08-cultural-adaptation-workflow-v1`

The goal is to simulate and compare a **baseline localization pipeline** with a **cultural-adaptation-aware treatment pipeline**, and to emit structured experiment evidence as a JSON file under `/evidence/results.json` following a strict schema.

The project is intentionally minimal and uses only the Python standard library so that it can run in the constrained sandbox described in the prompt.

## Contents

- `run.py` – main entrypoint that executes synthetic workloads through baseline and treatment pipelines, measures simple metrics, and writes `results.json` into `$BOOKMAS_EVIDENCE_DIR`.
- `experiment/` – core experiment logic
  - `__init__.py`
  - `data.py` – synthetic dataset definitions for workloads WL1–WL3.
  - `pipelines.py` – baseline & treatment pipeline implementations (deterministic, offline, rule-based).
  - `metrics.py` – metric calculations shared by both variants.
  - `runner.py` – orchestration logic to run the experiment and build evidence structure.
  - `utils.py` – small helpers (e.g., OS/python detection, random seed control).
- `tests/` – unit tests for experiment behavior and evidence schema
  - `test_experiment.py`
- `requirements.txt` – intentionally empty of third-party dependencies (standard library only).

## Design Overview

This project **simulates** a localization workflow with three workloads, each representing a content type from the specification:

- **WL1_marketing_landing_pages** – medium-form marketing copy.
- **WL2_support_and_help_center_articles** – help center / FAQ style content.
- **WL3_high_sensitivity_pharma_patient_leaflets** – high-sensitivity health-related content.

Because this environment is offline and cannot call external LLMs or collect real user studies, we:

- Use **deterministic synthetic source texts** encoded as small Python data structures.
- Implement **baseline** and **treatment** pipelines as simple, rule-based transformations.
- Implement a **cultural risk model and red-flag detector** using keyword/rule heuristics.
- Measure **simple numeric metrics** that are:
  - deterministic
  - computed from actual pipeline outputs
  - shared across baseline and treatment

These metrics are not the full real-world metrics from the chapter (e.g., real user trust), but they are aligned in spirit and provide a concrete demonstration of **relative improvement** of the treatment pipeline.

### Implemented Metrics

Per run (variant + workload), `run.py` records:

- `avg_cultural_flags` – average number of cultural red flags per item (lower is better).
- `avg_length_ratio` – average ratio `len(target_text) / len(source_text)` (closer to 1 is better; shows translation distortion, very roughly).

These are simple but **actually computed**, satisfying the requirement that no metric is fabricated.

Other metrics from the longer spec (e.g., real expert annotations, time-to-comprehension) cannot be measured in this sandbox and are therefore omitted, as required.

## Evidence File Contract

Running `python run.py` will:

1. Execute baseline and treatment pipelines for each workload (WL1, WL2, WL3).
2. Collect per-workload metrics for both variants.
3. Write `/evidence/results.json` (or `${BOOKMAS_EVIDENCE_DIR}/results.json` if the env var is set) with the following structure:

```jsonc
{
  "chapter": 8,
  "experiment_id": "exp-ch08-cultural-adaptation-workflow-v1",
  "environment": {
    "os": "...",       // from platform.system()
    "python": "..."   // from sys.version
  },
  "runs": [
    {
      "variant": "baseline",         // or "treatment"
      "workload_id": "WL1_marketing_landing_pages",
      "run_id": "baseline-WL1-1",   // unique per workload+variant
      "success": true,
      "metrics": {
        "avg_cultural_flags": 0.5,
        "avg_length_ratio": 1.07
      }
    }
    // ... at least one baseline and one treatment run per workload
  ],
  "notes": "... optional free text ..."
}
```

All numeric values inside `metrics` are **JSON numbers** (no strings or nulls).

## Baseline vs Treatment Logic (Simplified)

- **Baseline pipeline**
  - Performs a mock "translation" by doing light substitutions: target text is mostly the source with some locale markers.
  - Runs a **generic QA check**: validates placeholder preservation (`{{placeholder}}`) and counts basic "toxic" tokens.
  - No explicit cultural risk modeling, no nuanced adaptation.

- **Treatment pipeline**
  - Adds a simple **cultural risk scoring function** based on market, channel, and topic.
  - Applies a **rule-based cultural red-flag detector** to source and target.
  - Performs **cultural adaptations**:
    - Rewrites idioms / metaphors into more neutral variants.
    - Softens tone or adjusts formality for specific markets.
    - Localizes certain references (e.g., `football` to `soccer`, `Thanksgiving` to "local holiday").
  - Uses risk score and flags to decide if a **cultural review** would be needed (simulated as routing decisions tracked in metadata).

Because everything is deterministic and rule-based, this is reproducible and safe to run in a tiny offline container.

## How to Run

From the repository root (where this README resides):

1. **Run the experiment**

   ```bash
   python run.py
   ```

   This will create the evidence file:

   - If `$BOOKMAS_EVIDENCE_DIR` is set: `"$BOOKMAS_EVIDENCE_DIR"/results.json`
   - Otherwise: `/evidence/results.json`

   (The directory is created if it does not exist.)

2. **Run tests**

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

   Tests verify:
   - Evidence file exists and is valid JSON.
   - Schema contracts for `chapter`, `experiment_id`, `environment`, and `runs`.
   - There is at least one baseline and one treatment run per workload.
   - Each metrics dict contains numeric values only.

## Limitations

- No external MT/LLM providers, embeddings, or language detection libraries are used; all behavior is simulated via simple heuristics.
- The rich evaluation design from the full specification (expert cultural annotations, user studies, complex metrics) is not executable in this sandbox and is therefore not implemented.
- The focus of this project is **reproducibility and schema correctness**, not linguistic quality.

## Extensibility Notes

In a real setting, you could replace the internals of `pipelines.py` while keeping the same `runner.py` interface to:

- Plug in actual LLM-based translation and classification.
- Log cultural annotations that conform to the `evidence_schema` in the specification.
- Extend `metrics.py` and `run.py` to compute advanced metrics (e.g., cultural_redflag_precision) as long as they are computed from real data.

For the purposes of this book/sandbox, the current implementation is intentionally simple, deterministic, and dependency-free.
