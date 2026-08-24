"""Bounded local QA for readiness gates; no live evidence or GCP access."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
READINESS_FIXTURES = ROOT / "tests" / "schema" / "fixtures" / "readiness"
PART_FIXTURES = ROOT / "tests" / "parts_evidence" / "fixtures"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "environment"))
sys.path.insert(0, str(ROOT / "tests" / "parts_evidence"))

from spectra_env_adapter import assess_issuance  # noqa: E402
from evidence_gate import load_json, materialize_synthetic_record, validate_record  # noqa: E402
from test_issuance_gate import synthetic_control  # noqa: E402


def readiness_validator() -> Draft202012Validator:
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.json"):
        contents = json.loads(path.read_text(encoding="utf-8"))
        registry = registry.with_resource(
            contents["$id"], Resource.from_contents(contents)
        )
    dispatcher = json.loads(
        (SCHEMA_DIR / "readiness-receipt.schema.json").read_text(encoding="utf-8")
    )
    return Draft202012Validator(
        dispatcher,
        registry=registry,
        format_checker=FormatChecker(),
    )


def error_paths(errors) -> set[tuple[object, ...]]:
    """Collect leaf paths hidden below the dispatcher's oneOf error."""

    pending = list(errors)
    paths: set[tuple[object, ...]] = set()
    while pending:
        error = pending.pop()
        if error.context:
            pending.extend(error.context)
        else:
            paths.add(tuple(error.path))
    return paths


class LocalReadinessFailClosedQaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.part_control = materialize_synthetic_record(
            load_json(PART_FIXTURES / "synthetic-control.json"),
            PART_FIXTURES,
        )
        cls.validator = readiness_validator()

    def assert_part_hold(self, result, code: str) -> None:
        self.assertIn(code, result.codes)
        self.assertEqual("HOLD", result.assurance_decision)
        self.assertFalse(result.used_for_decision)
        self.assertIsNone(result.recommendation)
        self.assertNotEqual("EXACT_MATCH", result.identity_status)
        self.assertNotEqual("APPLICABLE", result.applicability_status)

    def test_ws31_malformed_evaluation_times_hold_without_exception(self) -> None:
        invalid_times = (
            datetime(2026, 8, 24),
            "2026-08-24T00:00:00Z",
            0,
            False,
            {},
            [],
        )
        for invalid_time in invalid_times:
            with self.subTest(invalid_time=repr(invalid_time)):
                evidence = synthetic_control()
                evidence["evidence_class"] = "ACTUAL_REVIEW"
                result = assess_issuance(evidence, now=invalid_time)
                self.assertEqual("HOLD_NOT_ISSUED", result["issuance_status"])
                self.assertEqual("PROVENANCE_FAILURE", result["processing_status"])
                self.assertEqual("HOLD", result["assurance_decision"])
                self.assertEqual(
                    ["ISSUANCE_EVALUATION_TIME_INVALID"],
                    result["error_codes"],
                )
                self.assertIsNone(result["normalized_environment"])

    def test_ws40_nul_missing_and_unreadable_artifacts_hold(self) -> None:
        for relative_path in ("\x00prefix", "middle\x00path", "suffix\x00"):
            with self.subTest(relative_path=repr(relative_path)):
                record = copy.deepcopy(self.part_control)
                record["artifacts"][0]["relative_path"] = relative_path
                result = validate_record(record, PART_FIXTURES)
                self.assert_part_hold(result, "ARTIFACT_PATH_INVALID")

        missing = copy.deepcopy(self.part_control)
        missing["artifacts"][0]["relative_path"] = "artifacts/not-present.txt"
        self.assert_part_hold(
            validate_record(missing, PART_FIXTURES),
            "ARTIFACT_HASH_MISMATCH",
        )

        with patch.object(Path, "stat", side_effect=PermissionError("synthetic denial")):
            unreadable = validate_record(copy.deepcopy(self.part_control), PART_FIXTURES)
        self.assert_part_hold(unreadable, "ARTIFACT_ACCESS_ERROR")

    def test_readiness_receipts_reject_optimistic_state_promotions(self) -> None:
        environment = json.loads(
            (READINESS_FIXTURES / "environment-hold-v1.json").read_text(
                encoding="utf-8"
            )
        )
        part = json.loads(
            (READINESS_FIXTURES / "part-contract-not-implemented-v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual([], list(self.validator.iter_errors(environment)))
        self.assertEqual([], list(self.validator.iter_errors(part)))

        environment["issuance_status"] = "ISSUABLE_CANDIDATE"
        environment["processing_status"] = "VALID"
        environment["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        environment["used_for_decision"] = True
        environment["blocker_codes"] = []

        part["readiness_status"] = "RECORD_VALIDATED"
        part["target_contract"]["implementation_status"] = "IMPLEMENTED"
        part["identity_status"] = "EXACT_MATCH"
        part["applicability_status"] = "APPLICABLE"
        part["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        part["used_for_decision"] = True
        part["blocker_codes"] = []

        environment_error_paths = error_paths(self.validator.iter_errors(environment))
        part_error_paths = error_paths(self.validator.iter_errors(part))
        self.assertTrue(
            {
                ("issuance_status",),
                ("assurance_decision",),
                ("used_for_decision",),
                ("blocker_codes",),
            }.issubset(environment_error_paths)
        )
        self.assertTrue(
            {
                ("readiness_status",),
                ("target_contract", "implementation_status"),
                ("assurance_decision",),
                ("used_for_decision",),
                ("blocker_codes",),
            }.issubset(part_error_paths)
        )


if __name__ == "__main__":
    unittest.main()
