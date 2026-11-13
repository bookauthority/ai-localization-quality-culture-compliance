# Chapter 14 Experiment: Scaling, Observability, and Continuous Improvement

This is a self-contained Python 3.11+ experiment project implementing a **simulated AI localization pipeline** with:

- Baseline vs treatment workflow variants
- Structured, stage-level instrumentation
- Simple monitoring and guardrail checks
- A tiny experimentation framework (randomized variant assignment, per-workload)
- Evidence emission in a strict JSON schema for downstream analysis

The implementation is deliberately **offline-only** and uses the **Python standard library only**. No network calls, external MT/LLM APIs, or external metrics backends are used. Instead, we simulate latency, quality, and cost while preserving relative behavior and fair comparisons between baseline and treatment.

The project is tailored to the specification:

- **Chapter**: 14 – Scaling, Observability, and Continuous Improvement
- **Experiment ID**: `exp-ch14-scaling-observability-continuous-improvement-v1`
- **Workloads**:
  - `workload-pharma-high-risk-labeling`
  - `workload-finance-medium-risk-disclosures-marketing`
  - `workload-saas-low-risk-ui-support`

The focus is on **instrumentation**, **observability**, and **experiment mechanics**, not on real translation quality.

## Project Structure

- `run.py` – Main entrypoint. Runs a small suite of baseline and treatment jobs per workload and writes `results.json` to the directory indicated by `BOOKMAS_EVIDENCE_DIR` (default: `/evidence`).
- `experiment/__init__.py` – Package marker.
- `experiment/config.py` – Static configuration for workloads, variants, and experiment metadata.
- `experiment/instrumentation.py` – Structured logging and metric collection primitives.
- `experiment/pipeline.py` – Simulated localization pipeline with stages and per-stage metrics.
- `experiment/experiment_runner.py` – Simple experimentation and randomization logic plus aggregation of results.
- `tests/test_experiment.py` – Unittest suite verifying schema correctness, behavioral expectations, and contract enforcement.
- `requirements.txt` – Empty runtime dependency list (stdlib only).

## Running the Experiment

1. **Environment setup**

   Ensure Python 3.11+ is available. Create a virtual environment if desired, but no additional packages are needed.

   ```bash
   python -m venv .venv
   . .venv/bin/activate  # on Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run tests**

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

   This validates, among other things:

   - The evidence file is created at the path specified by `BOOKMAS_EVIDENCE_DIR` when `run.py` is executed.
   - The evidence conforms to the required schema (chapter, experiment_id, environment, runs, metrics, etc.).
   - At least one baseline and one treatment run per workload exist.
   - All metric values are numbers and contain only numeric telemetry (no text or nested structures inside `metrics`).
   - Only `baseline` and `treatment` are accepted as variant labels.
   - Evidence output is deterministic across runs given the same environment, by relying on a seeded pseudorandom generator instead of wall-clock timings.

3. **Run the experiment**

   ```bash
   # Optional: override evidence directory
   export BOOKMAS_EVIDENCE_DIR=/evidence

   python run.py
   ```

   This will:

   - Generate a sequence of simulated localization jobs for each workload.
   - Randomly but deterministically assign each job to baseline or treatment variant using a fixed random seed.
   - Execute a simplified pipeline for each job, instrumenting per-stage execution times and a synthetic quality score.
   - Aggregate per-run metrics (e.g., `end_to_end_latency_ms`, `automated_quality_score`, `cost_cents`, `success_indicator`) into the evidence object.
   - Write the evidence JSON to `<BOOKMAS_EVIDENCE_DIR>/results.json`.

   The evidence directory is created if missing.

## What Is Measured

Within the sandbox constraints, we measure only what we can compute deterministically from our simulated pipeline:

For each run (job):

- `end_to_end_latency_ms` – Simulated total pipeline latency in milliseconds.
- `automated_quality_score` – Simulated continuous quality score in `[0, 1]`.
- `cost_cents` – Simulated cost per job in cents.
- A set of per-stage latency metrics (e.g., `stage_ingestion_latency_ms`, `simulated_ingestion_latency_ms`, etc.).
- `success_indicator` – `1.0` if the run meets a workload-specific synthetic quality threshold, else `0.0`.

These are **numeric** and vary between baseline and treatment in controlled ways to allow analysis of trade-offs.

We explicitly **do not** fabricate metrics we cannot measure in this offline sandbox—e.g., real API latency, external business KPIs, or actual compliance violations. Higher-level metrics listed in the full chapter specification (like p95 end-to-end latency by locale, business_kpi_ctr, or compliance_violation_rate) would be derived in a production system from richer raw telemetry and domain data. Here, `results.json` intentionally exposes only directly measured, synthetic per-run metrics suitable for demonstration.

## Design Overview

### Baseline vs Treatment

Both baseline and treatment share the same pipeline topology:

1. `ingestion`
2. `analysis`
3. `localization`
4. `qa`
5. `compliance`
6. `delivery`

Each stage contributes simulated latency and may affect quality or cost. The **treatment** variant adjusts parameters to model different quality/latency/cost trade-offs across workloads.

### Experiment Randomization

The `ExperimentRunner` assigns each synthetic job to either baseline or treatment using a fixed PRNG seed so that:

- Results are reproducible between runs.
- The split is reasonably balanced given the small fixed sample sizes.
- Every workload gets at least one baseline and one treatment run.

Only the two variants `baseline` and `treatment` are permitted; attempts to use any other variant string will raise an error.

### Instrumentation

`instrumentation.py` provides:

- `StructuredLogger` – Writes JSON log lines to stdout with correlation IDs and stage metadata.
- `MetricRecorder` – Tracks per-run metrics as a dictionary of numbers and enforces that values are finite numeric types.

The **evidence JSON is deliberately decoupled from logs**. `run.py` and `ExperimentRunner` build evidence directly from `MetricRecorder` outputs and synthetic configuration data; they **never read or parse log output**. This ensures that nondeterministic log fields (like real-time timestamps) cannot affect `results.json`, preserving strict reproducibility of evidence.

### Evidence Contract

The experiment runner writes `/evidence/results.json` (or `<BOOKMAS_EVIDENCE_DIR>/results.json` if the environment variable is set) with this schema:

```json
{
  "chapter": 14,
  "experiment_id": "exp-ch14-scaling-observability-continuous-improvement-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline" | "treatment",
      "workload_id": "workload-...",
      "run_id": "unique-within-workload-and-variant",
      "success": true | false,
      "metrics": {"measured_metric_name": 1.23, "another_metric": 0}
    }
  ],
  "notes": "optional text"
}
```

Additional top-level fields are allowed but are not currently emitted. **All metric values are finite JSON numbers.** Textual data and explanations live outside `metrics`.

The test suite asserts this contract, including:

- Required top-level keys and their types.
- The allowed values for `variant`.
- That `notes` is a string.
- That `metrics` contains only numeric values.

## Determinism and Reproducibility

The experiment uses a fixed seed for randomization and for all simulated timings and quality values. We avoid wall-clock timing in metric values, relying instead on pseudorandom numbers derived from the seeded generator. Logs include real-time timestamps for demonstration purposes, but these stay in stdout only and **do not influence** the evidence JSON.

`tests/test_experiment.py` includes a reproducibility test that runs `run.py` twice and expects the resulting `results.json` contents to be identical, guaranteeing deterministic evidence under the same environment and code.

## Limitations

- No external services: MT/LLM providers, Prometheus, Datadog, or queues are not used.
- No real data: Content, reference translations, and business KPIs are replaced with synthetic placeholders.
- Only a subset of the full KPI set is directly measured; the framework demonstrates how richer telemetry could be gathered, but this sandbox implementation focuses on a small, well-defined set of per-run metrics to keep the experiment runnable offline and fully deterministic.

Despite these constraints, this project shows how to:

- Attach observability to each pipeline stage.
- Define baseline vs treatment workflows cleanly.
- Run a controlled experiment with randomization and guardrails.
- Emit structured evidence ready for further offline analysis.
