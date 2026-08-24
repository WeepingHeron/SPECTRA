from __future__ import annotations

import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.parts_evidence.evidence_gate import (
    PROVENANCE_CODES,
    STRUCTURAL_CODES,
    apply_operations,
    load_json,
    materialize_synthetic_record,
    validate_json_text,
    validate_record,
)


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


class ExecutableExactPartEvidenceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        raw_control = load_json(FIXTURES / "synthetic-control.json")
        cls.control = materialize_synthetic_record(raw_control, FIXTURES)
        cls.attack_cases = load_json(FIXTURES / "attack-cases.json")

    def assert_safe_hold(self, result) -> None:
        self.assertEqual(result.assurance_decision, "HOLD")
        self.assertFalse(result.used_for_decision)
        self.assertIsNone(result.recommendation)
        self.assertNotEqual(result.applicability_status, "APPLICABLE")
        self.assertNotEqual(result.identity_status, "EXACT_MATCH")

    def test_01_synthetic_control_is_structurally_valid_demo_only(self) -> None:
        result = validate_record(self.control, FIXTURES)
        self.assertEqual(result.processing_status, "VALID")
        self.assertEqual(result.identity_status, "PARTIAL_UNRESOLVED")
        self.assertEqual(result.applicability_status, "NOT_EVALUATED")
        self.assertIn("SYNTHETIC_DEMO_ONLY", result.codes)
        self.assertFalse(set(result.codes) & STRUCTURAL_CODES)
        self.assertFalse(set(result.codes) & PROVENANCE_CODES)
        self.assert_safe_hold(result)

    def test_02_all_executable_attack_cases_fail_closed(self) -> None:
        self.assertGreaterEqual(len(self.attack_cases), 15)
        for case in self.attack_cases:
            with self.subTest(attack_id=case["attack_id"]):
                attacked = apply_operations(self.control, case["operations"])
                result = validate_record(attacked, FIXTURES)
                self.assertTrue(set(case["expected_codes"]).issubset(result.codes))
                if "expected_identity" in case:
                    self.assertEqual(result.identity_status, case["expected_identity"])
                self.assert_safe_hold(result)

    def test_03_malformed_json_and_non_object_are_stable(self) -> None:
        malformed = validate_json_text('{"kind":', FIXTURES)
        self.assertEqual(malformed.processing_status, "INVALID_INPUT")
        self.assertIn("MALFORMED_JSON", malformed.codes)
        self.assert_safe_hold(malformed)

        non_object = validate_record(["not", "an", "object"], FIXTURES)
        self.assertEqual(non_object.processing_status, "INVALID_INPUT")
        self.assertIn("MALFORMED_RECORD_TYPE", non_object.codes)
        self.assert_safe_hold(non_object)

    def test_04_family_only_is_not_exact_or_decision_eligible(self) -> None:
        family = copy.deepcopy(self.control)
        family["bom"]["approval"] = {"status": "NOT_PROVIDED"}
        family["tested_identity"]["exact_part_number"] = {"status": "NOT_REPORTED"}
        family["tested_identity"]["generic_part_number"] = {
            "status": "VERIFIED",
            "value": {"raw": "SYN-FAMILY", "canonical": "SYN-FAMILY"},
            "locator_ids": ["loc-synthetic-control"],
        }
        family["tested_identity"]["family_relation"] = {
            "status": "VERIFIED",
            "value": {"raw": "SYNTHETIC_RELATION", "canonical": "SYNTHETIC_RELATION"},
            "locator_ids": ["loc-synthetic-control"],
        }
        result = validate_record(family, FIXTURES)
        self.assertEqual(result.identity_status, "FAMILY_ONLY")
        self.assertIn("BOM_APPROVAL_MISSING", result.codes)
        self.assert_safe_hold(result)

    def test_05_h05_discovery_candidate_remains_unresolved(self) -> None:
        candidate = load_json(FIXTURES / "h05-discovery-candidate.json")
        result = validate_record(candidate, FIXTURES)
        expected = {
            "BOM_APPROVAL_MISSING",
            "BOM_APPROVAL_TARGET_MISSING",
            "RIGHTS_UNRESOLVED",
            "RAW_MANIFEST_REFERENCE_MISSING",
            "MISSION_APPLICABILITY_NOT_EVALUATED",
            "EXACT_TEST_ARTICLE_IDENTITY_UNRESOLVED",
            "SEB_EVIDENCE_MISSING",
            "SEGR_EVIDENCE_MISSING",
            "DISCOVERY_ONLY_INPUT",
        }
        self.assertTrue(expected.issubset(result.codes))
        self.assertEqual(result.identity_status, "PARTIAL_UNRESOLVED")
        self.assert_safe_hold(result)

    def test_06_artifact_filesystem_errors_fail_closed(self) -> None:
        for method_name in ("resolve", "stat", "read_bytes"):
            with self.subTest(method=method_name):
                with patch.object(
                    Path,
                    method_name,
                    side_effect=PermissionError("synthetic access denial"),
                ):
                    result = validate_record(copy.deepcopy(self.control), FIXTURES)
                self.assertIn("ARTIFACT_ACCESS_ERROR", result.codes)
                self.assert_safe_hold(result)

    def test_07_unexpected_programming_errors_are_not_swallowed(self) -> None:
        with patch.object(Path, "stat", side_effect=RuntimeError("synthetic bug")):
            with self.assertRaisesRegex(RuntimeError, "synthetic bug"):
                validate_record(copy.deepcopy(self.control), FIXTURES)


if __name__ == "__main__":
    unittest.main()
