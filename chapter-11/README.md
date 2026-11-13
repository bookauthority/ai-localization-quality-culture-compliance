# Chapter 11 Experiment: Data, Memory, and Terminology

This project implements a **self-contained, offline, deterministic simulation** of an AI-driven localization pipeline to compare:

- **Baseline:** MT/LLM-style translation *without* explicit use of translation memories (TM), termbases, or vector-retrieved examples.
- **Treatment:** The same pipeline but with **TM lookup**, **glossary enforcement**, and **vector-based example retrieval** integrated.

The implementation is simplified and self-contained (no external models, APIs, or extra libraries) but mirrors the structure and logic of a realistic system:

- TM lookups with fuzzy matching.
- Glossary/termbase enforcement and violation checks.
- Vector-style retrieval via deterministic embeddings and nearest-neighbor search.
- Shared workloads and deterministic pseudo-translations.
- Instrumented metrics and evidence output following the required schema.

All logic uses only the Python standard library and runs entirely offline.

## Project Layout

- `run.py` – Entry point that runs the experiment (baseline + treatment) and writes evidence JSON.
- `experiment/__init__.py` – Package marker.
- `experiment/config.py` – Static configuration and workload definitions.
- `experiment/assets.py` – In-memory TM, termbase, and style example datasets.
- `experiment/vectorstore.py` – Deterministic embedding and vector search implementation.
- `experiment/tm.py` – TM lookup with fuzzy matching.
- `experiment/terminology.py` – Glossary enforcement, terminology checks, and simple ROI helpers.
- `experiment/pipeline.py` – Baseline and treatment pipeline implementations.
- `experiment/metrics.py` – Metric computations and simple statistical helpers.
- `experiment/utils.py` – Shared helper functions (hashing, simple tokenization, etc.).
- `tests/test_experiment.py` – Unit tests validating evidence schema and basic behavior.

## Running the Experiment

Ensure you are in the project root (where `run.py` is located).

### 1. Run the main experiment

```bash
python run.py
```

This will:

1. Run the **baseline** pipeline for all three workloads.
2. Run the **treatment** pipeline for all three workloads.
3. Compute simple, reproducible metrics per workload and condition.
4. Write evidence as JSON to the directory specified by the
   `BOOKMAS_EVIDENCE_DIR` environment variable (default: `/evidence`):

- `/evidence/results.json`

The evidence file follows the exact schema required by the specification, e.g.:

```json
{
  "chapter": 11,
  "experiment_id": "exp-ch11-linguistic-assets-tm-terms-vs-none-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "workload-marketing-high-style",
      "run_id": "baseline_workload-marketing-high-style_v1",
      "success": true,
      "metrics": {
        "avg_length_ratio": 1.02,
        "terminology_accuracy": 65.0
      }
    },
    {
      "variant": "treatment",
      "workload_id": "workload-marketing-high-style",
      "run_id": "treatment_workload-marketing-high-style_v1",
      "success": true,
      "metrics": {
        "avg_length_ratio": 1.00,
        "terminology_accuracy": 86.0,
        "asset_hit_rate_tm": 40.0,
        "asset_hit_rate_termbase": 100.0,
        "asset_hit_rate_vector": 100.0
      }
    }
  ],
  "notes": "..."
}
```

Every metric value is computed from the actual (simulated) pipeline behavior; nothing is fabricated.

### 2. Running the Tests

Use Python's built-in unittest discovery:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests verify that:

- `run.py` produces an evidence file at the expected location.
- The evidence JSON conforms to the required schema (types, field names).
- At least one baseline and one treatment run are present for each workload.
- Metric values are numeric.

## What the Simulation Does

This project cannot use real MT engines, COMET, BLEU, or external dependencies in the restricted environment. Instead, it uses deterministic, stylized logic to approximate the **relative** effects of linguistic assets:

- **Pseudo-translation:**
  - Baseline: simple, deterministic character-level transformation of the source (e.g., reversing text, basic substitutions) with no knowledge of TM or terminology.
  - Treatment: prefers TM matches when available; otherwise generates pseudo-translations that attempt to apply glossary terms and style examples.

- **TM Lookup:**
  - A small in-memory TM is defined in `experiment/assets.py`.
  - Fuzzy matching is done using a normalized Levenshtein distance.
  - The treatment pipeline records whether a TM hit was found above the configured thresholds.

- **Terminology / Termbase:**
  - A small termbase with required and forbidden terms is defined.
  - Treatment injection ensures that required target terms are included; basic checks count correct vs. required occurrences.
  - Terminology accuracy is computed as the proportion of required occurrences that are correctly realized.

- **Vector Search:**
  - Embeddings are toy vectors derived deterministically from text (e.g., character-code features) to simulate an embedding model.
  - A tiny in-memory vector index is built and queried to fetch nearest style examples.
  - Treatment logs whether a sufficiently similar example was found.

## Metrics Implemented

Because we are offline and restricted to the standard library, we do **not** compute BLEU, COMET, or human-rating metrics.

Instead, we compute a subset of metrics that can be simulated deterministically and meaningfully compare baseline vs. treatment:

- `avg_length_ratio` – Average ratio `len(translation)/len(source)` per workload and condition.
- `terminology_accuracy` – Percentage of required glossary terms correctly realized in outputs.
- `terminology_violation_rate` – Percentage of segments with any terminology violation.
- `asset_hit_rate_tm` – Percentage of segments with TM hit above threshold (treatment only).
- `asset_hit_rate_termbase` – Percentage of segments that contain at least one termbase term (treatment only).
- `asset_hit_rate_vector` – Percentage of segments with at least one vector example above similarity threshold (treatment only).

These are all numeric, computed from actual runs, and sufficient to demonstrate the experimental design and asset impact qualitatively.

Metrics that cannot be computed realistically here (BLEU, COMET, human scores, post-editing effort, ROI in currency) are **omitted** from `metrics` and discussed in comments.

## Extending to Real Systems

To turn this into a real experiment with external models and full metrics, you would:

1. **Plug in real MT/LLM** calls where pseudo-translation is done.
2. **Replace embeddings** with calls to a real sentence embedding model and a vector index (e.g., FAISS).
3. **Connect to your actual TM/TBX** files and style examples.
4. **Add BLEU/COMET** computations using appropriate libraries.
5. **Wire human evaluation tooling** to collect real human scores and post-edit logs.

The structure of baseline vs. treatment, metric collection, and evidence generation in this repo is designed to be easily swappable with real components.

## Reproducibility Notes

- All randomness (e.g., simple noise in pseudo-translations) is controlled via fixed seeds per run.
- The same workloads, seeds, and asset sets are used for both baseline and treatment.
- Evidence filenames and run IDs are deterministic given the workload and variant.

## License

This code is provided as a reference implementation for reproducible experimentation in AI localization contexts.
