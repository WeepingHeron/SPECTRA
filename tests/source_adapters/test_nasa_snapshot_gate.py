#!/usr/bin/env python3
"""Attack tests for the local NASA snapshot intake gate."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_source_adapter.nasa_snapshot_gate import REQUIRED_ACTIONS, evaluate_nasa_snapshot  # noqa: E402

FIXTURES = ROOT / "tests/source_adapters/fixtures"
NOW = datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc)


class NasaSnapshotGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.control = json.loads((FIXTURES / "nasa-snapshot-control.json").read_text(encoding="utf-8"))
        cls.content = (FIXTURES / "nasa-snapshot-control.txt").read_bytes()

    def evaluate(self, candidate: dict, *, anchors=None, content: bytes | None = None) -> dict:
        return evaluate_nasa_snapshot(
            candidate,
            self.content if content is None else content,
            trusted_anchors=anchors,
            now=NOW,
        )

    def assert_hold(self, result: dict, *codes: str) -> None:
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertEqual(result["use_status"], "NOT_FOR_DECISION")
        self.assertEqual(result["engineering_gate"], "NOT_EVALUATED")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertEqual(result["suitability"], "NOT_EVALUATED")
        for code in codes:
            self.assertIn(code, result["stable_codes"])

    def trusted_anchors(self, candidate: dict) -> dict:
        identity = candidate["part_identity"]
        return {
            "manifest": {
                "manifest_id": "external-manifest-001",
                "record_id": candidate["record_id"],
                "official_locator": candidate["official_locator"],
                "content_sha256": candidate["content_sha256"],
                "captured_at": candidate["captured_at"],
                "last_modified": candidate["last_modified"],
                "source_revision": candidate["source_revision"],
            },
            "rights": {
                "anchor_id": "external-rights-001",
                "record_id": candidate["record_id"],
                "allowed_actions": sorted(REQUIRED_ACTIONS),
                "status": "ACTIVE",
            },
            "bom": {
                "anchor_id": "external-bom-001",
                "manufacturer": identity["manufacturer"],
                "orderable_part_number": identity["orderable_part_number"],
                "approval_status": "APPROVED",
            },
        }

    def actual_candidate(self) -> dict:
        candidate = copy.deepcopy(self.control)
        candidate["snapshot_class"] = "ACTUAL_CANDIDATE"
        for grant in candidate["rights"]:
            grant["grant_source"] = "NASA_DIRECT_GRANT"
        return candidate

    def test_bundled_synthetic_control_is_never_for_decision(self) -> None:
        result = self.evaluate(copy.deepcopy(self.control))
        self.assertEqual(
            {grant["grant_source"] for grant in self.control["rights"]},
            {"SYNTHETIC_CONTROL_ONLY"},
        )
        self.assertEqual(result["snapshot_class"], "SYNTHETIC_CONTROL")
        self.assertEqual(result["issuance_status"], "SYNTHETIC_CONTROL")
        self.assertEqual(result["use_status"], "NOT_FOR_DECISION")
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertEqual(result["stable_codes"], [])

    def test_actual_candidate_without_external_anchors_holds(self) -> None:
        candidate = self.actual_candidate()
        result = self.evaluate(candidate)
        self.assert_hold(
            result,
            "TRUSTED_MANIFEST_MISSING",
            "TRUSTED_RIGHTS_ANCHOR_MISSING",
            "APPROVED_BOM_ANCHOR_MISSING",
        )

    def test_exact_external_anchors_reach_review_only_not_decision(self) -> None:
        candidate = self.actual_candidate()
        result = self.evaluate(candidate, anchors=self.trusted_anchors(candidate))
        self.assertEqual(result["issuance_status"], "READY_FOR_REVIEW")
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["use_status"], "NOT_FOR_DECISION")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])

    def test_external_manifest_must_bind_revision_and_last_modified(self) -> None:
        candidate = self.actual_candidate()
        anchors = self.trusted_anchors(candidate)
        anchors["manifest"]["source_revision"] = "different-revision"
        anchors["manifest"]["last_modified"] = "2026-08-20T00:00:00Z"
        self.assert_hold(self.evaluate(candidate, anchors=anchors), "TRUSTED_MANIFEST_MISMATCH")

    def test_family_only_part_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.control)
        candidate["part_identity"]["identity_status"] = "FAMILY_ONLY"
        self.assert_hold(self.evaluate(candidate), "FAMILY_ONLY_PART_REJECTED")

    def test_non_nasa_host_and_redirect_are_rejected(self) -> None:
        candidate = copy.deepcopy(self.control)
        candidate["official_locator"] = "https://nasa.gov.attacker.example/record"
        candidate["redirect_chain"] = ["https://nepp.nasa.gov/record"]
        self.assert_hold(
            self.evaluate(candidate),
            "OFFICIAL_LOCATOR_NOT_ALLOWLISTED",
            "REDIRECT_NOT_ALLOWED",
        )

    def test_stale_and_naive_snapshot_times_are_rejected(self) -> None:
        stale = copy.deepcopy(self.control)
        stale["captured_at"] = "2026-01-01T00:00:00Z"
        self.assert_hold(self.evaluate(stale), "SNAPSHOT_STALE")
        naive = copy.deepcopy(self.control)
        naive["captured_at"] = "2026-08-24T09:00:00"
        self.assert_hold(self.evaluate(naive), "TIMEZONE_REQUIRED")

    def test_content_hash_mismatch_is_rejected(self) -> None:
        self.assert_hold(self.evaluate(copy.deepcopy(self.control), content=b"tampered\n"), "CONTENT_SHA256_MISMATCH")

    def test_rights_inheritance_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.control)
        candidate["rights"][0]["inherited_from"] = "PUBLIC_ACCESS_ASSUMPTION"
        self.assert_hold(self.evaluate(candidate), "RIGHTS_INHERITANCE_FORBIDDEN")

    def test_malformed_locator_port_and_rights_action_do_not_throw(self) -> None:
        locator = copy.deepcopy(self.control)
        locator["official_locator"] = "https://nepp.nasa.gov:bad/record"
        self.assert_hold(self.evaluate(locator), "OFFICIAL_LOCATOR_INVALID")
        rights = copy.deepcopy(self.control)
        rights["rights"][0]["action"] = ["LOCATOR_SHARE"]
        self.assert_hold(self.evaluate(rights), "ACTION_RIGHTS_INVALID")

    def test_self_declared_approval_is_rejected(self) -> None:
        candidate = copy.deepcopy(self.control)
        candidate["approval"] = {"status": "APPROVED", "by": "payload"}
        self.assert_hold(self.evaluate(candidate), "SELF_DECLARED_APPROVAL_REJECTED")

    def test_pass_and_suitability_promotions_are_rejected(self) -> None:
        candidate = copy.deepcopy(self.control)
        candidate["claimed_decision"] = "PASS"
        candidate["claimed_suitability"] = "SUITABLE"
        self.assert_hold(
            self.evaluate(candidate),
            "OPTIMISTIC_DECISION_REJECTED",
            "SUITABILITY_PROMOTION_REJECTED",
        )

    def test_provider_record_revision_and_last_modified_are_required(self) -> None:
        provider = copy.deepcopy(self.control)
        provider["provider"] = "ESA"
        self.assert_hold(self.evaluate(provider), "PROVIDER_NOT_NASA")
        record = copy.deepcopy(self.control)
        record["record_id"] = "unstable id"
        self.assert_hold(self.evaluate(record), "STABLE_RECORD_ID_INVALID")
        revision = copy.deepcopy(self.control)
        revision["source_revision"] = ""
        self.assert_hold(self.evaluate(revision), "SOURCE_REVISION_INVALID")
        modified = copy.deepcopy(self.control)
        modified["last_modified"] = "unknown"
        self.assert_hold(self.evaluate(modified), "LAST_MODIFIED_INVALID")

    def test_result_contains_no_content_bytes_or_generated_values(self) -> None:
        result = self.evaluate(copy.deepcopy(self.control))
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("SYNTHETIC NASA SNAPSHOT CONTROL", serialized)
        self.assertNotIn("official_locator", serialized)
        self.assertNotIn("content_sha256", serialized)
        self.assertNotIn("dose", serialized.lower())
        self.assertNotIn("confidence", serialized.lower())


if __name__ == "__main__":
    unittest.main()
