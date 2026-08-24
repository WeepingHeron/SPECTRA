from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.assurance.gcp_d02.evaluate_remediation_batch import evaluate


ROOT = Path(__file__).resolve().parents[3]


class RemediationBatchEvaluationTests(unittest.TestCase):
    def test_actual_locked_batch_is_partial_safe(self) -> None:
        load = lambda path: json.loads((ROOT / path).read_text(encoding="utf-8"))
        result = evaluate(
            load("tests/assurance/gcp_d02/manifest.json"),
            load("docs/workstreams/70-platform-gcp/evidence/h09-remediation-control.json"),
            load("docs/workstreams/70-platform-gcp/evidence/h09-remediation-core-parity.json"),
            load("docs/workstreams/60-assurance-evals/evidence/ASR_D02_DEPLOYED_GCP_REMEDIATION_BATCH_H09.json"),
        )
        self.assertEqual(result["control_observation"]["classification"], "CONTROL_PASS")
        self.assertEqual(result["aggregate"]["safe_failures"], 4)
        self.assertEqual(result["aggregate"]["false_accepts"], 0)
        self.assertEqual(result["aggregate"]["false_passes"], 0)
        self.assertEqual(result["aggregate"]["unexpected_results"], 0)
        self.assertEqual(result["aggregate"]["result"], "PARTIAL_SAFE")


if __name__ == "__main__":
    unittest.main()
