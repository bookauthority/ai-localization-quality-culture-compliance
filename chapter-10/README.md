# Chapter 10 Experiment: Routing, Orchestration, and CI/CD for Localization Pipelines

This is a self-contained, offline-friendly Python 3.11+ experiment project for:

- **Chapter**: 10
- **Title**: Routing, Orchestration, and CI/CD for Localization Pipelines
- **Experiment ID**: `exp-ch10-routing-orchestration-cicd-001`

It simulates baseline vs. treatment localization pipelines and records measured metrics
(latencies and throughput) in an evidence file suitable for automated validation.

## Design Overview

The goal is to approximate the real-world comparison described in the specification
while remaining safe and fully deterministic in an offline sandbox.

We simulate three workloads:

1. **WL1-high-risk-product-docs**  (high risk, regulated docs)
2. **WL2-low-risk-marketing-and-ui** (low/medium risk, marketing + UI)
3. **WL3-peak-load-stress-test** (synthetic peak stress load)

For each workload we execute two variants:

- **Baseline**: monolithic, synchronous, hard-coded routing
- **Treatment**: configuration-driven routing + queue-based orchestrator with
  more realistic features (canary flags, prioritization, etc.), simulated
  but implemented concretely in code.

### What Is Actually Measured

Because the environment is offline and uses only the Python standard library,
we cannot call real MT/LLM APIs, CI/CD services, queues, or workflow engines.
Instead, we simulate processing using the `time.perf_counter()` clock and
programmed delays:

- We run each workload for each variant.
- Every "segment" is represented by a small Python dict.
- Segments are processed in worker threads that apply routing rules and a
  synthetic per-stage processing time.
- We record wall-clock times for each segment and compute:
  - `end_to_end_latency_p50` (median seconds per segment)
  - `end_to_end_latency_p95` (95th percentile seconds per segment)
  - `throughput` (segments per second over the workload run)

These numeric measurements are derived from actual instrumented execution.
We do **not** fabricate metrics such as cost, error_rate, incidents, etc.
Omitted metrics are explained in `notes` in the evidence file.

The simulation is lightweight and bounded (small volumes, short sleeps) to
remain fast and safe.

### Baseline vs. Treatment Logic

Both variants share:

- The same synthesized segment data per workload.
- The same random seed (42) to generate deterministic content features.

**Baseline characteristics**:

- Synchronous sequential processing (single-threaded) of all segments.
- "Routing" decided via hard-coded if/else statements embedded in the worker.
- Simple fixed per-segment processing time profile.
- No queues, no canary flags, no explicit priorities.

**Treatment characteristics**:

- Configuration-driven router (rules defined in Python data, but easily
  externalizable).
- Work queue + multi-threaded workers to emulate an orchestrator.
- Per-segment workflow path chosen by rules based on language, risk level,
  content type, and channel.
- Simulated features:
  - A simple feature-flag configuration.
  - Canary routing for a portion of segments in WL2.
  - Priority handling (WL1 segments receive less contention in the queue).

The treatment is designed to **potentially** improve throughput and tail
latency in this synthetic environment by exploiting parallelism and more
balanced routing, but we do not assume or enforce a particular outcome.

### Evidence File Contract

`run.py` writes a JSON evidence file to the directory specified by the
`BOOKMAS_EVIDENCE_DIR` environment variable (default: `/evidence`).

The file path is:

```text
/evidence/results.json
```

with this exact top-level structure:

```json
{
  "chapter": 10,
  "experiment_id": "exp-ch10-routing-orchestration-cicd-001",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline" | "treatment",
      "workload_id": "WL1-high-risk-product-docs" | ...,
      "run_id": "...",
      "success": true | false,
      "metrics": {
        "end_to_end_latency_p50": 0.123,
        "end_to_end_latency_p95": 0.456,
        "throughput": 78.9
      }
    },
    ...
  ],
  "notes": "..."
}
```

Requirements:

- At least one **baseline** and one **treatment** run are produced for each
  workload (WL1, WL2, WL3).
- Metric values **must** be finite JSON numbers.
- No non-numeric values are stored inside `metrics`.
- Extra explanatory fields (stdout, comments, etc.) are stored outside the
  `metrics` objects.

### How to Run

From the project root:

1. **Run the experiment and generate evidence**

   ```bash
   export BOOKMAS_EVIDENCE_DIR=/evidence  # optional; default is /evidence
   python run.py
   ```

   This will:

   - Synthesize workloads for WL1, WL2, WL3.
   - Execute baseline and treatment variants.
   - Compute metrics and write `/evidence/results.json`.

2. **Run tests**

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

   The tests verify:

   - Evidence file exists and is valid JSON.
   - Evidence schema matches the required contract.
   - Numeric metrics are present and finite.
   - At least one baseline and one treatment run per workload.

### Project Layout

- `run.py` – Main entrypoint that runs the experiment and writes the evidence.
- `experiment/core.py` – Simulation primitives for segments, routing, and
  orchestrators.
- `experiment/workloads.py` – Workload definitions and data synthesis.
- `experiment/runner.py` – Logic to execute baseline and treatment runs and
  aggregate metrics.
- `tests/test_experiment.py` – Schema and behavior tests for the evidence
  file and experiment code.
- `requirements.txt` – Empty of runtime dependencies; only the Python standard
  library is used.

### Limitations

- No real network calls, CI/CD, or external queues are used; everything is
  simulated in-process.
- Many metrics from the specification (e.g., cost_per_segment, error_rate,
  incidents, rollbacks) are **not measured** and therefore intentionally
  omitted from the `metrics` objects.
- Routing and orchestration rules are simplified but structured to illustrate
  configuration-driven behavior vs. hard-coded routing.

This setup is intended to demonstrate reproducible experimentation patterns
rather than provide production-ready infrastructure code.
