import json
import os
import unittest
from pathlib import Path


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure evidence directory exists and run the experiment entry point.
        self.evidence_dir = Path(os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence"))
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Import run after setting env var so it writes to the right place.
        # We re-run the experiment for each test module invocation; runtime is
        # small due to synthetic data and small segment counts.
        import run as run_module

        run_module.main()
        self.evidence_path = self.evidence_dir / "results.json"

    def test_evidence_file_exists(self) -> None:
        self.assertTrue(self.evidence_path.is_file(), "results.json must exist")

    def test_evidence_schema_and_metrics(self) -> None:
        with self.evidence_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level keys
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        self.assertEqual(data["chapter"], 12)
        self.assertEqual(
            data["experiment_id"], "ch12-vendor-bakeoff-hybrid-sourcing-001"
        )

        env = data["environment"]
        self.assertIsInstance(env.get("os"), str)
        self.assertIsInstance(env.get("python"), str)

        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 6)  # 3 workloads * 2 variants

        # Track seen variants per workload to ensure each workload has both.
        variants_per_workload = {}

        for run in runs:
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            variant = run["variant"]
            workload_id = run["workload_id"]
            run_id = run["run_id"]
            success = run["success"]
            metrics = run["metrics"]

            self.assertIn(variant, ("baseline", "treatment"))
            self.assertIsInstance(workload_id, str)
            self.assertIsInstance(run_id, str)
            self.assertIsInstance(success, bool)
            self.assertIsInstance(metrics, dict)

            # Each metric value must be a finite number (int or float).
            for key, value in metrics.items():
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} must be numeric, got {type(value)!r}",
                )

            # Record variant presence per workload.
            variants_per_workload.setdefault(workload_id, set()).add(variant)

        # Ensure that for each workload we have at least one baseline and one treatment run.
        expected_workloads = {
            "pharma_patient_info_high_risk",
            "finance_marketing_and_disclosures_medium_risk",
            "b2b_saas_ui_and_help_low_to_medium_risk",
        }
        self.assertTrue(
            expected_workloads.issubset(set(variants_per_workload.keys())),
            "All expected workloads must be present in runs",
        )

        for wl in expected_workloads:
            variants = variants_per_workload.get(wl, set())
            self.assertIn("baseline", variants, f"Workload {wl} missing baseline run")
            self.assertIn("treatment", variants, f"Workload {wl} missing treatment run")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
