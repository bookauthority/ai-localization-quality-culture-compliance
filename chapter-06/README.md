# Chapter 6 Experiment: Operationalizing Quality – Metrics, Evaluation, and Feedback Loops

This is a self-contained Python 3.11+ experiment project that simulates a localization quality pipeline with **baseline** and **treatment** variants.

The goal is to demonstrate how to:

- Define and compute basic quality metrics
- Compare a minimal baseline QA pipeline against an enhanced, quality-aware pipeline
- Produce structured evidence in a standard JSON schema for governance and dashboards

The implementation here is **offline and deterministic**:

- No external APIs, MT engines, or QE services are called
- All translation and quality behavior is simulated using simple heuristic models
- Randomness is fully controlled via a fixed seed

Despite the simplifications, the project mirrors the structure of a real experiment:

- Multiple workloads with different risk/content profiles
- Baseline vs. treatment variants
- Instrumentation for latency-like and quality-like metrics
- Evidence serialization to `/evidence/results.json` with a well-defined schema

## Project Layout

- `run.py` – Entry point to run the experiment and write evidence
- `experiment/__init__.py` – Package marker
- `experiment/randomization.py` – Centralized, seed-based random utilities
- `experiment/simulation.py` – Workload definitions and simulated translation/QA logic
- `experiment/metrics.py` – Metric computation & aggregation utilities
- `tests/test_experiment.py` – Unit tests verifying the evidence schema and behavior
- `requirements.txt` – Empty runtime dependency list (standard library only)

## Running the Experiment

From the project root:

```bash
python run.py
```

This will:

1. Determine the evidence directory from the `BOOKMAS_EVIDENCE_DIR` environment variable (default: `/evidence`).
2. Simulate processing three workloads for both baseline and treatment variants.
3. Collect numeric metrics per run (e.g., average quality score, functional error rate, pseudo-latency).
4. Write `results.json` in the evidence directory with the following structure:

```json
{
  "chapter": 6,
  "experiment_id": "ch06-operationalizing-quality-metrics-eval-feedback-v1",
  "environment": {
    "os": "...",
    "python": "..."
  },
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "w1-ui_product_strings",
      "run_id": "...",
      "success": true,
      "metrics": {
        "avg_quality_score": 0.0,
        "functional_error_rate": 0.0,
        "avg_latency_ms": 0.0
      }
    },
    {
      "variant": "treatment",
      "workload_id": "w1-ui_product_strings",
      "run_id": "...",
      "success": true,
      "metrics": {
        "avg_quality_score": 0.0,
        "functional_error_rate": 0.0,
        "avg_latency_ms": 0.0
      }
    }
    // ... at least one baseline and one treatment run per workload
  ],
  "notes": "... optional free-text notes ..."
}
```

All metric values are **numbers** (no strings, booleans, nulls, or complex types).

## Running Tests

From the project root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Tests verify that:

- `run.py` creates a valid `results.json` file in the evidence directory
- The JSON structure and value types conform to the required schema
- There is at least one baseline and one treatment run per workload
- Each run has at least one numeric metric value

## Design & Simplifications

### Simulated Translation and Quality

The book specification references MT engines, prompts, human review, and quality estimation. In this offline sandbox, those are simulated as follows:

- **Segments**: Synthetic segments are generated per workload with different lengths and risk profiles.
- **Baseline variant**:
  - Minimal QA (length and placeholder checks only)
  - Lower simulated quality scores and higher functional error rates
- **Treatment variant**:
  - Additional simulated linguistic and functional checks
  - Structured "human-like" feedback baked into the simulation
  - Better average quality score and lower functional error rate

The simulation is deterministic given the global seed (`42`) and does not rely on the system clock for any measurements (pseudo-latency is computed mathematically, not timed).

### Metrics in this Implementation

The full book specification includes many metrics; in this constrained sandbox we provide a **safe subset** that we can honestly measure:

- `avg_quality_score` – Synthetic numeric quality score in [0, 100], averaged over all simulated segments for a run.
- `functional_error_rate` – Proportion of segments with at least one functional issue.
- `avg_latency_ms` – Pseudo-latency per segment in milliseconds; a deterministic function of content length and variant complexity.

All are derived from actual simulation outcomes (no fabricated constants).

Because we are fully offline and not calling real services or involving human annotators, metrics such as true human_overall_quality_score, real QE scores, costs, or BLEU/ChrF are **not** reported in `results.json`.

## Reproducibility

- Random seed is fixed at `42` in `experiment/randomization.py`.
- No external network, subprocesses, or system-dependent behavior are used.
- The only writable external path is the evidence directory (`/evidence` by default).

## Extending This Project

This skeleton is designed to be easy to extend:

- Add richer segment simulation (e.g., error categories, severity) in `experiment/simulation.py`.
- Add additional metrics (e.g., per-workload aggregates) in `experiment/metrics.py`.
- Integrate with real MT/QE APIs (outside of this sandbox) by swapping the simulators with concrete implementations and reusing the evidence-writing contract from `run.py`.
