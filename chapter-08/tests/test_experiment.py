import json
import os
import unittest
from pathlib import Path


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure we run the experiment once for all tests if evidence not present.
        self.evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        self.evidence_path = Path(self.evidence_dir) / "results.json"
        if not self.evidence_path.exists():
            # Import run.main to execute experiment
            import run as experiment_run

            experiment_run.main()

        with self.evidence_path.open("r", encoding="utf-8") as f:
            self.data = json.load(f)

    def test_top_level_schema(self) -> None:
        d = self.data
        self.assertIsInstance(d, dict)
        self.assertIn("chapter", d)
        self.assertIn("experiment_id", d)
        self.assertIn("environment", d)
        self.assertIn("runs", d)

        self.assertEqual(d["chapter"], 8)
        self.assertEqual(d["experiment_id"], "exp-ch08-cultural-adaptation-workflow-v1")

        env = d["environment"]
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)
        self.assertIsInstance(env["os"], str)
        self.assertIsInstance(env["python"], str)

    def test_runs_structure_and_variants(self) -> None:
        runs = self.data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 6)  # 3 workloads * 2 variants

        workloads = {"WL1_marketing_landing_pages", "WL2_support_and_help_center_articles", "WL3_high_sensitivity_pharma_patient_leaflets"}

        by_workload = {wl: {"baseline": 0, "treatment": 0} for wl in workloads}

        for run in runs:
            self.assertIsInstance(run, dict)
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            variant = run["variant"]
            workload_id = run["workload_id"]

            self.assertIn(variant, {"baseline", "treatment"})
            self.assertIn(workload_id, workloads)
            self.assertIsInstance(run["run_id"], str)
            self.assertIsInstance(run["success"], bool)

            by_workload[workload_id][variant] += 1

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            # metrics must contain only numeric values
            self.assertGreater(len(metrics), 0)
            for key, value in metrics.items():
                self.assertIsInstance(key, str)
                # In Python, bool is a subclass of int, but we reject bools explicitly
                self.assertNotIsInstance(value, bool, msg=f"Metric {key} must not be bool")
                self.assertIsInstance(value, (int, float), msg=f"Metric {key} must be numeric")

        # Ensure at least one baseline and one treatment per workload
        for wl, counts in by_workload.items():
            self.assertGreaterEqual(counts["baseline"], 1, msg=f"No baseline run for {wl}")
            self.assertGreaterEqual(counts["treatment"], 1, msg=f"No treatment run for {wl}")


if __name__ == "__main__":
    unittest.main()
