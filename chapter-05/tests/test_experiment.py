import json
import os
import unittest


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure the experiment has been run; if not, run it.
        evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        self.evidence_path = os.path.join(evidence_dir, "results.json")
        if not os.path.exists(self.evidence_path):
            import run as experiment_run

            experiment_run.main()

    def test_evidence_schema_and_metrics(self) -> None:
        with open(self.evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level schema checks
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("chapter"), 5)
        self.assertEqual(data.get("experiment_id"), "exp-ch05-baseline-ai-localization-pipeline-v1")

        env = data.get("environment")
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)

        runs = data.get("runs")
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 4)  # 2 workloads * (baseline + treatment)

        # Track presence of variants per workload
        workloads = {
            "sample_customer_support_tickets": {"baseline": False, "treatment": False},
            "sample_marketing_snippets": {"baseline": False, "treatment": False},
        }

        for run in runs:
            self.assertIsInstance(run, dict)
            variant = run.get("variant")
            workload_id = run.get("workload_id")
            run_id = run.get("run_id")
            success = run.get("success")
            metrics = run.get("metrics")

            self.assertIn(variant, ("baseline", "treatment"))
            self.assertIn(workload_id, workloads.keys())
            self.assertIsInstance(run_id, str)
            self.assertIsInstance(success, bool)
            self.assertIsInstance(metrics, dict)

            # Mark presence of this variant for the workload
            workloads[workload_id][variant] = True

            # Metric values must be finite numbers when present
            for key, value in metrics.items():
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} must be numeric, got {type(value)}",
                )

        # Ensure both baseline and treatment were run for each workload
        for workload_id, variants in workloads.items():
            self.assertTrue(
                variants["baseline"],
                msg=f"Baseline run missing for workload {workload_id}",
            )
            self.assertTrue(
                variants["treatment"],
                msg=f"Treatment run missing for workload {workload_id}",
            )


if __name__ == "__main__":
    unittest.main()
