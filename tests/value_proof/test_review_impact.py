#!/usr/bin/env python3
"""Direct attacks and controls for REVIEW_IMPACT_1.0.0."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_value_proof import (  # noqa: E402
    CONTRACT_VERSION,
    classify_review_impact,
    source_sha256,
)


EVENTS = ("TID", "SEU", "SEL", "SEB", "SEGR")


def leaf(value: object, locator: str) -> dict[str, object]:
    return {
        "value": value,
        "source_locator": locator,
        "source_sha256": source_sha256(value, locator),
    }


def snapshot(side: str) -> dict:
    prefix = f"synthetic://mission-case/{side}"
    identity = {
        "manufacturer": "Example Semiconductor",
        "orderable_part_number": "EX-100-A",
        "package": "QFP-64",
        "process": "CMOS-65NM",
        "die": "DIE-A",
        "lot": "LOT-A",
    }
    return {
        "mission_orbit_context": {
            "orbit_regime": leaf("LEO", f"{prefix}#/mission/orbit/regime"),
            "altitude_km": leaf(550.0, f"{prefix}#/mission/orbit/altitude_km"),
            "inclination_deg": leaf(97.6, f"{prefix}#/mission/orbit/inclination_deg"),
        },
        "duration_days": leaf(365.0, f"{prefix}#/mission/duration_days"),
        "shielding_mm_al_equivalent": leaf(
            2.0, f"{prefix}#/shielding/mm_al_equivalent"
        ),
        "approved_component_identity": {
            field: leaf(value, f"{prefix}#/approved_bom/components/0/identity/{field}")
            for field, value in identity.items()
        },
        "event_coverage": {
            event: leaf(True, f"{prefix}#/evidence/event_coverage/{event}")
            for event in EVENTS
        },
    }


def control() -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "data_class": "SYNTHETIC",
        "baseline": snapshot("baseline"),
        "candidate": snapshot("candidate"),
        "requested_outcome": {
            "engineering_gate": "NOT_EVALUATED",
            "evaluation_status": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "suitability": "NOT_EVALUATED",
            "used_for_decision": False,
        },
    }


def replace(payload: dict, path: tuple[str, ...], value: object) -> None:
    target = payload
    for segment in path[:-1]:
        target = target[segment]
    locator = target[path[-1]]["source_locator"]
    target[path[-1]] = leaf(value, locator)


class ReviewImpactTests(unittest.TestCase):
    def assert_boundary(self, result: dict) -> None:
        self.assertEqual(result["data_class"], "SYNTHETIC")
        self.assertEqual(result["engineering_gate"], "NOT_EVALUATED")
        self.assertEqual(result["evaluation_status"], "NOT_EVALUATED")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertEqual(result["suitability"], "NOT_EVALUATED")
        self.assertFalse(result["used_for_decision"])

    def test_normal_synthetic_control_has_no_claimed_impact(self) -> None:
        result = classify_review_impact(control())
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["impact_status"], "NO_REVIEW_IMPACT_DETECTED")
        self.assertEqual(result["changed_fields"], [])
        self.assertEqual(result["blocker_codes"], [])
        self.assert_boundary(result)

    def test_orbit_change_closes_on_environment_contract_refresh(self) -> None:
        payload = control()
        replace(payload, ("candidate", "mission_orbit_context", "altitude_km"), 600.0)
        result = classify_review_impact(payload)
        self.assertEqual(
            result["blocker_codes"], ["ENVIRONMENT_CONTRACT_REFRESH_REQUIRED"]
        )
        self.assertEqual(result["affected_calculations"], [])
        self.assertEqual(
            result["changed_fields"][0]["field_pointer"],
            "mission_orbit_context.altitude_km",
        )
        self.assertEqual(
            result["changed_fields"][0]["candidate"]["source_locator"],
            payload["candidate"]["mission_orbit_context"]["altitude_km"]["source_locator"],
        )
        self.assertIn("does not derive environment", result["next_actions"][0]["instruction"])

    def test_duration_change_requires_existing_tid_and_seu_recalculation(self) -> None:
        payload = control()
        replace(payload, ("candidate", "duration_days"), 730.0)
        result = classify_review_impact(payload)
        self.assertEqual(result["affected_calculations"], ["SEU", "TID"])
        self.assertEqual(
            result["required_rechecks"],
            ["SEU_RECALCULATION_REQUIRED", "TID_RECALCULATION_REQUIRED"],
        )
        self.assertNotIn("required_tid", result)

    def test_shield_change_requires_existing_tid_recalculation_only(self) -> None:
        payload = control()
        replace(payload, ("candidate", "shielding_mm_al_equivalent"), 3.0)
        result = classify_review_impact(payload)
        self.assertEqual(result["affected_calculations"], ["TID"])
        self.assertEqual(result["required_rechecks"], ["TID_RECALCULATION_REQUIRED"])
        self.assertEqual(result["changed_fields"][0]["field_pointer"], "shielding_mm_al_equivalent")
        self.assertEqual(result["next_actions"][0]["action_code"], "RERUN_EXISTING_TID_CALCULATION")
        self.assertIn("not an input to the current SEE", result["next_actions"][0]["instruction"])

    def test_part_change_invalidates_exact_part_event_bindings(self) -> None:
        payload = control()
        replace(
            payload,
            ("candidate", "approved_component_identity", "orderable_part_number"),
            "EX-100-B",
        )
        result = classify_review_impact(payload)
        self.assertEqual(result["blocker_codes"], ["EXACT_PART_EVIDENCE_REVIEW_REQUIRED"])
        self.assertEqual([item["event"] for item in result["invalidated_evidence"]], list(EVENTS))
        self.assertIn("EXACT_PART_IDENTITY_REVIEW_REQUIRED", result["required_rechecks"])
        self.assertIn("EVENT_COVERAGE_REVIEW_REQUIRED", result["required_rechecks"])

    def test_compound_change_returns_all_review_impacts(self) -> None:
        payload = control()
        replace(payload, ("candidate", "mission_orbit_context", "inclination_deg"), 51.6)
        replace(payload, ("candidate", "duration_days"), 500.0)
        replace(payload, ("candidate", "shielding_mm_al_equivalent"), 4.0)
        replace(payload, ("candidate", "approved_component_identity", "package"), "BGA-100")
        replace(payload, ("candidate", "event_coverage", "SEGR"), False)
        result = classify_review_impact(payload)
        self.assertEqual(len(result["changed_fields"]), 5)
        self.assertEqual(result["affected_calculations"], ["SEU", "TID"])
        radiation_actions = [
            action for action in result["next_actions"]
            if action["action_code"].startswith("RERUN_EXISTING")
        ]
        self.assertEqual(
            [(action["action_code"], action["scope"]) for action in radiation_actions],
            [
                ("RERUN_EXISTING_TID_SEU_CALCULATIONS", ["duration_days"]),
                ("RERUN_EXISTING_TID_CALCULATION", ["shielding_mm_al_equivalent"]),
            ],
        )
        for blocker in (
            "ENVIRONMENT_CONTRACT_REFRESH_REQUIRED",
            "RADIATION_RECALCULATION_REQUIRED",
            "EXACT_PART_EVIDENCE_REVIEW_REQUIRED",
            "EVENT_COVERAGE_MISSING_SEGR",
        ):
            self.assertIn(blocker, result["blocker_codes"])
        self.assert_boundary(result)

    def test_each_missing_event_has_exact_location_evidence_and_action(self) -> None:
        expected_requirement = {
            "TID": "REVIEW_EVIDENCE_REQUIRED",
            "SEU": "REVIEW_EVIDENCE_REQUIRED",
            "SEL": "TEST_EVIDENCE_REQUIRED",
            "SEB": "TEST_EVIDENCE_REQUIRED",
            "SEGR": "TEST_EVIDENCE_REQUIRED",
        }
        for event in EVENTS:
            with self.subTest(event=event):
                payload = control()
                replace(payload, ("candidate", "event_coverage", event), False)
                result = classify_review_impact(payload)
                gap = result["evidence_gaps"][0]
                self.assertEqual(gap["event"], event)
                self.assertEqual(gap["field_pointer"], f"event_coverage.{event}")
                self.assertEqual(
                    gap["source_locator"],
                    payload["candidate"]["event_coverage"][event]["source_locator"],
                )
                self.assertEqual(gap["requirement_code"], expected_requirement[event])
                action = result["next_actions"][0]
                self.assertEqual(action["scope"]["event"], event)
                if event == "TID":
                    self.assertIn("do not infer that a new test is required", action["instruction"])
                elif event == "SEU":
                    self.assertIn("do not infer destructive-event coverage", action["instruction"])
                else:
                    self.assertIn("does not decide whether a new test must be run", action["instruction"])

    def test_tampered_source_hash_hides_values_and_locations(self) -> None:
        payload = control()
        payload["candidate"]["duration_days"]["source_sha256"] = "0" * 64
        result = classify_review_impact(payload)
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertEqual(result["impact_status"], "DATA_UNAVAILABLE")
        self.assertEqual(result["changed_fields"], [])
        self.assertEqual(result["problem_locations"][0]["field_pointer"], "duration_days")
        self.assertEqual(result["problem_locations"][0]["source_locator"], "UNAVAILABLE")
        self.assertEqual(result["blocker_codes"], ["SOURCE_PROVENANCE_INVALID"])
        self.assert_boundary(result)

    def test_tampered_locator_is_detected_by_locator_value_binding(self) -> None:
        payload = control()
        payload["candidate"]["event_coverage"]["SEL"]["source_locator"] += "/forged"
        result = classify_review_impact(payload)
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertEqual(
            result["problem_locations"][0]["field_pointer"], "event_coverage.SEL"
        )
        self.assertEqual(result["evidence_gaps"], [])

    def test_missing_locator_fails_closed_without_trusting_value(self) -> None:
        payload = control()
        payload["baseline"]["approved_component_identity"]["lot"]["source_locator"] = ""
        result = classify_review_impact(payload)
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertEqual(result["changed_fields"], [])
        self.assertIn("SOURCE_INTEGRITY_REVIEW_REQUIRED", result["required_rechecks"])

    def test_optimistic_pass_and_savings_claim_injection_is_rejected(self) -> None:
        for mutation in ("pass", "savings"):
            with self.subTest(mutation=mutation):
                payload = control()
                if mutation == "pass":
                    payload["requested_outcome"]["engineering_gate"] = "PASS"
                    payload["requested_outcome"]["assurance_decision"] = "PASS"
                else:
                    payload["requested_outcome"]["claimed_cost_savings_percent"] = 40
                    payload["claimed_time_savings_days"] = 12
                result = classify_review_impact(payload)
                self.assertEqual(result["processing_status"], "INVALID_INPUT")
                self.assertEqual(result["impact_status"], "DATA_UNAVAILABLE")
                self.assertIn(
                    "OPTIMISTIC_OUTCOME_FORBIDDEN" if mutation == "pass" else "INPUT_FIELD_FORBIDDEN_OR_MISSING",
                    result["error_codes"],
                )
                self.assertNotIn("claimed_cost_savings_percent", result)
                self.assertNotIn("claimed_time_savings_days", result)
                self.assert_boundary(result)

    def test_output_is_deterministic_and_input_is_not_mutated(self) -> None:
        payload = control()
        before = copy.deepcopy(payload)
        first = classify_review_impact(payload)
        second = classify_review_impact(payload)
        self.assertEqual(first, second)
        self.assertEqual(payload, before)
        self.assertEqual(len(first["receipt_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
