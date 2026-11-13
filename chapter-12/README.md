# Chapter 12 – Evaluating Vendors and Building a Hybrid Sourcing Model

This is a self-contained, offline Python 3.11+ experiment project simulating a
multi-vendor localization bake-off and hybrid sourcing model.

It is intentionally constrained to the Python standard library so it can run in
restricted environments without external dependencies or network access.

The real book chapter would integrate with actual MT/LLM/TMS/LSP vendor APIs
and external metrics (BLEU, COMET, etc.). Here, we provide a *structural* and
*reproducible* experiment harness that:

- Models three workloads:
  - `pharma_patient_info_high_risk`
  - `finance_marketing_and_disclosures_medium_risk`
  - `b2b_saas_ui_and_help_low_to_medium_risk`
- Simulates a **baseline single-vendor** model and a **treatment hybrid
  multi-vendor** routing model.
- Instruments and records **real numeric metrics** derived from actual code
  execution (segment counts, simulated latencies, synthetic quality scores),
  without fabricating values.
- Produces an evidence file at `/evidence/results.json` that follows the
  required contract.

Because the sandbox is offline and we must not call external services, this
experiment uses **deterministic synthetic data and scoring**. This allows us to
focus on the *architecture* and *reproducibility* of vendor evaluation and
hybrid sourcing decisions.

## Project layout

- `run.py` – Main entry point. Runs the baseline and treatment experiments and
  writes `/evidence/results.json`.
- `experiment/__init__.py` – Package marker.
- `experiment/config.py` – Static configuration for workloads, vendors, and
  routing policies (baseline vs hybrid).
- `experiment/data_generation.py` – Deterministic synthetic dataset generator
  for the three workloads and language pairs.
- `experiment/vendors.py` – Vendor abstraction and simple simulated vendor
  implementations (baseline + two additional vendors). Includes a hybrid
  routing policy for the treatment configuration.
- `experiment/metrics.py` – Metric instrumentation utilities (segment counts,
  simple pseudo-quality scores, pseudo-latency, throughput).
- `experiment/runner.py` – Core experiment harness that runs baseline and
  treatment variants over all workloads and aggregates metrics.
- `tests/test_experiment.py` – Unit tests verifying evidence schema and basic
  behavior using Python's standard `unittest` framework.
- `requirements.txt` – Empty of runtime dependencies by design (only standard
  library is used).

## How this maps to the chapter’s goals

This code focuses on **structure and method** rather than real translation
quality:

- **Vendor categories & adapters** – `experiment/vendors.py` mimics MT/LLM
  providers as pluggable vendor drivers with a common interface. In real life
  you would also add TMS and LSP gateways here.
- **Evaluation framework** – `experiment/runner.py` coordinates runs, collects
  metrics, and passes them to the evidence writer in `run.py`.
- **Bake-off design** – Baseline runs all content through a single vendor.
  Treatment uses a simple rule-based hybrid router to assign workloads and
  language pairs to different vendors.
- **Hybrid & lock-in considerations** – The use of vendor-neutral data
  structures and pluggable adapters illustrates how to avoid hard-coding
  business logic to any specific vendor.

## Running the experiment

1. Ensure you are using **Python 3.11+**.

2. (Optional) Create a virtual environment (no external dependencies are
   required):

   ```bash
   python -m venv .venv
   . .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. Install dependencies (none beyond the standard library, but this keeps the
   workflow consistent):

   ```bash
   pip install -r requirements.txt
   ```

4. Run the experiment:

   ```bash
   python run.py
   ```

   This will:

   - Generate synthetic source segments for each workload and language pair.
   - Run a **baseline** variant using a single vendor.
   - Run a **treatment** variant using a hybrid routing policy.
   - Compute simple numeric metrics (segment count, pseudo-quality, simulated
     latency, throughput) using only standard library functionality.
   - Write the evidence JSON file to `/evidence/results.json`.

5. Run the unit tests:

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

   The tests verify:

   - `/evidence/results.json` exists after running `run.py`.
   - It has the required top-level keys and schema.
   - All metrics are numeric values and properly associated with baseline and
     treatment runs for all three workloads.

## Evidence file contract

`run.py` *must* write JSON to the path constructed from the
`BOOKMAS_EVIDENCE_DIR` environment variable (defaulting to `/evidence` if not
set):

```jsonc
{
  "chapter": 12,
  "experiment_id": "ch12-vendor-bakeoff-hybrid-sourcing-001",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline",          // or "treatment"
      "workload_id": "pharma_patient_info_high_risk",
      "run_id": "baseline_pharma_1",  // unique per (variant, workload)
      "success": true,
      "metrics": {
        "segments_processed": 600,
        "avg_quality_score": 0.78,
        "latency_ms_avg": 12.3,
        "throughput_segs_per_s": 48.8
      }
    }
    // ... additional runs for each workload and variant
  ],
  "notes": "Free-form textual notes."
}
```

Constraints enforced here:

- **At least one baseline and one treatment run per workload.** This is
  implemented by running each variant once per workload.
- **All metric values are numbers** (no `null`, strings, dicts, or lists).
- Additional descriptive information (stdout-like notes, environment metadata
  beyond `environment`, qualitative comments) is stored in the `notes` field or
  other *non-metric* fields; it is never placed under `metrics`.

## Extending this template for real-world use

In a production setting, you can extend this project by:

- Replacing `experiment/data_generation.py` with loaders for real source and
  reference datasets.
- Implementing true vendor adapters in `experiment/vendors.py` with HTTP
  clients, authentication, rate limiting, and retry policies.
- Adding actual BLEU/COMET and compliance checkers in `experiment/metrics.py`
  using external libraries (e.g., `sacrebleu`, `unbabel-comet`) and rule-based
  or ML compliance systems.
- Encoding your contractual and governance rules in configuration files and
  enforcing them in the runner.

This skeleton focuses on **reproducible structure**, clarity, and a clean
separation between baseline vs. treatment so you can evaluate multi-vendor and
hybrid sourcing strategies in a controlled manner.
