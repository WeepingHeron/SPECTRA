from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import canonical_runtime_json, evaluate_runtime_mitigation  # noqa: E402
from spectra_sim.contracts import load_contract_fixture  # noqa: E402


def mitigation(packet):
    return next(item for item in packet["inputs"] if item["kind"] == "MITIGATION")


def policy(packet):
    return next(item for item in packet["inputs"] if item["kind"] == "USER_POLICY")


def canonical_hash(value) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def rehash_policy(packet):
    item = policy(packet)
    scope = item["scope"]
    scope_projection = {
        "component_ids": sorted(scope["component_ids"]),
        "mission_ids": sorted(scope["mission_ids"]),
        "tenant_id": scope["tenant_id"],
    }
    scope_hash = canonical_hash(scope_projection)
    rules = copy.deepcopy(item["rules"])
    rules["required_destructive_modes"] = sorted(rules["required_destructive_modes"])
    content_hash = canonical_hash({
        "contract_version": item["contract_version"],
        "policy_id": item["policy_id"],
        "policy_version": item["policy_version"],
        "rules": rules,
        "scope_hash": scope_hash,
    })
    scope["scope_hash"] = scope_hash
    item["policy_content_hash"] = content_hash
    item["approval"]["approval_scope_hash"] = scope_hash
    item["approval"]["approval_target_hash"] = content_hash
    item["metadata"]["content_hash"] = content_hash
    item["metadata"]["calculation_run"]["output_hash"] = content_hash


class MitigationRuntimeCalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        valid = ROOT / "tests/schema/fixtures/valid"
        cls.packets = {
            "WATCHDOG": load_contract_fixture(valid / "synthetic-v2-hold.json"),
            "TMR": load_contract_fixture(valid / "synthetic-tmr-runtime-hold.json"),
            "SEL_PROTECTION": load_contract_fixture(valid / "synthetic-sel-runtime-hold.json"),
        }
        schema = json.loads(
            (ROOT / "simulation/schemas/mitigation-runtime-result.schema.json").read_text()
        )
        cls.common_schema = json.loads((ROOT / "schemas/common.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        registry = Registry().with_resource(
            cls.common_schema["$id"], Resource.from_contents(cls.common_schema)
        )
        cls.result_schema = schema
        cls.result_validator = Draft202012Validator(schema, registry=registry)

    def packet(self, method):
        return copy.deepcopy(self.packets[method])

    def evaluate(self, packet):
        result = evaluate_runtime_mitigation(packet)
        errors = sorted(self.result_validator.iter_errors(result), key=lambda error: list(error.path))
        self.assertEqual([], [error.message for error in errors])
        json.loads(canonical_runtime_json(result))
        return result

    def assert_safe(self, packet, code):
        result = self.evaluate(packet)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertIn(code, result["stable_error_codes"])
        self.assertEqual(sorted(result["stable_error_codes"]), result["stable_error_codes"])
        return result

    def test_processing_status_reuses_and_stays_within_common_enum(self):
        processing_schema = self.result_schema["properties"]["processing_status"]
        self.assertEqual(
            "https://spectra.local/schemas/common.schema.json#/$defs/processingStatus",
            processing_schema["$ref"],
        )
        common_statuses = set(self.common_schema["$defs"]["processingStatus"]["enum"])
        observed = {
            self.evaluate(self.packet(method))["processing_status"]
            for method in ("WATCHDOG", "TMR", "SEL_PROTECTION")
        }
        attacked = self.packet("TMR")
        mitigation(attacked)["design_parameters"]["voter_model"]["susceptible"] = True
        observed.add(self.evaluate(attacked)["processing_status"])
        self.assertTrue(observed.issubset(common_statuses))
        self.assertNotIn("NOT_EVALUATED", common_statuses)

    def test_watchdog_count_control_is_exact_zero_one_sixty(self):
        result = self.evaluate(self.packet("WATCHDOG"))
        self.assertEqual("VALID", result["processing_status"])
        self.assertEqual("SYNTHETIC", result["data_class"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertEqual({
            "method": "WATCHDOG",
            "true_target_event_count": 0.0,
            "true_positive_activation_count": 0.0,
            "false_positive_activation_count": 1.0,
            "reboot_count_total": 1.0,
            "downtime_total_seconds": 60.0,
        }, result["computed_projection"])
        self.assertTrue(result["declared_projection_comparison"]["matches"])

    def test_watchdog_rate_input_normalizes_to_same_count(self):
        packet = self.packet("WATCHDOG")
        model = mitigation(packet)["design_parameters"]["false_positive_model"]
        model.pop("activation_count")
        model["activation_rate_per_second"] = 1 / 3600
        result = self.evaluate(packet)
        self.assertEqual("VALID", result["processing_status"])
        self.assertAlmostEqual(1, result["normalized_counts"]["false_positive_activation_count"])
        self.assertEqual(60.0, result["computed_projection"]["downtime_total_seconds"])

    def test_tmr_exact_boundaries(self):
        for p, expected in ((0, 0), (0.1, 0.028), (1, 1)):
            with self.subTest(p=p):
                packet = self.packet("TMR")
                mitigation(packet)["design_parameters"]["replica_failure_probability"] = p
                mitigation(packet)["runtime_projection"]["system_failure_probability"] = expected
                result = self.evaluate(packet)
                self.assertEqual("VALID", result["processing_status"])
                self.assertEqual(expected, result["computed_projection"]["system_failure_probability"])

    def test_sel_true_false_cycles_and_phase_duration_are_exact(self):
        result = self.evaluate(self.packet("SEL_PROTECTION"))
        self.assertEqual("VALID", result["processing_status"])
        self.assertEqual(1.0, result["computed_projection"]["true_sel_activation_count"])
        self.assertEqual(1.0, result["computed_projection"]["false_trip_activation_count"])
        self.assertEqual(2.0, result["computed_projection"]["power_cycle_count_total"])
        self.assertEqual(32.0, result["computed_projection"]["downtime_total_seconds"])

    def test_same_input_is_byte_identical(self):
        packet = self.packet("WATCHDOG")
        first = self.evaluate(packet)
        second = self.evaluate(packet)
        self.assertEqual(first, second)
        self.assertEqual(canonical_runtime_json(first), canonical_runtime_json(second))

    def test_policy_thresholds_are_only_evaluated_when_present(self):
        packet = self.packet("WATCHDOG")
        no_threshold = self.evaluate(packet)["policy_evaluation"]["rule_results"]
        self.assertTrue(all(rule["outcome"] == "NOT_EVALUATED" for rule in no_threshold))
        rules = policy(packet)["rules"]
        rules["maximum_reboots"] = 0
        rules["maximum_downtime_seconds"] = 60
        rehash_policy(packet)
        evaluated = self.evaluate(packet)["policy_evaluation"]["rule_results"]
        outcomes = {rule["rule_id"]: rule["outcome"] for rule in evaluated}
        self.assertEqual("FAIL", outcomes["MAXIMUM_REBOOTS"])
        self.assertEqual("PASS", outcomes["MAXIMUM_DOWNTIME_SECONDS"])

    def test_approved_string_on_synthetic_policy_cannot_support(self):
        packet = self.packet("WATCHDOG")
        approval = policy(packet)["approval"]
        approval.update({
            "status": "APPROVED",
            "approved_by": "synthetic-approver",
            "approved_at": "2026-08-20T00:00:00Z",
            "valid_until": "2027-08-20T00:00:00Z",
        })
        result = self.evaluate(packet)
        self.assertEqual("VALID", result["processing_status"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertFalse(result["policy_evaluation"]["evidence_eligible"])
        self.assertIn("NON_EVIDENTIARY_POLICY", result["stable_error_codes"])

    def test_count_rate_conflict_and_omission_fail_closed(self):
        for mode in ("both", "neither"):
            with self.subTest(mode=mode):
                packet = self.packet("WATCHDOG")
                model = mitigation(packet)["design_parameters"]["target_event_model"]
                if mode == "both":
                    model["event_rate_per_second"] = 0
                else:
                    model.pop("event_count")
                self.assert_safe(packet, "ACTIVATION_COUNT_RATE_CONFLICT")

    def test_denominator_window_mismatch_fails_closed(self):
        packet = self.packet("WATCHDOG")
        mitigation(packet)["design_parameters"]["false_positive_model"]["denominator"]["scope"] = "DEVICE"
        self.assert_safe(packet, "RECOVERY_DENOMINATOR_WINDOW_MISMATCH")

    def test_action_fraction_sum_error_fails_closed(self):
        packet = self.packet("WATCHDOG")
        mitigation(packet)["design_parameters"]["false_positive_model"]["action_paths"][0]["fraction"] = 0.5
        self.assert_safe(packet, "ACTION_PATH_FRACTION_INVALID")

    def test_watchdog_false_totals_omission_is_detected(self):
        packet = self.packet("WATCHDOG")
        declared = mitigation(packet)["runtime_projection"]
        declared["reboot_count_total"] = 0
        declared["downtime_total_seconds"] = 0
        result = self.assert_safe(packet, "WATCHDOG_FALSE_POSITIVE_IGNORED")
        self.assertEqual(1.0, result["computed_projection"]["reboot_count_total"])
        self.assertEqual(60.0, result["computed_projection"]["downtime_total_seconds"])

    def test_watchdog_detection_latency_double_count_is_detected(self):
        packet = self.packet("WATCHDOG")
        parameters = mitigation(packet)["design_parameters"]
        parameters["target_event_model"]["event_count"] = 1
        declared = mitigation(packet)["runtime_projection"]
        declared.update({
            "true_target_event_count": 1,
            "true_positive_activation_count": 1,
            "false_positive_activation_count": 1,
            "reboot_count_total": 2,
            "downtime_total_seconds": 92,
        })
        result = self.assert_safe(packet, "WATCHDOG_DETECTION_LATENCY_DOUBLE_COUNTED")
        self.assertEqual(91.0, result["computed_projection"]["downtime_total_seconds"])

    def test_tmr_voter_and_common_mode_ineligibility_do_not_execute_formula(self):
        attacks = (
            ("voter", lambda params: params["voter_model"].update({"susceptible": True}), "TMR_VOTER_SUSCEPTIBLE"),
            ("common", lambda params: params["common_mode_model"].update({"probability": 0.01}), "TMR_COMMON_MODE_NONZERO"),
        )
        for label, mutate, code in attacks:
            with self.subTest(label=label):
                packet = self.packet("TMR")
                mutate(mitigation(packet)["design_parameters"])
                result = self.assert_safe(packet, code)
                self.assertIsNone(result["computed_projection"])

    def test_tmr_independence_and_repair_ineligibility_do_not_execute_formula(self):
        attacks = (
            ("independence", lambda params: params.update({"independence_verified": False}), "TMR_INDEPENDENCE_UNVERIFIED"),
            ("repair", lambda params: params["repair_model"].update({"repair_within_window": True}), "TMR_REPAIR_WINDOW_MISMATCH"),
        )
        for label, mutate, code in attacks:
            with self.subTest(label=label):
                packet = self.packet("TMR")
                mutate(mitigation(packet)["design_parameters"])
                result = self.assert_safe(packet, code)
                self.assertIsNone(result["computed_projection"])

    def test_tmr_output_semantic_change_does_not_execute_formula(self):
        packet = self.packet("TMR")
        mitigation(packet)["design_parameters"]["output_semantic"] = "availability"
        result = self.assert_safe(packet, "TMR_OUTPUT_SEMANTIC_MISMATCH")
        self.assertIsNone(result["computed_projection"])

    def test_sel_false_trip_and_required_evidence_gaps_do_not_execute(self):
        attacks = (
            ("false-trip", lambda params: params.pop("false_trip_model"), "SEL_FALSE_TRIP_MODEL_MISSING"),
            ("prompt", lambda params: params.pop("prompt_failure_evidence_id"), "SEL_PROTECTION_NOT_VALIDATED"),
            ("latent", lambda params: params.pop("latent_damage_evidence_id"), "SEL_PROTECTION_NOT_VALIDATED"),
            ("post-test", lambda params: params.pop("post_test_electrical_evidence_id"), "SEL_PROTECTION_NOT_VALIDATED"),
        )
        for label, mutate, code in attacks:
            with self.subTest(label=label):
                packet = self.packet("SEL_PROTECTION")
                mutate(mitigation(packet)["design_parameters"])
                result = self.assert_safe(packet, code)
                self.assertIsNone(result["computed_projection"])

    def test_sel_duration_double_count_is_detected(self):
        packet = self.packet("SEL_PROTECTION")
        mitigation(packet)["runtime_projection"]["downtime_total_seconds"] = 64
        result = self.assert_safe(packet, "SEL_DURATION_DOUBLE_COUNTED")
        self.assertEqual(32.0, result["computed_projection"]["downtime_total_seconds"])

    def test_sel_action_duration_and_destructive_mode_substitution_fail_closed(self):
        duration_packet = self.packet("SEL_PROTECTION")
        mitigation(duration_packet)["design_parameters"]["true_sel_model"]["action_paths"][0]["duration_seconds"] = 16
        self.assert_safe(duration_packet, "SEL_DURATION_SEMANTIC_CONFLICT")
        mode_packet = self.packet("SEL_PROTECTION")
        mitigation(mode_packet)["target_failure_modes"] = ["SEB"]
        self.assert_safe(mode_packet, "MITIGATION_METHOD_MODE_MISMATCH")

    def test_runtime_version_equation_and_evidence_link_tampering_fail_closed(self):
        attacks = (
            ("version", lambda item: item.update({"runtime_contract_version": "9.0.0"}), "MITIGATION_RUNTIME_CONTRACT_MISSING"),
            ("equation", lambda item: item["effect_model"].update({"equation_id": "UNBOUND"}), "MITIGATION_EQUATION_ID_MISMATCH"),
            ("evidence", lambda item: item.update({"verification_evidence_ids": ["wrong"]}), "MITIGATION_EVIDENCE_LINK_MISMATCH"),
        )
        for label, mutate, code in attacks:
            with self.subTest(label=label):
                packet = self.packet("WATCHDOG")
                mutate(mitigation(packet))
                self.assert_safe(packet, code)

    def test_declared_projection_tampering_is_detected_for_all_methods(self):
        fields = {
            "WATCHDOG": "downtime_total_seconds",
            "TMR": "system_failure_probability",
            "SEL_PROTECTION": "downtime_total_seconds",
        }
        codes = {
            "WATCHDOG": "WATCHDOG_RUNTIME_PROJECTION_MISMATCH",
            "TMR": "TMR_RUNTIME_PROJECTION_MISMATCH",
            "SEL_PROTECTION": "SEL_RUNTIME_PROJECTION_MISMATCH",
        }
        for method, field in fields.items():
            with self.subTest(method=method):
                packet = self.packet(method)
                mitigation(packet)["runtime_projection"][field] += 0.25
                result = self.assert_safe(packet, codes[method])
                self.assertIn(field, result["declared_projection_comparison"]["mismatched_fields"])

    def test_policy_content_scope_history_expiry_and_revocation_tampering(self):
        attacks = (
            ("content", lambda item: item["rules"].update({"maximum_reboots": 5}), "POLICY_CONTENT_HASH_MISMATCH"),
            ("scope", lambda item: item["scope"]["mission_ids"].append("mission-attack"), "POLICY_SCOPE_HASH_MISMATCH"),
            ("history", lambda item: item["immutable_history_ref"].update({"head_hash": "sha256:" + "0" * 64}), "POLICY_HISTORY_MISMATCH"),
            ("expiry", lambda item: item["approval"].update({"valid_until": "2026-08-19T00:00:00Z"}), "POLICY_EXPIRED"),
            ("revocation", lambda item: item["approval"].update({"status": "REVOKED", "revoked_at": "2026-08-20T00:00:00Z", "revocation_reason": "Synthetic attack"}), "POLICY_REVOKED"),
        )
        for label, mutate, code in attacks:
            with self.subTest(label=label):
                packet = self.packet("WATCHDOG")
                mutate(policy(packet))
                self.assert_safe(packet, code)

    def test_malformed_nonfinite_and_negative_inputs_never_raise(self):
        malformed = self.packet("WATCHDOG")
        mitigation(malformed)["design_parameters"] = []
        self.assert_safe(malformed, "MALFORMED_MITIGATION_PARAMETERS")
        list_packet = self.packet("WATCHDOG")
        list_packet["inputs"] = {}
        self.assert_safe(list_packet, "PACKET_SCHEMA_INVALID")
        for label, value, code in (
            ("nan", float("nan"), "NON_FINITE_NUMERIC_INPUT"),
            ("inf", float("inf"), "NON_FINITE_NUMERIC_INPUT"),
            ("negative-inf", float("-inf"), "NON_FINITE_NUMERIC_INPUT"),
            ("negative", -1, "PACKET_SCHEMA_INVALID"),
        ):
            with self.subTest(label=label):
                packet = self.packet("WATCHDOG")
                mitigation(packet)["design_parameters"]["detection_latency_seconds"] = value
                self.assert_safe(packet, code)

    def test_cli_control_and_nonfinite_attack_are_machine_readable(self):
        control = subprocess.run(
            [sys.executable, str(ROOT / "simulation/run_mitigation_runtime.py"), "--summary"],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(0, control.returncode, control.stderr)
        self.assertEqual("HOLD", json.loads(control.stdout)["assurance_decision"])
        packet = self.packet("WATCHDOG")
        mitigation(packet)["design_parameters"]["detection_latency_seconds"] = float("nan")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "non-finite.json"
            path.write_text(json.dumps(packet), encoding="utf-8")
            attack = subprocess.run(
                [sys.executable, str(ROOT / "simulation/run_mitigation_runtime.py"), str(path)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
        self.assertEqual(2, attack.returncode)
        self.assertNotIn("Traceback", attack.stderr + attack.stdout)
        result = json.loads(attack.stdout)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertIn("NON_FINITE_NUMERIC_INPUT", result["stable_error_codes"])


if __name__ == "__main__":
    unittest.main()
