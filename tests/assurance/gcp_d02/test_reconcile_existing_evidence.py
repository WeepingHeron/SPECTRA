import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tests/assurance/gcp_d02/reconcile_existing_evidence.py"
EVALUATOR = ROOT / "tests/assurance/gcp_d02/run_preparation.py"


class ExistingEvidenceReconciliationTest(unittest.TestCase):
    def test_existing_control_only_is_evaluated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "evidence.json"
            completed = subprocess.run(
                ["python3", str(SCRIPT), "--output", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"evaluated_attacks": 0', completed.stdout)
            evidence = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(evidence["aggregate"]["evaluated_controls"], 1)
            self.assertEqual(evidence["aggregate"]["evaluated_attacks"], 0)
            self.assertEqual(evidence["aggregate"]["false_passes"], "NOT_COMPUTED")
            self.assertEqual(evidence["aggregate"]["result"], "NOT_EVALUATED")
            control, *attacks = evidence["case_observations"]
            self.assertTrue(control["execution_attempted"])
            self.assertEqual(control["classification"], "CONTROL_PASS")
            self.assertTrue(all(not item["execution_attempted"] for item in attacks))
            self.assertTrue(all(item["classification"] == "NOT_EVALUATED" for item in attacks))
            evaluated = subprocess.run(
                ["python3", str(EVALUATOR), "--evaluate-evidence", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(evaluated.stdout)
            self.assertEqual(result["summary"]["not_evaluated"], 16)
            self.assertEqual(result["summary"]["false_passes"], 0)
            self.assertEqual(result["results"][0]["classification"], "CONTROL_PASS")


if __name__ == "__main__":
    unittest.main()
