"""Direct contract tests for version-dispatched readiness receipts."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIR = ROOT / "tests" / "schema" / "fixtures" / "readiness"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validator() -> Draft202012Validator:
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.json"):
        contents = load_json(path)
        registry = registry.with_resource(
            contents["$id"], Resource.from_contents(contents)
        )
    schema = load_json(SCHEMA_DIR / "readiness-receipt.schema.json")
    return Draft202012Validator(schema, registry=registry, format_checker=FormatChecker())


class ReadinessReceiptContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = validator()
        cls.environment_hold = load_json(FIXTURE_DIR / "environment-hold-v1.json")
        cls.part_hold = load_json(FIXTURE_DIR / "part-contract-not-implemented-v1.json")

    def assert_valid(self, instance: dict) -> None:
        errors = sorted(self.validator.iter_errors(instance), key=lambda error: list(error.path))
        self.assertEqual([], errors, "\n".join(error.message for error in errors))

    def assert_invalid(self, instance: dict) -> None:
        self.assertTrue(list(self.validator.iter_errors(instance)))

    def test_current_hold_receipts_are_version_dispatched(self) -> None:
        self.assert_valid(self.environment_hold)
        self.assert_valid(self.part_hold)

    def test_unknown_version_and_cross_kind_fields_are_rejected(self) -> None:
        wrong_version = copy.deepcopy(self.environment_hold)
        wrong_version["contract_version"] = "2.0.0"
        self.assert_invalid(wrong_version)

        cross_kind = copy.deepcopy(self.part_hold)
        cross_kind["issuance_status"] = "HOLD_NOT_ISSUED"
        self.assert_invalid(cross_kind)

    def test_receipt_v1_cannot_carry_output_references(self) -> None:
        environment = copy.deepcopy(self.environment_hold)
        environment["issued_contract_ref"] = {
            "environment_id": "synthetic-environment",
            "artifact_sha256": "sha256:" + "0" * 64,
        }
        self.assert_invalid(environment)

        part = copy.deepcopy(self.part_hold)
        part["evidence_record_ref"] = {
            "evidence_id": "synthetic-evidence",
            "evidence_content_sha256": "sha256:" + "0" * 64,
        }
        self.assert_invalid(part)

    def test_receipt_v1_rejects_not_yet_supported_success_statuses(self) -> None:
        environment = copy.deepcopy(self.environment_hold)
        environment["issuance_status"] = "ISSUED"
        environment["processing_status"] = "VALID"
        environment["blocker_codes"] = []
        environment["issued_contract_ref"] = {
            "environment_id": "synthetic-environment",
            "artifact_sha256": "sha256:" + "0" * 64,
        }
        self.assert_invalid(environment)

        part = copy.deepcopy(self.part_hold)
        part["readiness_status"] = "RECORD_VALIDATED"
        part["blocker_codes"] = []
        part["target_contract"]["implementation_status"] = "IMPLEMENTED"
        part["evidence_record_ref"] = {
            "evidence_id": "synthetic-evidence",
            "evidence_content_sha256": "sha256:" + "0" * 64,
        }
        self.assert_invalid(part)

    def test_actual_environment_review_cannot_be_issuable_candidate(self) -> None:
        optimistic_actual = copy.deepcopy(self.environment_hold)
        optimistic_actual["source_result"]["evidence_class"] = "ACTUAL_REVIEW"
        optimistic_actual["issuance_status"] = "ISSUABLE_CANDIDATE"
        optimistic_actual["processing_status"] = "VALID"
        optimistic_actual["blocker_codes"] = []
        self.assert_invalid(optimistic_actual)

    def test_synthetic_environment_control_cannot_be_issuable_candidate(self) -> None:
        optimistic_synthetic = copy.deepcopy(self.environment_hold)
        optimistic_synthetic["source_result"]["evidence_class"] = "SYNTHETIC_CONTROL"
        optimistic_synthetic["issuance_status"] = "ISSUABLE_CANDIDATE"
        optimistic_synthetic["processing_status"] = "VALID"
        optimistic_synthetic["blocker_codes"] = []
        self.assert_invalid(optimistic_synthetic)

    def test_test_gate_cannot_claim_part_v2_is_implemented(self) -> None:
        optimistic_part = copy.deepcopy(self.part_hold)
        optimistic_part["readiness_status"] = "HOLD_NOT_READY"
        optimistic_part["target_contract"]["implementation_status"] = "IMPLEMENTED"
        self.assert_invalid(optimistic_part)

    def test_receipts_never_become_assurance_or_decision_inputs(self) -> None:
        for fixture in (self.environment_hold, self.part_hold):
            decision_use = copy.deepcopy(fixture)
            decision_use["used_for_decision"] = True
            self.assert_invalid(decision_use)

            supported = copy.deepcopy(fixture)
            supported["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
            self.assert_invalid(supported)


if __name__ == "__main__":
    unittest.main()
