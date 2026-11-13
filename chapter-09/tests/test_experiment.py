import json
import os
import unittest


class ExperimentRunTest(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure evidence directory exists and is empty before each test.
        self.evidence_dir = "/evidence"
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.evidence_path = os.path.join(self.evidence_dir, "results.json")
        if os.path.exists(self.evidence_path):
            os.remove(self.evidence_path)

    def test_run_produces_valid_evidence(self) -> None:
        # Import and run the main function from run.py
        import run  # type: ignore

        run.main()

        # Evidence file should now exist.
        self.assertTrue(os.path.exists(self.evidence_path), "Evidence file was not created")

        with open(self.evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level schema checks
        self.assertIsInstance(data, dict)
        self.assertIn("chapter", data)
        self.assertEqual(data["chapter"], 9)

        self.assertIn("experiment_id", data)
        self.assertEqual(data["experiment_id"], "exp-ch09-compliance-pipeline-prepost-v1")

        self.assertIn("environment", data)
        env = data["environment"]
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)
        self.assertIsInstance(env["os"], str)
        self.assertIsInstance(env["python"], str)

        self.assertIn("runs", data)
        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreater(len(runs), 0, "No runs recorded in evidence")

        # Collect per-workload, per-variant presence
        workload_variants = {}
        for run_rec in runs:
            self.assertIsInstance(run_rec, dict)
            # Required keys
            for key in ("variant", "workload_id", "run_id", "success", "metrics"):
                self.assertIn(key, run_rec)

            variant = run_rec["variant"]
            workload_id = run_rec["workload_id"]
            run_id = run_rec["run_id"]
            success = run_rec["success"]
            metrics = run_rec["metrics"]

            self.assertIn(variant, ("baseline", "treatment"))
            self.assertIsInstance(workload_id, str)
            self.assertIsInstance(run_id, str)
            self.assertIsInstance(success, bool)

            # Metrics must be a dict of finite numbers only.
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 0, "Metrics dict must not be empty")
            for mk, mv in metrics.items():
                self.assertIsInstance(mk, str)
                self.assertIsInstance(mv, (int, float))

            workload_variants.setdefault(workload_id, set()).add(variant)

        # Each workload must have at least one baseline and one treatment run.
        for workload_id, variants in workload_variants.items():
            self.assertIn("baseline", variants, f"Workload {workload_id} missing baseline run")
            self.assertIn("treatment", variants, f"Workload {workload_id} missing treatment run")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
