from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests/schema"))

from spectra_sim import SimulationOptions, run_simulation  # noqa: E402
import validate_contracts as contracts  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class SyntheticVerticalSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = load(ROOT / "tests/schema/fixtures/valid/synthetic-hold.json")
        cls.model = load(ROOT / "simulation/config/synthetic-model.json")
        schema_docs = [load(path) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
        cls.result_schema = load(ROOT / "simulation/schemas/simulation-result.schema.json")
        Draft202012Validator.check_schema(cls.result_schema)
        resources = [(schema["$id"], Resource.from_contents(schema)) for schema in schema_docs]
        resources.append((cls.result_schema["$id"], Resource.from_contents(cls.result_schema)))
        cls.registry = Registry().with_resources(resources)

    def assert_result_schema(self, result):
        errors = list(Draft202012Validator(
            self.result_schema, registry=self.registry, format_checker=FormatChecker()
        ).iter_errors(result))
        self.assertEqual([], [error.message for error in errors])

    def assert_packet_contract(self, result):
        packet = result["evidence_packet"]
        self.assertIsNotNone(packet)
        schema_docs = [load(path) for path in sorted((ROOT / "schemas").glob("*.schema.json"))]
        registry = contracts.build_registry(schema_docs)
        packet_schema = load(ROOT / "schemas/evidence-packet.schema.json")
        self.assertEqual([], contracts.schema_errors(packet, packet_schema, registry))
        self.assertEqual(set(), contracts.semantic_codes(packet))

    def test_base_run_is_deterministic_synthetic_hold(self):
        first = run_simulation(self.packet, self.model)
        second = run_simulation(self.packet, self.model)
        self.assertEqual(first, second)
        self.assertEqual("SYNTHETIC", first["data_class"])
        self.assertEqual("HOLD", first["assurance_decision"])
        self.assertEqual("PASS", first["engineering_gate"])
        self.assertAlmostEqual(6.0, first["metrics"]["shielded_tid"]["value"])
        self.assertAlmostEqual(12.0, first["metrics"]["required_tid"]["value"])
        self.assertAlmostEqual(0.063072, first["metrics"]["raw_seu"]["value"])
        self.assertAlmostEqual(0.0063072, first["metrics"]["residual_seu"]["value"])
        self.assert_result_schema(first)
        self.assert_packet_contract(first)

    def test_more_shielding_reduces_synthetic_tid(self):
        values = [
            run_simulation(self.packet, self.model, SimulationOptions(shielding_mm=mm))["metrics"]["shielded_tid"]["value"]
            for mm in (1, 2, 3, 4)
        ]
        self.assertEqual(values, sorted(values, reverse=True))
        self.assertEqual(4, len(set(values)))
        self.assertEqual([8.0, 6.0, 4.5, 3.5], values)

    def test_duration_scales_tid_and_see(self):
        short = run_simulation(self.packet, self.model, SimulationOptions(duration_value=0.5))
        long = run_simulation(self.packet, self.model, SimulationOptions(duration_value=2.0))
        self.assertAlmostEqual(4.0, long["metrics"]["required_tid"]["value"] / short["metrics"]["required_tid"]["value"])
        self.assertAlmostEqual(4.0, long["metrics"]["raw_seu"]["value"] / short["metrics"]["raw_seu"]["value"])
        self.assertAlmostEqual(6.0, short["metrics"]["required_tid"]["value"])
        self.assertAlmostEqual(24.0, long["metrics"]["required_tid"]["value"])
        self.assertAlmostEqual(0.031536, short["metrics"]["raw_seu"]["value"])
        self.assertAlmostEqual(0.126144, long["metrics"]["raw_seu"]["value"])
        self.assert_packet_contract(short)
        self.assert_packet_contract(long)

    def test_ecc_reduces_residual_without_changing_raw_events(self):
        enabled = run_simulation(self.packet, self.model, SimulationOptions(ecc_enabled=True))
        disabled = run_simulation(self.packet, self.model, SimulationOptions(ecc_enabled=False))
        self.assertEqual(enabled["metrics"]["raw_seu"]["value"], disabled["metrics"]["raw_seu"]["value"])
        self.assertLess(enabled["metrics"]["residual_seu"]["value"], disabled["metrics"]["residual_seu"]["value"])
        self.assertAlmostEqual(
            enabled["metrics"]["raw_seu"]["value"] * 0.1,
            enabled["metrics"]["residual_seu"]["value"],
        )

    def test_missing_destructive_see_never_supports(self):
        packet = copy.deepcopy(self.packet)
        evidence = next(item for item in packet["inputs"] if item["kind"] == "PART_TEST_EVIDENCE")
        evidence["evidence_types"] = ["TID", "SEU"]
        result = run_simulation(packet, self.model)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertIsNone(result["evidence_packet"])
        self.assertIn("DESTRUCTIVE_SEE_EVIDENCE_MISSING", result["evidence_gaps"][0]["description"])

    def test_missing_cross_section_is_invalid_input_hold(self):
        packet = copy.deepcopy(self.packet)
        evidence = next(item for item in packet["inputs"] if item["kind"] == "PART_TEST_EVIDENCE")
        del evidence["cross_section"]
        result = run_simulation(packet, self.model)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertIsNone(result["evidence_packet"])
        self.assert_result_schema(result)

    def test_severely_malformed_packet_fails_closed(self):
        result = run_simulation({"schema_version": "1.0.0"}, self.model)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertIsNone(result["evidence_packet"])
        self.assert_result_schema(result)

    def test_unapproved_policy_fails_engineering_and_remains_hold(self):
        packet = copy.deepcopy(self.packet)
        policy = next(item for item in packet["inputs"] if item["kind"] == "USER_POLICY")
        policy["approval_status"] = "PENDING_APPROVAL"
        policy.pop("approved_by")
        policy.pop("approved_at")
        result = run_simulation(packet, self.model)
        outcomes = {item["rule_id"]: item["outcome"] for item in result["rule_results"]}
        self.assertEqual("FAIL", outcomes["POLICY_APPROVAL_V1"])
        self.assertEqual("FAIL", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])

    def test_all_generated_metrics_are_explicitly_synthetic(self):
        result = run_simulation(self.packet, self.model)
        for metric in result["metrics"].values():
            self.assertEqual("SYNTHETIC", metric["metadata"]["data_class"])
            self.assertIn("calculation_run", metric["metadata"])

    def test_tid_limit_and_user_seu_limit_fail_closed(self):
        packet = copy.deepcopy(self.packet)
        evidence = next(item for item in packet["inputs"] if item["kind"] == "PART_TEST_EVIDENCE")
        evidence["tid_test_limit"]["value"] = 5
        tid_result = run_simulation(packet, self.model)
        self.assertEqual("INVALID_INPUT", tid_result["processing_status"])
        self.assertEqual("HOLD", tid_result["assurance_decision"])
        self.assertIn("TEST_RANGE_EXCEEDED", tid_result["evidence_gaps"][0]["description"])
        seu_result = run_simulation(
            self.packet, self.model, SimulationOptions(maximum_residual_seu=0.000001)
        )
        seu_outcomes = {item["rule_id"]: item["outcome"] for item in seu_result["rule_results"]}
        self.assertEqual("FAIL", seu_outcomes["SEU_POLICY_V1"])
        self.assertEqual("HOLD", seu_result["assurance_decision"])

    def test_out_of_scope_does_not_interpolate_or_support(self):
        result = run_simulation(self.packet, self.model, SimulationOptions(shielding_mm=5))
        self.assertEqual("OUT_OF_MODEL_SCOPE", result["processing_status"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assert_result_schema(result)
        self.assert_packet_contract(result)

    def test_invalid_unit_returns_hold_without_evidence_packet(self):
        result = run_simulation(
            self.packet, self.model, SimulationOptions(duration_value=1, duration_unit="fortnight")
        )
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertIsNone(result["evidence_packet"])
        self.assert_result_schema(result)

    def test_synthetic_result_can_never_claim_support(self):
        scenarios = [
            SimulationOptions(),
            SimulationOptions(shielding_mm=1),
            SimulationOptions(shielding_mm=4),
            SimulationOptions(ecc_enabled=False),
            SimulationOptions(tid_design_factor=3),
        ]
        for options in scenarios:
            result = run_simulation(self.packet, self.model, options)
            self.assertEqual("SYNTHETIC", result["data_class"])
            self.assertEqual("HOLD", result["assurance_decision"])

    def test_semantically_corrupted_packet_is_rejected_before_calculation(self):
        packet = copy.deepcopy(self.packet)
        packet["trace"].append(copy.deepcopy(packet["trace"][0]))
        result = run_simulation(packet, self.model)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertIsNone(result["evidence_packet"])
        self.assertIn("DUPLICATE_TRACE_ID", result["evidence_gaps"][0]["description"])
        self.assert_result_schema(result)

    def test_negative_numeric_inputs_fail_closed(self):
        negative_duration = run_simulation(
            self.packet, self.model, SimulationOptions(duration_value=-1)
        )
        self.assertEqual("INVALID_INPUT", negative_duration["processing_status"])
        self.assertEqual("HOLD", negative_duration["assurance_decision"])
        packet = copy.deepcopy(self.packet)
        environment = next(item for item in packet["inputs"] if item["kind"] == "RADIATION_ENVIRONMENT")
        environment["particle_flux"]["value"] = -1
        negative_flux = run_simulation(packet, self.model)
        self.assertEqual("INVALID_INPUT", negative_flux["processing_status"])
        self.assertEqual("HOLD", negative_flux["assurance_decision"])
        self.assertEqual("NOT_EVALUATED", negative_flux["engineering_gate"])
        nonfinite_limit = run_simulation(
            self.packet, self.model, SimulationOptions(maximum_residual_seu=float("inf"))
        )
        self.assertEqual("INVALID_INPUT", nonfinite_limit["processing_status"])
        self.assertEqual("HOLD", nonfinite_limit["assurance_decision"])

    def test_duplicate_required_input_fails_without_exception(self):
        packet = copy.deepcopy(self.packet)
        packet["inputs"].append(copy.deepcopy(next(
            item for item in packet["inputs"] if item["kind"] == "MISSION"
        )))
        result = run_simulation(packet, self.model)
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assert_result_schema(result)

    def test_reordered_contract_inputs_produce_valid_dynamic_traces(self):
        packet = copy.deepcopy(self.packet)
        old_inputs = packet["inputs"]
        new_inputs = list(reversed(old_inputs))
        old_to_new = {old_index: len(old_inputs) - 1 - old_index for old_index in range(len(old_inputs))}
        packet["inputs"] = new_inputs
        for trace in packet["trace"]:
            for field in ("input_pointer", "origin_pointer"):
                parts = trace[field].split("/")
                parts[2] = str(old_to_new[int(parts[2])])
                trace[field] = "/".join(parts)
        result = run_simulation(packet, self.model)
        self.assertEqual("VALID", result["processing_status"])
        self.assertEqual("PASS", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assert_packet_contract(result)
        evidence_index = next(
            index for index, item in enumerate(result["evidence_packet"]["inputs"])
            if item["kind"] == "PART_TEST_EVIDENCE"
        )
        residual_trace = next(
            trace for trace in result["evidence_packet"]["trace"]
            if trace["trace_id"] == "trace-seu-residual"
        )
        self.assertEqual(f"/inputs/{evidence_index}/cross_section", residual_trace["input_pointer"])

    def test_tampered_synthetic_model_fails_closed(self):
        model = copy.deepcopy(self.model)
        model["data_class"] = "PUBLISHED"
        result = run_simulation(self.packet, model)
        self.assertEqual("MODEL_FAILURE", result["processing_status"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assert_result_schema(result)
        self.assert_packet_contract(result)

    def test_engineering_pass_support_escalation_is_rejected(self):
        result = run_simulation(self.packet, self.model)
        self.assertEqual("PASS", result["engineering_gate"])
        attacked = copy.deepcopy(result)
        attacked["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        attacked["evidence_packet"]["decision"]["assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        result_errors = list(Draft202012Validator(
            self.result_schema, registry=self.registry, format_checker=FormatChecker()
        ).iter_errors(attacked))
        self.assertTrue(result_errors)
        self.assertIn(
            "NON_EVIDENTIARY_SOURCE_INPUT",
            contracts.semantic_codes(attacked["evidence_packet"]),
        )


if __name__ == "__main__":
    unittest.main()
