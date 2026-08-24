import copy
import json
import unittest
from pathlib import Path

from src.spectra_parts_adapter import assess_published_reference_package


ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / "docs/workstreams/40-parts-evidence/references"
COMPARISON_PATH = REFERENCES / "23lc1024-published-comparison.json"
CANDIDATE_PATH = REFERENCES / "23lc1024-published-source-candidate.json"
ANCHORS_PATH = REFERENCES / "23lc1024-published-source-anchors.json"
ACTUAL_LOCAL_PATH = Path("/private/tmp/23lc1024-cosmic-radiation-full.pdf")


class PublishedReferencePackageTest(unittest.TestCase):
    def setUp(self):
        self.comparison = json.loads(COMPARISON_PATH.read_text(encoding="utf-8"))
        self.candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
        self.anchors = json.loads(ANCHORS_PATH.read_text(encoding="utf-8"))

    def assess(self, comparison=None, candidate=None, anchors=None, content=None):
        if content is None:
            if not ACTUAL_LOCAL_PATH.is_file():
                self.skipTest("external actual PDF is not present")
            content = ACTUAL_LOCAL_PATH.read_bytes()
        return assess_published_reference_package(
            self.comparison if comparison is None else comparison,
            self.candidate if candidate is None else candidate,
            content,
            trusted_anchors=self.anchors if anchors is None else anchors,
        )

    def test_actual_source_resolves_only_manifest_and_rights_codes(self):
        result = self.assess()

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(
            result["package_status"], "SOURCE_READY_COMPARISON_BLOCKED"
        )
        self.assertEqual(
            result["resolved_source_codes"],
            ["RIGHTS_SCOPE_UNRESOLVED", "SOURCE_ARTIFACT_MANIFEST_MISSING"],
        )
        self.assertNotIn(
            "SOURCE_ARTIFACT_MANIFEST_MISSING",
            result["remaining_blocking_codes"],
        )
        self.assertNotIn(
            "RIGHTS_SCOPE_UNRESOLVED", result["remaining_blocking_codes"]
        )

    def test_exact_part_and_environment_blockers_remain_after_source_pass(self):
        result = self.assess()

        self.assertTrue(
            {
                "PART_IDENTITY_PARTIAL",
                "PACKAGE_MISMATCH",
                "LOT_DIE_UNRESOLVED",
                "MISSION_ENVIRONMENT_UNAVAILABLE",
                "TID_EVIDENCE_MISSING",
                "DESTRUCTIVE_SEE_EVIDENCE_MISSING",
            }.issubset(result["remaining_blocking_codes"])
        )
        self.assertEqual(result["comparison_status"], "NOT_COMPARABLE")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])

    def test_source_and_comparison_hash_must_match(self):
        comparison = copy.deepcopy(self.comparison)
        comparison["published_observation"]["source"][
            "observed_artifact_sha256"
        ] = "0" * 64

        result = self.assess(comparison=comparison)

        self.assertEqual(result["processing_status"], "INVALID_INPUT")
        self.assertEqual(result["package_status"], "PACKAGE_NOT_READY")
        self.assertIn("SOURCE_PACKAGE_BINDING_FAILED", result["stable_codes"])
        self.assertEqual(result["resolved_source_codes"], [])

    def test_comparison_optimism_cannot_be_laundered_by_valid_source(self):
        comparison = copy.deepcopy(self.comparison)
        comparison["used_for_decision"] = True

        result = self.assess(comparison=comparison)

        self.assertEqual(result["processing_status"], "INVALID_INPUT")
        self.assertIn("COMPARISON_RECEIPT_INVALID", result["stable_codes"])
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])

    def test_missing_source_anchors_cannot_resolve_source_codes(self):
        result = self.assess(anchors={})

        self.assertEqual(result["package_status"], "PACKAGE_NOT_READY")
        self.assertIn("SOURCE_PACKAGE_BINDING_FAILED", result["stable_codes"])
        self.assertEqual(result["resolved_source_codes"], [])
        self.assertIn(
            "SOURCE_ARTIFACT_MANIFEST_MISSING",
            result["remaining_blocking_codes"],
        )


if __name__ == "__main__":
    unittest.main()
