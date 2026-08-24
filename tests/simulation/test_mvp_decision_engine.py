from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import MvpDecisionError, canonical_result_json, run_mvp_decision  # noqa: E402
from spectra_sim.contracts import packet_contract_errors  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class MvpDecisionEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load(ROOT / "simulation/fixtures/mvp-ecc-policy-v2.json")
        cls.model = load(ROOT / "simulation/config/synthetic-model.json")

    def result(self, case=None):
        return run_mvp_decision(case or self.case, self.model)

    def rule(self, scenario, rule_id):
        return next(
            item["outcome"] for item in scenario["rule_results"]
            if item["rule_id"] == rule_id
        )

    def test_same_normalized_input_is_canonically_identical(self):
        first = self.result()
        second = self.result()
        self.assertEqual(first, second)
        self.assertEqual(canonical_result_json(first), canonical_result_json(second))
        self.assertEqual(first["input_hash"], second["input_hash"])
        self.assertEqual(first["output_hash"], second["output_hash"])

    def test_ecc_off_on_uses_explicit_transition_counts(self):
        result = self.result()
        baseline = result["baseline"]
        variant = result["variant"]
        self.assertAlmostEqual(0.063072, baseline["metrics"]["raw_seu"]["value"])
        self.assertAlmostEqual(0.063072, baseline["metrics"]["residual_logical_errors"]["value"])
        self.assertAlmostEqual(0.05, variant["metrics"]["corrected"]["value"])
        self.assertAlmostEqual(0.01, variant["metrics"]["detected_uncorrectable"]["value"])
        self.assertAlmostEqual(0.003072, variant["metrics"]["silent_uncorrected"]["value"])
        self.assertAlmostEqual(0.013072, variant["metrics"]["residual_logical_errors"]["value"])
        self.assertEqual("NOT_EVALUATED", self.rule(baseline, "ECC_TRANSITION_V2"))
        self.assertEqual("PASS", self.rule(variant, "ECC_TRANSITION_V2"))

    def test_analysis_device_count_is_separate_from_bom_identity(self):
        attacked = copy.deepcopy(self.case)
        attacked["analysis_device_count"] = 1
        attacked["ecc_fault_distribution"]["patterns"] = [
            {
                "multiplicity_bits": 1,
                "incident_events": 0.031536,
                "transition": {
                    "corrected": 1,
                    "detected_uncorrectable": 0,
                    "silent_uncorrected": 0,
                },
            }
        ]
        result = self.result(attacked)
        self.assertAlmostEqual(0.031536, result["baseline"]["metrics"]["raw_seu"]["value"])
        bom = next(
            item for item in result["baseline"]["evidence_packet"]["inputs"]
            if item["kind"] == "BOM"
        )
        self.assertNotIn("quantity", bom["components"][0])

    def test_draft_and_approved_policy_states_are_deterministic(self):
        result = self.result()
        baseline = result["baseline"]
        variant = result["variant"]
        self.assertEqual("DRAFT", baseline["policy_approval_status"])
        self.assertEqual("FAIL", self.rule(baseline, "POLICY_APPROVAL_STATE_V2"))
        self.assertEqual("FAIL", self.rule(baseline, "RESIDUAL_SEU_THRESHOLD_V2"))
        self.assertEqual("APPROVED", variant["policy_approval_status"])
        self.assertEqual("PASS", self.rule(variant, "POLICY_APPROVAL_STATE_V2"))
        self.assertEqual("PASS", self.rule(variant, "RESIDUAL_SEU_THRESHOLD_V2"))

    def test_synthetic_and_missing_real_dependencies_remain_not_evaluated_hold(self):
        result = self.result()
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        for scenario in (result["baseline"], result["variant"]):
            self.assertEqual("NOT_EVALUATED", scenario["engineering_gate"])
            self.assertEqual("HOLD", scenario["assurance_decision"])
            self.assertEqual("NOT_EVALUATED", self.rule(scenario, "EVIDENCE_ELIGIBILITY_V2"))
            gap_codes = {gap["gap_code"] for gap in scenario["evidence_gaps"]}
            self.assertTrue({"STAGE3_INPUT_UNAVAILABLE", "STAGE4_INPUT_UNAVAILABLE", "SYNTHETIC_ONLY"}.issubset(gap_codes))

    def test_generated_evidence_packets_pass_schema_and_semantic_gate(self):
        result = self.result()
        for scenario in (result["baseline"], result["variant"]):
            self.assertEqual([], packet_contract_errors(scenario["evidence_packet"]))
            self.assertEqual("1.1.0", scenario["evidence_packet"]["schema_version"])

    def test_change_impact_captures_inputs_outputs_decisions_and_invalidations(self):
        impact = self.result()["change_impact"]
        input_fields = {item["field"] for item in impact["input_changes"]}
        output_fields = {item["field"] for item in impact["output_changes"]}
        decision_fields = {item["field"] for item in impact["decision_changes"]}
        reasons = {item["reason_code"] for item in impact["invalidated_evidence"]}
        self.assertEqual({"ecc_enabled", "mitigation_id", "policy.approval.status"}, input_fields)
        self.assertIn("residual_logical_errors", output_fields)
        self.assertIn("POLICY_APPROVAL_STATE_V2", decision_fields)
        self.assertEqual({"MITIGATION_INPUT_CHANGED", "POLICY_VERSION_CHANGED"}, reasons)
        self.assertEqual("HOLD", next(item["after"] for item in impact["decision_changes"] if item["field"] == "assurance_decision"))

    def test_ecc_cannot_substitute_for_missing_destructive_mode(self):
        attacked = copy.deepcopy(self.case)
        attacked["variant"]["policy"]["rules"]["required_destructive_modes"] = ["SEL", "SEB"]
        with self.assertRaises(MvpDecisionError) as raised:
            self.result(attacked)
        self.assertEqual("SCENARIO_PACKET_CONTRACT_INVALID", raised.exception.code)
        self.assertIn("DESTRUCTIVE_SEE_MODE_MISSING", raised.exception.message)

    def test_generic_factor_and_distribution_mismatch_fail_closed(self):
        factor_attack = copy.deepcopy(self.case)
        factor_attack["variant"]["mitigation"]["effectiveness_factor"] = 0.1
        with self.assertRaises(MvpDecisionError) as factor_error:
            self.result(factor_attack)
        self.assertEqual("MVP_INPUT_SCHEMA_INVALID", factor_error.exception.code)
        distribution_attack = copy.deepcopy(self.case)
        distribution_attack["ecc_fault_distribution"]["patterns"][0]["incident_events"] = 0.04
        with self.assertRaises(MvpDecisionError) as distribution_error:
            self.result(distribution_attack)
        self.assertEqual("ECC_FAULT_DISTRIBUTION_MISMATCH", distribution_error.exception.code)

    def test_non_finite_numeric_inputs_fail_at_direct_engine_boundary(self):
        for label, value in (
            ("NaN", float("nan")),
            ("Infinity", float("inf")),
            ("-Infinity", float("-inf")),
        ):
            with self.subTest(value=label):
                attacked = copy.deepcopy(self.case)
                attacked["particle_flux"]["value"] = value
                with self.assertRaises(MvpDecisionError) as raised:
                    self.result(attacked)
                self.assertEqual("NON_FINITE_NUMERIC_INPUT", raised.exception.code)
                self.assertIn("/particle_flux/value", raised.exception.message)

    def test_lower_level_tid_and_see_value_errors_are_stable_engine_errors(self):
        for target, expected_code in (
            ("spectra_sim.mvp_engine.calculate_tid", "TID_CALCULATION_INPUT_INVALID"),
            ("spectra_sim.mvp_engine.calculate_see", "SEE_CALCULATION_INPUT_INVALID"),
        ):
            with self.subTest(target=target), patch(target, side_effect=ValueError("rejected")):
                with self.assertRaises(MvpDecisionError) as raised:
                    self.result()
                self.assertEqual(expected_code, raised.exception.code)
                self.assertIn("rejected", raised.exception.message)

    def test_cli_non_finite_numeric_inputs_return_machine_readable_hold(self):
        for label, value in (
            ("NaN", float("nan")),
            ("Infinity", float("inf")),
            ("-Infinity", float("-inf")),
        ):
            with self.subTest(value=label), tempfile.TemporaryDirectory() as directory:
                attacked = copy.deepcopy(self.case)
                attacked["particle_flux"]["value"] = value
                path = Path(directory) / "non-finite.json"
                path.write_text(json.dumps(attacked), encoding="utf-8")
                completed = subprocess.run(
                    [sys.executable, str(ROOT / "simulation/run_mvp_decision.py"), str(path)],
                    cwd=ROOT, check=False, capture_output=True, text=True,
                )
                self.assertEqual(2, completed.returncode)
                self.assertEqual("", completed.stdout)
                self.assertNotIn("Traceback", completed.stderr)
                failure = json.loads(completed.stderr)
                self.assertEqual("NON_FINITE_NUMERIC_INPUT", failure["error_code"])
                self.assertEqual("INVALID_INPUT", failure["processing_status"])
                self.assertEqual("NOT_EVALUATED", failure["engineering_gate"])
                self.assertEqual("HOLD", failure["assurance_decision"])

    def test_cli_exports_summary_and_contract_valid_variant_packet(self):
        summary = subprocess.run(
            [sys.executable, str(ROOT / "simulation/run_mvp_decision.py"), "--summary"],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(0, summary.returncode, summary.stderr)
        summary_json = json.loads(summary.stdout)
        self.assertEqual("HOLD", summary_json["variant"]["assurance"])
        packet_export = subprocess.run(
            [sys.executable, str(ROOT / "simulation/run_mvp_decision.py"), "--evidence-packet", "variant"],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(0, packet_export.returncode, packet_export.stderr)
        self.assertEqual([], packet_contract_errors(json.loads(packet_export.stdout)))


if __name__ == "__main__":
    unittest.main()
