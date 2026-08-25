from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import canonical_mission_case_result, synthesize_mission_case  # noqa: E402


HASH_A = "sha256:" + "a" * 64
HASH_B = "sha256:" + "b" * 64
HASH_C = "sha256:" + "c" * 64


def identity(**overrides):
    value = {
        "manufacturer": "Example Semi",
        "orderable_part_number": "EX-100-PKG",
        "package": "QFP-64",
        "process": "P1",
        "die": "DIE-A",
        "lot": "LOT-01",
    }
    value.update(overrides)
    return value


def event(event_type, locator, **values):
    value = {
        "event_type": event_type,
        "source_event_type": event_type,
        "locator": locator,
    }
    if event_type in {"SEL", "SEB", "SEGR"}:
        value.update(
            {
                "fluence": {"value": 1e10, "unit": "particles/cm2"},
                "sample_size": 3,
                "observed_events": 0,
            }
        )
    value.update(values)
    return value


def source(source_id, document_id, artifact_hash, claims):
    return {
        "source_id": source_id,
        "document_id": document_id,
        "mission_case_id": "mission-case-control",
        "data_class": "SYNTHETIC",
        "artifact_sha256": artifact_hash,
        "observed_artifact_sha256": artifact_hash,
        "locator": f"synthetic://{document_id}",
        "claims": claims,
    }


def claim(claim_id, events, tested_identity=None, conditions=None):
    return {
        "claim_id": claim_id,
        "component_id": "component-001",
        "tested_identity": tested_identity or identity(),
        "test_conditions": conditions or {},
        "event_evidence": events,
    }


class MissionCaseSynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(
            (ROOT / "simulation/config/synthetic-model.json").read_text(encoding="utf-8")
        )

    def setUp(self):
        self.case = {
            "contract_version": "MISSION_CASE_1.0.0",
            "mission_case_id": "mission-case-control",
            "data_class": "SYNTHETIC",
            "mission_conditions": {
                "mission_id": "mission-001",
                "duration": {"value": 1, "unit": "year"},
                "environment_tid": {"value": 10, "unit": "krad(Si)"},
                "particle_flux": {"value": 1000, "unit": "particles/cm2/s"},
                "shielding": {"value": 2, "unit": "mm_Al_equivalent"},
                "tid_design_factor": 2,
                "analysis_device_count": 2,
            },
            "approved_bom_targets": [
                {
                    "component_id": "component-001",
                    "approval_status": "APPROVED",
                    "identity": identity(),
                }
            ],
            "sources": [
                source(
                    "source-tid",
                    "document-tid",
                    HASH_A,
                    [
                        claim(
                            "claim-tid",
                            [
                                event(
                                    "TID",
                                    "synthetic://document-tid#page=3",
                                    tid_test_limit={"value": 25, "unit": "krad(Si)"},
                                )
                            ],
                        )
                    ],
                ),
                source(
                    "source-seu",
                    "document-seu",
                    HASH_B,
                    [
                        claim(
                            "claim-seu",
                            [
                                event(
                                    "SEU",
                                    "synthetic://document-seu#table=2",
                                    cross_section={"value": 1e-6, "unit": "cm2/device"},
                                )
                            ],
                        )
                    ],
                ),
                source(
                    "source-destructive",
                    "document-destructive",
                    HASH_C,
                    [
                        claim(
                            "claim-destructive",
                            [
                                event("SEL", "synthetic://document-destructive#sel"),
                                event("SEB", "synthetic://document-destructive#seb"),
                                event("SEGR", "synthetic://document-destructive#segr"),
                            ],
                        )
                    ],
                ),
            ],
        }

    def evaluate(self, case=None):
        return synthesize_mission_case(case or self.case, self.model)

    def test_synthetic_multi_document_control_is_deterministic_and_source_local(self):
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first, second)
        self.assertEqual(canonical_mission_case_result(first), canonical_mission_case_result(second))
        self.assertEqual("VALID", first["processing_status"])
        self.assertEqual("NOT_EVALUATED", first["engineering_gate"])
        self.assertEqual("HOLD", first["assurance_decision"])
        self.assertEqual("EXACT_MATCH", first["questions"]["exact_part_identity"]["status"])
        for comparison in first["identity_comparisons"]:
            self.assertEqual(
                {
                    "manufacturer": "EXACT_MATCH",
                    "orderable_part_number": "EXACT_MATCH",
                    "package": "EXACT_MATCH",
                    "process": "EXACT_MATCH",
                    "die": "EXACT_MATCH",
                    "lot": "EXACT_MATCH",
                },
                {row["field"]: row["status"] for row in comparison["fields"]},
            )
        self.assertEqual("NOT_EVALUATED", first["questions"]["mission_test_applicability"]["status"])
        self.assertEqual("COMPLETE", first["questions"]["event_coverage"]["status"])
        self.assertEqual({"PRESENT"}, {row["status"] for row in first["event_coverage"]})
        self.assertEqual(2, len(first["applicability_calculations"]))
        self.assertIn("SPECIES_TEST_CONDITION_MISSING", first["stable_codes"])
        tid = next(row for row in first["applicability_calculations"] if row["event_type"] == "TID")
        seu = next(row for row in first["applicability_calculations"] if row["event_type"] == "SEU")
        self.assertEqual("source-tid", tid["source_trace"]["source_id"])
        self.assertEqual("source-seu", seu["source_trace"]["source_id"])
        self.assertIn("SEL_APPLICABILITY_UNSUPPORTED", first["stable_codes"])

    def test_existing_tid_and_see_core_functions_are_reused(self):
        with patch("spectra_sim.mission_case.calculate_tid", wraps=__import__("spectra_sim.tid", fromlist=["calculate_tid"]).calculate_tid) as tid_call, patch(
            "spectra_sim.mission_case.calculate_see",
            wraps=__import__("spectra_sim.see", fromlist=["calculate_see"]).calculate_see,
        ) as see_call:
            self.evaluate()
        self.assertEqual(1, tid_call.call_count)
        self.assertEqual(1, see_call.call_count)

    def test_destructive_event_name_without_observation_is_not_coverage(self):
        attacked = copy.deepcopy(self.case)
        sel = attacked["sources"][2]["claims"][0]["event_evidence"][0]
        del sel["fluence"]
        result = self.evaluate(attacked)
        sel_coverage = next(
            row for row in result["event_coverage"] if row["event_type"] == "SEL"
        )
        self.assertEqual(result["processing_status"], "INVALID_INPUT")
        self.assertEqual(sel_coverage["status"], "INVALID")
        self.assertIn("SEL_OBSERVATION_INVALID", result["stable_codes"])

    def test_published_source_trace_does_not_promote_synthetic_core_output(self):
        case = copy.deepcopy(self.case)
        case["sources"][1]["data_class"] = "PUBLISHED"
        result = self.evaluate(case)
        self.assertEqual("VALID", result["processing_status"])
        self.assertEqual("SYNTHETIC", result["data_class"])
        seu = next(row for row in result["applicability_calculations"] if row["event_type"] == "SEU")
        self.assertEqual("PUBLISHED", seu["source_trace"]["data_class"])
        self.assertEqual("HOLD", result["assurance_decision"])

        promoted = copy.deepcopy(case)
        promoted["data_class"] = "PUBLISHED"
        rejected = self.evaluate(promoted)
        self.assertEqual("INVALID_INPUT", rejected["processing_status"])
        self.assertEqual("SYNTHETIC", rejected["data_class"])
        self.assertIn("MISSION_CASE_DATA_CLASS_INVALID", rejected["stable_codes"])

    def test_identity_missing_and_conflict_are_field_specific(self):
        missing = copy.deepcopy(self.case)
        del missing["sources"][0]["claims"][0]["tested_identity"]["lot"]
        missing_result = self.evaluate(missing)
        self.assertEqual("MISSING", missing_result["questions"]["exact_part_identity"]["status"])
        self.assertIn("IDENTITY_LOT_MISSING", missing_result["stable_codes"])

        conflict = copy.deepcopy(self.case)
        conflict["sources"][1]["claims"][0]["tested_identity"]["package"] = "BGA-64"
        conflict_result = self.evaluate(conflict)
        self.assertEqual("CONFLICT", conflict_result["questions"]["exact_part_identity"]["status"])
        self.assertIn("IDENTITY_PACKAGE_CONFLICT", conflict_result["stable_codes"])

    def test_caller_supplied_identity_or_applicability_status_is_not_trusted(self):
        for target, key, value in (
            ("tested_identity", "identity_status", "EXACT_MATCH"),
            ("test_conditions", "status", "APPLICABLE"),
        ):
            with self.subTest(target=target):
                attacked = copy.deepcopy(self.case)
                attacked["sources"][0]["claims"][0][target][key] = value
                result = self.evaluate(attacked)
                self.assertEqual("INVALID_INPUT", result["processing_status"])
                self.assertEqual("NOT_EVALUATED", result["questions"]["exact_part_identity"]["status"])
                self.assertIn("INPUT_FIELD_FORBIDDEN", result["stable_codes"])

    def test_mission_test_range_and_unsupported_condition_gaps_hold(self):
        attacked = copy.deepcopy(self.case)
        tid_claim = attacked["sources"][0]["claims"][0]
        tid_claim["event_evidence"][0]["tid_test_limit"]["value"] = 5
        tid_claim["test_conditions"] = {
            "species": "proton",
            "energy": {"value": 63, "unit": "MeV"},
            "let": {"value": 10, "unit": "MeV-cm2/mg"},
            "fluence": {"value": 1e7, "unit": "particles/cm2"},
            "temperature": {"value": 85, "unit": "degC"},
            "bias": "maximum rated",
        }
        result = self.evaluate(attacked)
        self.assertEqual("OUTSIDE_TESTED_RANGE", result["applicability_calculations"][0]["status"])
        for code in (
            "TID_TEST_RANGE_INSUFFICIENT",
            "SPECIES_COMPARISON_UNSUPPORTED",
            "ENERGY_COMPARISON_UNSUPPORTED",
            "LET_COMPARISON_UNSUPPORTED",
            "FLUENCE_COMPARISON_UNSUPPORTED",
            "TEMPERATURE_COMPARISON_UNSUPPORTED",
            "BIAS_COMPARISON_UNSUPPORTED",
        ):
            self.assertIn(code, result["stable_codes"])
        condition_statuses = {
            row["dimension"]: row["status"]
            for row in result["test_condition_comparisons"]
            if row["source_trace"]["claim_id"] == "claim-tid"
        }
        self.assertEqual(
            {
                "species": "UNSUPPORTED_BY_CURRENT_MODEL",
                "energy": "UNSUPPORTED_BY_CURRENT_MODEL",
                "let": "UNSUPPORTED_BY_CURRENT_MODEL",
                "fluence": "UNSUPPORTED_BY_CURRENT_MODEL",
                "temperature": "UNSUPPORTED_BY_CURRENT_MODEL",
                "bias": "UNSUPPORTED_BY_CURRENT_MODEL",
            },
            condition_statuses,
        )
        self.assertEqual("HOLD", result["assurance_decision"])

    def test_multiple_numeric_documents_remain_separate_and_are_not_summed_or_overwritten(self):
        attacked = copy.deepcopy(self.case)
        attacked["sources"].append(
            source(
                "source-tid-second",
                "document-tid-second",
                "sha256:" + "d" * 64,
                [
                    claim(
                        "claim-tid-second",
                        [
                            event(
                                "TID",
                                "synthetic://document-tid-second#page=9",
                                tid_test_limit={"value": 40, "unit": "krad(Si)"},
                            )
                        ],
                    )
                ],
            )
        )
        result = self.evaluate(attacked)
        tid_rows = [row for row in result["applicability_calculations"] if row["event_type"] == "TID"]
        self.assertEqual(2, len(tid_rows))
        self.assertEqual([25, 40], [row["tested_limit_krad_si"] for row in tid_rows])
        self.assertEqual(
            ["source-tid", "source-tid-second"],
            [row["source_trace"]["source_id"] for row in tid_rows],
        )

    def test_event_missing_and_seu_substitution_do_not_cover_destructive_see(self):
        missing = copy.deepcopy(self.case)
        missing["sources"][2]["claims"][0]["event_evidence"] = missing["sources"][2]["claims"][0]["event_evidence"][:1]
        missing_result = self.evaluate(missing)
        self.assertEqual("PARTIAL", missing_result["questions"]["event_coverage"]["status"])
        self.assertIn("SEB_EVIDENCE_MISSING", missing_result["stable_codes"])
        self.assertIn("SEGR_EVIDENCE_MISSING", missing_result["stable_codes"])

        substituted = copy.deepcopy(self.case)
        seb = substituted["sources"][2]["claims"][0]["event_evidence"][1]
        seb["source_event_type"] = "SEU"
        result = self.evaluate(substituted)
        seb_row = next(row for row in result["event_coverage"] if row["event_type"] == "SEB")
        self.assertEqual("INVALID", seb_row["status"])
        self.assertIn("EVENT_TYPE_SUBSTITUTION", result["stable_codes"])
        self.assertIn("SEB_COVERAGE_INVALID", result["stable_codes"])

    def test_damaged_source_hash_and_locator_fail_closed_with_trace(self):
        for field, value, code in (
            ("artifact_sha256", "sha256:broken", "SOURCE_ARTIFACT_HASH_INVALID"),
            ("observed_artifact_sha256", "sha256:" + "e" * 64, "SOURCE_ARTIFACT_HASH_MISMATCH"),
            ("locator", "", "SOURCE_LOCATOR_INVALID"),
        ):
            with self.subTest(field=field):
                attacked = copy.deepcopy(self.case)
                attacked["sources"][0][field] = value
                result = self.evaluate(attacked)
                self.assertEqual("INVALID_INPUT", result["processing_status"])
                self.assertEqual("NOT_EVALUATED", result["questions"]["exact_part_identity"]["status"])
                self.assertEqual("NOT_EVALUATED", result["questions"]["event_coverage"]["status"])
                self.assertIn(code, result["questions"]["event_coverage"]["blocker_codes"])
                self.assertIn(code, result["stable_codes"])
                tid = next(row for row in result["event_coverage"] if row["event_type"] == "TID")
                self.assertEqual("INVALID", tid["status"])
                self.assertEqual("source-tid", tid["source_trace"][0]["source_id"])

    def test_mixed_mission_case_ids_are_rejected(self):
        attacked = copy.deepcopy(self.case)
        attacked["sources"][1]["mission_case_id"] = "mission-case-attacker"
        result = self.evaluate(attacked)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertIn("MISSION_CASE_ID_MIXED", result["stable_codes"])
        seu = next(row for row in result["event_coverage"] if row["event_type"] == "SEU")
        self.assertEqual("INVALID", seu["status"])


if __name__ == "__main__":
    unittest.main()
