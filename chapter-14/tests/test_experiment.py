import json
import os
import unittest
from pathlib import Path

from experiment.config import EXPERIMENT_ID, CHAPTER, WORKLOADS, variant_parameters
from experiment.experiment_runner import ExperimentRunner
from experiment.instrumentation import MetricRecorder


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # Honour BOOKMAS_EVIDENCE_DIR contract and ensure a clean directory.
        self.evidence_dir = Path(os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence"))
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        results_file = self.evidence_dir / "results.json"
        if results_file.exists():
            results_file.unlink()

    def _results_path(self) -> Path:
        env_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        return Path(env_dir) / "results.json"

    def _load_results(self):
        from run import main  # import here to avoid side effects at module load

        # Run the main experiment, which should create the evidence file.
        main()

        results_path = self._results_path()
        self.assertTrue(results_path.exists(), "results.json was not created")

        with results_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def test_results_schema_and_metrics(self):
        data = self._load_results()

        # Top-level keys and types
        self.assertIn("chapter", data)
        self.assertIsInstance(data["chapter"], int)
        self.assertEqual(data["chapter"], CHAPTER)

        self.assertIn("experiment_id", data)
        self.assertIsInstance(data["experiment_id"], str)
        self.assertEqual(data["experiment_id"], EXPERIMENT_ID)

        self.assertIn("environment", data)
        env = data["environment"]
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)
        self.assertIsInstance(env["os"], str)
        self.assertIsInstance(env["python"], str)

        # Optional notes field must be a string when present.
        self.assertIn("notes", data)
        self.assertIsInstance(data["notes"], str)

        # Runs array
        self.assertIn("runs", data)
        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreater(len(runs), 0)

        workloads_seen = {}

        for run in runs:
            self.assertIsInstance(run, dict)
            # Required run fields
            for key in ("variant", "workload_id", "run_id", "success", "metrics"):
                self.assertIn(key, run, f"Missing key '{key}' in run record")

            # Variant must be exactly baseline or treatment.
            self.assertIn(run["variant"], ("baseline", "treatment"))
            self.assertIsInstance(run["workload_id"], str)
            self.assertIsInstance(run["run_id"], str)
            self.assertIsInstance(run["success"], bool)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 0)

            # All metric values must be finite numbers and only numeric
            # telemetry should appear here.
            disallowed_metric_keys = {
                "stdout",
                "environment_metadata",
                "risk-indicator",
                "logs",
            }
            for m_name, m_value in metrics.items():
                self.assertNotIn(
                    m_name,
                    disallowed_metric_keys,
                    msg=f"Non-metric key '{m_name}' must not appear inside metrics",
                )
                self.assertIsInstance(
                    m_value,
                    (int, float),
                    msg=f"Metric '{m_name}' must be numeric, got {type(m_value)!r}",
                )
                self.assertFalse(
                    m_value != m_value,  # NaN check
                    msg=f"Metric '{m_name}' must not be NaN",
                )
                self.assertNotIn(
                    m_value,
                    (float("inf"), float("-inf")),
                    msg=f"Metric '{m_name}' must be finite",
                )

            wid = run["workload_id"]
            workloads_seen.setdefault(wid, set()).add(run["variant"])

        # Ensure each workload has at least one baseline and one treatment run.
        expected_workloads = {w.workload_id for w in WORKLOADS}
        self.assertTrue(
            expected_workloads.issubset(workloads_seen.keys()),
            msg="Not all expected workloads were present in runs",
        )

        for wid in expected_workloads:
            variants = workloads_seen[wid]
            self.assertIn("baseline", variants, f"No baseline runs for {wid}")
            self.assertIn("treatment", variants, f"No treatment runs for {wid}")

        # Check that there is at least one shared metric name across runs.
        metric_name_sets = [set(run["metrics"].keys()) for run in runs]
        shared_metrics = set.intersection(*metric_name_sets)
        self.assertGreater(
            len(shared_metrics), 0, "No common metrics across runs; comparison impossible",
        )

    def test_results_reproducibility(self):
        # Running the experiment twice should produce identical evidence
        # because we use fixed seeds and deterministic logic. We also
        # indirectly assert that logs (which contain timestamps) do not
        # feed back into evidence.
        from run import main

        main()
        with self._results_path().open("r", encoding="utf-8") as f:
            first = json.load(f)

        # Run again and compare.
        main()
        with self._results_path().open("r", encoding="utf-8") as f:
            second = json.load(f)

        self.assertEqual(first, second, "Evidence output is not deterministic")

    def test_metric_recorder_rejects_non_numeric(self):
        # MetricRecorder should enforce numeric, finite values to keep
        # metrics clean and schema-compliant.
        recorder = MetricRecorder()

        with self.assertRaises(TypeError):
            recorder.record("not_numeric", "oops")  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            recorder.record("nan_value", float("nan"))

        with self.assertRaises(ValueError):
            recorder.record("inf_value", float("inf"))

    def test_variant_restrictions_negative(self):
        # Attempting to use an unsupported variant label must fail via
        # variant_parameters to guard the evidence schema over time.
        from experiment.config import WorkloadConfig, variant_parameters

        wl = WorkloadConfig(
            workload_id="synthetic-workload",
            description="Synthetic for negative variant test",
            risk_level="low",
            jobs_per_variant=1,
            baseline_latency_ms=100.0,
            treatment_latency_ms=110.0,
            baseline_quality_mean=0.8,
            treatment_quality_mean=0.9,
            baseline_cost_cents=5.0,
            treatment_cost_cents=5.5,
        )

        with self.assertRaises(ValueError):
            variant_parameters(wl, "control")

    def test_explicit_variant_values_in_runner(self):
        # Directly inspect ExperimentRunner output to ensure only the
        # allowed variant labels appear. This guards against regressions
        # where additional labels might be introduced without updating
        # the contract.
        runner = ExperimentRunner(
            experiment_id=EXPERIMENT_ID,
            chapter=CHAPTER,
            workloads=WORKLOADS,
        )
        runs = runner.run_all()
        seen_variants = {run["variant"] for run in runs}
        self.assertTrue(seen_variants.issubset({"baseline", "treatment"}))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
