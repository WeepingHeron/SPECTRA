import copy
import hashlib
import json
import math
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.spectra_gcp_adapter import build_product_timeline


ROOT = Path(__file__).resolve().parents[2]
RECEIPT_PATH = ROOT / "docs/workstreams/70-platform-gcp/evidence/h07-live-execution-receipt.json"
SNAPSHOT_PATH = ROOT / "demo/data/h05-gcp-snapshot.json"
BUILDER_PATH = ROOT / "demo/build_gcp_live_timeline.py"


class ProductTimelineTest(unittest.TestCase):
    def setUp(self):
        self.actual_receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        self.failed_receipt = {
            "contract_version": "SPECTRA_READ_ONLY_GCP_CONNECTOR_RECEIPT_1.0.0",
            "processing_status": "PROVENANCE_FAILURE",
            "connector_status": "NOT_OBSERVED",
            "observation_mode": "LIVE_API",
            "assurance_decision": "HOLD",
            "used_for_decision": False,
            "stable_codes": ["GCLOUD_AUTH_REAUTH_REQUIRED"],
            "event_receipt": None,
        }
        self.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    def valid_live_receipt(self):
        execution = {
            "project_id": "iceu-686",
            "region": "asia-northeast3",
            "workflow_name": "spectra-h04-e2e",
            "execution_id": "ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34",
            "correlation_id": "spectra-h05-ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34",
        }
        return {
            "contract_version": "SPECTRA_READ_ONLY_GCP_CONNECTOR_RECEIPT_1.0.0",
            "processing_status": "VALID",
            "connector_status": "OBSERVED",
            "observation_mode": "LIVE_API",
            "assurance_decision": "HOLD",
            "used_for_decision": False,
            "stable_codes": [],
            "event_receipt": {
                "processing_status": "VALID",
                "stream_status": "COMPLETE",
                "execution_status": "SUCCEEDED",
                "workflow_success_is_business_pass": False,
                "assurance_decision": "HOLD",
                "execution_ref": execution,
                "timeline": [
                    {
                        "sequence": 0,
                        "occurred_at": "2026-08-25T00:00:00Z",
                        "event_type": "WORKFLOW_STARTED",
                        "source_kind": "WORKFLOW",
                        "source_id": "spectra-h04-e2e",
                        "state": "RUNNING",
                    }
                ],
                "stream_sha256": "sha256:" + "1" * 64,
            },
        }

    def test_auth_failure_uses_labeled_verified_snapshot_fallback(self):
        result = build_product_timeline(
            self.failed_receipt, verified_snapshot=self.snapshot
        )
        self.assertEqual(result["display_mode"], "VERIFIED_SNAPSHOT_FALLBACK")
        self.assertEqual(result["live_connection_status"], "NOT_OBSERVED")
        self.assertFalse(result["live_api_observed"])
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["timeline_kind"], "SUMMARY_NOT_EVENT_REPLAY")
        self.assertEqual(result["source_codes"], ["GCLOUD_AUTH_REAUTH_REQUIRED"])
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["workflow_success_is_business_pass"])
        self.assertTrue(all(step["occurred_at"] is None for step in result["steps"]))

    def test_valid_live_receipt_is_preferred_without_assurance_promotion(self):
        result = build_product_timeline(
            self.valid_live_receipt(), verified_snapshot=self.snapshot
        )
        self.assertEqual(result["display_mode"], "LIVE_API")
        self.assertTrue(result["live_api_observed"])
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])

    def test_actual_read_only_receipt_builds_live_api_timeline(self):
        result = build_product_timeline(
            self.actual_receipt, verified_snapshot=self.snapshot
        )
        self.assertEqual(result["display_mode"], "LIVE_API")
        self.assertEqual(result["live_connection_status"], "OBSERVED")
        self.assertTrue(result["live_api_observed"])
        self.assertEqual(len(result["steps"]), 8)
        self.assertEqual(result["steps"][-1]["state"], "SUCCEEDED")
        self.assertEqual(result["assurance_decision"], "HOLD")

    def test_optimistic_live_receipt_is_not_displayed_as_live(self):
        attacked = self.valid_live_receipt()
        attacked["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        result = build_product_timeline(attacked, verified_snapshot=self.snapshot)
        self.assertEqual(result["display_mode"], "VERIFIED_SNAPSHOT_FALLBACK")
        self.assertFalse(result["live_api_observed"])

    def test_tampered_fallback_closes_as_data_unavailable(self):
        attacked = copy.deepcopy(self.snapshot)
        attacked["workflow"]["revision"] = "attacker-revision"
        result = build_product_timeline(
            self.failed_receipt, verified_snapshot=attacked
        )
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertEqual(result["display_mode"], "DATA_UNAVAILABLE")
        self.assertEqual(result["steps"], [])
        self.assertEqual(result["assurance_decision"], "HOLD")

    def test_nonfinite_live_timeline_cannot_escape_or_display_live(self):
        attacked = self.valid_live_receipt()
        attacked["event_receipt"]["timeline"][0]["sequence"] = math.nan
        result = build_product_timeline(attacked, verified_snapshot=self.snapshot)
        self.assertEqual(result["display_mode"], "VERIFIED_SNAPSHOT_FALLBACK")
        self.assertFalse(result["live_api_observed"])

    def test_timeline_hash_and_exporter_are_deterministic(self):
        result = build_product_timeline(
            self.failed_receipt, verified_snapshot=self.snapshot
        )
        self.assertEqual(
            result["timeline_sha256"],
            "sha256:"
            + hashlib.sha256(result["timeline_hash_preimage"].encode()).hexdigest(),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first_json = root / "first.json"
            first_js = root / "first.js"
            second_json = root / "second.json"
            second_js = root / "second.js"
            for json_path, js_path in (
                (first_json, first_js),
                (second_json, second_js),
            ):
                subprocess.run(
                    [
                        "python3",
                        str(BUILDER_PATH),
                        "--json",
                        str(json_path),
                        "--javascript",
                        str(js_path),
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(first_json.read_bytes(), second_json.read_bytes())
            self.assertEqual(first_js.read_bytes(), second_js.read_bytes())


if __name__ == "__main__":
    unittest.main()
