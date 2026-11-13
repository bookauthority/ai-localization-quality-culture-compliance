import json
import os
import unittest


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure evidence directory exists and is isolated for tests.
        self.evidence_dir = "/evidence"
        os.makedirs(self.evidence_dir, exist_ok=True)
        # Remove any previous evidence file if present.
        evidence_path = os.path.join(self.evidence_dir, "results.json")
        if os.path.exists(evidence_path):
            os.remove(evidence_path)

    def test_run_produces_valid_evidence(self) -> None:
        # Import and run the experiment entry point.
        import run as experiment_run

        experiment_run.main()

        evidence_path = os.path.join(self.evidence_dir, "results.json")
        self.assertTrue(os.path.exists(evidence_path), "Evidence file not created")

        with open(evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level schema checks
        self.assertIn("chapter", data)
        self.assertIsInstance(data["chapter"], int)
        self.assertEqual(data["chapter"], 11)

        self.assertIn("experiment_id", data)
        self.assertIsInstance(data["experiment_id"], str)
        self.assertEqual(data["experiment_id"], "exp-ch11-linguistic-assets-tm-terms-vs-none-v1")

        self.assertIn("environment", data)
        self.assertIsInstance(data["environment"], dict)
        self.assertIn("os", data["environment"])
        self.assertIn("python", data["environment"])

        self.assertIn("runs", data)
        self.assertIsInstance(data["runs"], list)
        self.assertGreaterEqual(len(data["runs"]), 6)  # 3 workloads * 2 variants

        # Check runs structure and metrics numeric types
        workloads_seen = {}
        for run in data["runs"]:
            self.assertIn("variant", run)
            self.assertIn(run["variant"], ("baseline", "treatment"))

            self.assertIn("workload_id", run)
            workload_id = run["workload_id"]
            self.assertIsInstance(workload_id, str)

            self.assertIn("run_id", run)
            self.assertIsInstance(run["run_id"], str)

            self.assertIn("success", run)
            self.assertIsInstance(run["success"], bool)

            self.assertIn("metrics", run)
            self.assertIsInstance(run["metrics"], dict)

            # All metric values must be finite numbers
            for key, value in run["metrics"].items():
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} has non-numeric type {type(value)}",
                )

            workloads_seen.setdefault(workload_id, set()).add(run["variant"])

        # Each workload must have at least one baseline and one treatment run
        for workload_id, variants in workloads_seen.items():
            self.assertIn("baseline", variants, msg=f"Missing baseline for {workload_id}")
            self.assertIn("treatment", variants, msg=f"Missing treatment for {workload_id}")

        # Optional notes field may exist and should be a string if present
        if "notes" in data:
            self.assertIsInstance(data["notes"], str)


if __name__ == "__main__":
    unittest.main()
