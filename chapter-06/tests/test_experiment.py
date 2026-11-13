import json
import os
import unittest
from pathlib import Path


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Use a temporary evidence directory under the test working dir
        self.evidence_dir = Path("./_test_evidence").absolute()
        if self.evidence_dir.exists():
            # Clean up any prior test artifacts
            for p in self.evidence_dir.glob("*"):
                if p.is_file():
                    p.unlink()
        else:
            self.evidence_dir.mkdir(parents=True, exist_ok=True)
        os.environ["BOOKMAS_EVIDENCE_DIR"] = str(self.evidence_dir)

    def tearDown(self) -> None:
        # Best-effort cleanup of evidence directory
        if self.evidence_dir.exists():
            for p in self.evidence_dir.glob("*"):
                if p.is_file():
                    p.unlink()

    def _load_results(self):
        from run import main  # Import here to ensure env var is set first

        main()
        results_path = self.evidence_dir / "results.json"
        self.assertTrue(results_path.is_file(), "results.json was not created")
        with results_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def test_results_schema_and_values(self):
        data = self._load_results()

        # Top-level keys
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        self.assertEqual(data["chapter"], 6)
        self.assertEqual(
            data["experiment_id"],
            "ch06-operationalizing-quality-metrics-eval-feedback-v1",
        )

        env = data["environment"]
        self.assertIsInstance(env.get("os"), str)
        self.assertIsInstance(env.get("python"), str)

        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 6)  # 3 workloads * 2 variants

        workloads_seen = set()
        variants_by_workload = {}

        for run in runs:
            # Required run keys
            for key in ("variant", "workload_id", "run_id", "success", "metrics"):
                self.assertIn(key, run)

            variant = run["variant"]
            workload_id = run["workload_id"]
            workloads_seen.add(workload_id)

            self.assertIn(variant, ("baseline", "treatment"))
            self.assertIsInstance(run["run_id"], str)
            self.assertIsInstance(run["success"], bool)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            # At least one metric must be present
            self.assertGreaterEqual(len(metrics), 1)

            # All metric values must be plain numbers (int or float)
            for name, value in metrics.items():
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {name} must be numeric, got {type(value)}",
                )

            # Track which variants were present per workload
            variants_by_workload.setdefault(workload_id, set()).add(variant)

        # Expected workloads must all be present
        expected_workloads = {
            "w1-ui_product_strings",
            "w2-marketing_pages",
            "w3-high_risk_regulated_docs",
        }
        self.assertTrue(
            expected_workloads.issubset(workloads_seen),
            msg=f"Missing workloads in runs: {expected_workloads - workloads_seen}",
        )

        # Each workload must have at least one baseline and one treatment run
        for wid in expected_workloads:
            self.assertIn(wid, variants_by_workload)
            self.assertIn("baseline", variants_by_workload[wid])
            self.assertIn("treatment", variants_by_workload[wid])


if __name__ == "__main__":
    unittest.main()
