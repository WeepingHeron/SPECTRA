import copy
import hashlib
import json
import unittest
from pathlib import Path

from src.spectra_parts_adapter import evaluate_published_artifact


ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / "docs/workstreams/40-parts-evidence/references"
CANDIDATE_PATH = REFERENCES / "23lc1024-published-source-candidate.json"
ANCHORS_PATH = REFERENCES / "23lc1024-published-source-anchors.json"
CONTROL_PATH = (
    ROOT / "tests/parts_evidence/fixtures/published-source-control.txt"
)
ACTUAL_LOCAL_PATH = Path("/private/tmp/23lc1024-cosmic-radiation-full.pdf")


class PublishedArtifactGateTest(unittest.TestCase):
    def setUp(self):
        self.candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
        self.anchors = json.loads(ANCHORS_PATH.read_text(encoding="utf-8"))
        self.control_bytes = CONTROL_PATH.read_bytes()

    def synthetic_control(self):
        candidate = copy.deepcopy(self.candidate)
        anchors = copy.deepcopy(self.anchors)
        digest = hashlib.sha256(self.control_bytes).hexdigest()
        candidate["source_class"] = "SYNTHETIC_CONTROL"
        candidate["byte_size"] = len(self.control_bytes)
        candidate["content_sha256"] = digest
        for grant in candidate["rights"]["action_grants"]:
            grant["basis"] = "SYNTHETIC_CONTROL_ONLY"
        anchors["manifest"]["byte_size"] = len(self.control_bytes)
        anchors["manifest"]["content_sha256"] = digest
        return candidate, anchors

    def evaluate(self, candidate=None, anchors=None, content=None):
        return evaluate_published_artifact(
            self.candidate if candidate is None else candidate,
            self.control_bytes if content is None else content,
            trusted_anchors=self.anchors if anchors is None else anchors,
        )

    def assert_hold(self, result, *codes):
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertEqual(result["use_status"], "NOT_FOR_DECISION")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertIsNone(result["artifact_binding"])
        for code in codes:
            self.assertIn(code, result["stable_codes"])

    def test_synthetic_control_binds_bytes_but_never_becomes_reference(self):
        candidate, anchors = self.synthetic_control()
        result = self.evaluate(candidate, anchors, self.control_bytes)

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["issuance_status"], "SYNTHETIC_CONTROL")
        self.assertEqual(
            result["source_artifact_status"], "BYTES_AND_LICENSE_SCOPE_BOUND"
        )
        self.assertEqual(result["stable_codes"], [])
        self.assertFalse(result["used_for_decision"])

    def test_actual_external_pdf_reaches_reference_review_when_available(self):
        if not ACTUAL_LOCAL_PATH.is_file():
            self.skipTest("external actual PDF is not present")
        result = self.evaluate(content=ACTUAL_LOCAL_PATH.read_bytes())

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(
            result["issuance_status"], "READY_FOR_REFERENCE_REVIEW"
        )
        self.assertEqual(
            result["rights_status"],
            "LICENSE_SCOPE_CONFIRMED_WITH_CONDITIONS",
        )
        self.assertEqual(
            result["artifact_binding"]["content_sha256"],
            self.candidate["content_sha256"],
        )
        self.assertEqual(result["assurance_decision"], "HOLD")

    def test_content_and_size_tamper_fail_closed(self):
        candidate, anchors = self.synthetic_control()
        tampered = self.control_bytes + b"tamper"
        result = self.evaluate(candidate, anchors, tampered)

        self.assert_hold(
            result, "CONTENT_SIZE_MISMATCH", "CONTENT_SHA256_MISMATCH"
        )

    def test_candidate_and_anchor_rebinding_cannot_replace_reviewed_pdf(self):
        if not ACTUAL_LOCAL_PATH.is_file():
            self.skipTest("external actual PDF is not present")
        tampered = ACTUAL_LOCAL_PATH.read_bytes() + b"tamper"
        digest = hashlib.sha256(tampered).hexdigest()
        candidate = copy.deepcopy(self.candidate)
        anchors = copy.deepcopy(self.anchors)
        candidate["byte_size"] = len(tampered)
        candidate["content_sha256"] = digest
        anchors["manifest"]["byte_size"] = len(tampered)
        anchors["manifest"]["content_sha256"] = digest

        result = self.evaluate(candidate, anchors, tampered)
        self.assert_hold(result, "REVIEWED_ARTIFACT_IDENTITY_MISMATCH")

    def test_missing_and_mismatched_anchors_fail_closed(self):
        candidate, anchors = self.synthetic_control()
        missing = self.evaluate(candidate, {}, self.control_bytes)
        mismatched = copy.deepcopy(anchors)
        mismatched["manifest"]["content_sha256"] = "0" * 64
        mismatch_result = self.evaluate(
            candidate, mismatched, self.control_bytes
        )

        self.assert_hold(missing, "TRUSTED_MANIFEST_MISMATCH")
        self.assert_hold(missing, "TRUSTED_RIGHTS_REVIEW_MISMATCH")
        self.assert_hold(mismatch_result, "TRUSTED_MANIFEST_MISMATCH")

    def test_optimistic_use_is_rejected(self):
        candidate, anchors = self.synthetic_control()
        candidate["claimed_use_status"] = "FOR_DECISION"
        candidate["claimed_decision"] = "PASS"

        self.assert_hold(
            self.evaluate(candidate, anchors, self.control_bytes),
            "OPTIMISTIC_USE_REJECTED",
        )

    def test_non_allowlisted_and_malformed_urls_are_rejected(self):
        candidate, anchors = self.synthetic_control()
        candidate["official_record_url"] = (
            "https://jlupub.ub.uni-giessen.de.attacker.example/items/fake"
        )
        candidate["artifact_url"] = (
            "https://jlupub.ub.uni-giessen.de:bad/server/api/core/bitstreams/x"
        )

        result = self.evaluate(candidate, anchors, self.control_bytes)
        self.assert_hold(
            result,
            "OFFICIAL_RECORD_URL_INVALID",
            "ARTIFACT_URL_INVALID",
            "SOURCE_LOCATOR_IDENTITY_MISMATCH",
        )

    def test_license_and_attribution_must_stay_bound_to_record(self):
        candidate, anchors = self.synthetic_control()
        candidate["license"]["id"] = "PUBLIC"
        candidate["attribution"]["source_url"] = "https://example.invalid"
        candidate["attribution"]["modified"] = True

        result = self.evaluate(candidate, anchors, self.control_bytes)
        self.assert_hold(
            result,
            "LICENSE_BINDING_INVALID",
            "ATTRIBUTION_BINDING_MISMATCH",
            "MODIFICATION_NOTICE_INVALID",
        )

    def test_action_rights_cannot_be_inherited_or_omitted(self):
        candidate, anchors = self.synthetic_control()
        candidate["rights"]["action_grants"].pop()
        candidate["rights"]["action_grants"][0]["basis"] = (
            "PUBLIC_ACCESS_ASSUMPTION"
        )

        result = self.evaluate(candidate, anchors, self.control_bytes)
        self.assert_hold(
            result, "ACTION_RIGHT_NOT_ACTIVE", "ACTION_RIGHTS_INCOMPLETE"
        )

    def test_condition_and_rights_anchor_tamper_fail_closed(self):
        candidate, anchors = self.synthetic_control()
        candidate["rights"]["conditions"].remove("NO_ENDORSEMENT")
        anchors["rights_review"]["status"] = "SELF_APPROVED"

        result = self.evaluate(candidate, anchors, self.control_bytes)
        self.assert_hold(
            result,
            "LICENSE_CONDITIONS_INCOMPLETE",
            "TRUSTED_RIGHTS_REVIEW_MISMATCH",
        )

    def test_malformed_types_and_unknown_fields_do_not_throw(self):
        candidate, anchors = self.synthetic_control()
        candidate["byte_size"] = True
        candidate["approval"] = "APPROVED"
        result = self.evaluate(candidate, anchors, content="not-bytes")

        self.assert_hold(
            result,
            "INPUT_FIELD_FORBIDDEN",
            "CONTENT_BYTES_INVALID",
            "CONTENT_SIZE_MISMATCH",
            "CONTENT_SHA256_MISMATCH",
        )

    def test_receipt_keeps_non_copyright_and_scientific_limits_explicit(self):
        candidate, anchors = self.synthetic_control()
        result = self.evaluate(candidate, anchors, self.control_bytes)

        self.assertEqual(
            result["limitations"],
            [
                "NON_COPYRIGHT_RIGHTS_NOT_ASSESSED",
                "SCIENTIFIC_ACCURACY_NOT_ESTABLISHED",
                "EXACT_PART_IDENTITY_NOT_ESTABLISHED",
            ],
        )
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("Effects of Cosmic Radiation", serialized)
        self.assertNotIn("Mona C. Plettenberg", serialized)


if __name__ == "__main__":
    unittest.main()
