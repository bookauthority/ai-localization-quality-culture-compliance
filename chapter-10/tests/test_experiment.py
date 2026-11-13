import json
import math
import os
import unittest
from pathlib import Path


EXPERIMENT_ID = "exp-ch10-routing-orchestration-cicd-001"
EXPECTED_CHAPTER = 10
EXPECTED_WORKLOAD_IDS = {
    "WL1-high-risk-product-docs",
    "WL2-low-risk-marketing-and-ui",
    "WL3-peak-load-stress-test",
}


class TestExperimentEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Ensure evidence has been generated. If not, run the experiment.
        evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        cls.evidence_dir = Path(evidence_dir)
        cls.evidence_dir.mkdir(parents=True, exist_ok=True)
        cls.evidence_file = cls.evidence_dir / "results.json"

        if not cls.evidence_file.exists():
            # Import and run the experiment
            from run import main as run_main

            run_main()

        with cls.evidence_file.open("r", encoding="utf-8") as f:
            cls.evidence = json.load(f)

    def test_top_level_structure(self) -> None:
        ev = self.evidence
        self.assertIsInstance(ev, dict)
        self.assertEqual(ev.get("chapter"), EXPECTED_CHAPTER)
        self.assertEqual(ev.get("experiment_id"), EXPERIMENT_ID)

        env = ev.get("environment")
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)

        self.assertIn("runs", ev)
        self.assertIsInstance(ev["runs"], list)

    def test_runs_schema_and_metrics(self) -> None:
        runs = self.evidence["runs"]
        self.assertGreaterEqual(len(runs), 1)

        seen = {"baseline": set(), "treatment": set()}

        for run in runs:
            self.assertIsInstance(run, dict)
            variant = run.get("variant")
            self.assertIn(variant, {"baseline", "treatment"})

            workload_id = run.get("workload_id")
            self.assertIn(workload_id, EXPECTED_WORKLOAD_IDS)

            run_id = run.get("run_id")
            self.assertIsInstance(run_id, str)
            self.assertTrue(run_id)

            success = run.get("success")
            self.assertIsInstance(success, bool)

            metrics = run.get("metrics")
            self.assertIsInstance(metrics, dict)

            # Required metrics
            for key in ("end_to_end_latency_p50", "end_to_end_latency_p95", "throughput"):
                self.assertIn(key, metrics)
                value = metrics[key]
                self.assertIsInstance(value, (int, float))
                self.assertTrue(math.isfinite(value))

            seen[variant].add(workload_id)

        # Ensure at least one baseline and one treatment run per workload
        for variant in ("baseline", "treatment"):
            for wid in EXPECTED_WORKLOAD_IDS:
                self.assertIn(
                    wid,
                    seen[variant],
                    msg=f"Missing {variant} run for workload {wid}",
                )

    def test_notes_present(self) -> None:
        # Notes field is optional per spec but recommended; here we ensure it's present
        ev = self.evidence
        self.assertIn("notes", ev)
        self.assertIsInstance(ev["notes"], str)
        self.assertTrue(len(ev["notes"]) > 0)


if __name__ == "__main__":
    unittest.main()
