from __future__ import annotations

import copy
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("h05_agents", ROOT / "service/main.py")
AGENTS = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AGENTS)


def load_fixture(name: str) -> dict:
    return json.loads((ROOT / f"fixtures/{name}").read_text(encoding="utf-8"))


def envelope(fixture: dict, declared_sha: str | None = None) -> dict:
    body_sha = AGENTS.sha256_uri(fixture)
    receipt_sha = declared_sha or body_sha
    return {
        "run_id": "local-run-001",
        "correlation_id": "local-correlation-001",
        "input_storage": {
            "artifact_id": fixture["artifact_id"],
            "project_id": "synthetic-project",
            "bucket_id": "synthetic-bucket",
            "object_name": "inputs/synthetic.json",
            "generation": "1",
            "metadata_sha256": receipt_sha,
            "expected_sha256": receipt_sha,
        },
        "fixture": fixture,
    }


class AgentContractTests(unittest.TestCase):
    def test_canonical_numeric_boundary_and_workflows_parity(self):
        self.assertEqual(AGENTS.sha256_uri({"value": 12.0}), AGENTS.sha256_uri({"value": 12}))
        with self.assertRaises(ValueError):
            AGENTS.canonical_bytes({"value": math.inf})

    def test_normal_chain_uses_production_core_and_remains_hold(self):
        request = envelope(load_fixture("normal.json"))
        mission = AGENTS.evaluate(copy.deepcopy(request), "mission")
        parts = AGENTS.evaluate(copy.deepcopy(request), "parts")
        assurance_request = copy.deepcopy(request)
        assurance_request["prior_results"] = {"mission": mission, "parts": parts}
        assurance = AGENTS.evaluate(assurance_request, "assurance")
        self.assertEqual("VALID", mission["processing_status"])
        self.assertTrue(mission["body_hash_verified"])
        self.assertIn("PRODUCTION_CORE_BOUND", mission["stable_codes"])
        self.assertEqual("mvp-synthetic-ecc-policy-001", mission["core_result"]["case_id"])
        self.assertEqual("VALID", parts["processing_status"])
        self.assertEqual("VALID", assurance["processing_status"])
        self.assertEqual("NOT_EVALUATED", assurance["engineering_gate"])
        self.assertEqual("HOLD", assurance["assurance_decision"])

    def test_local_production_core_semantic_and_hash_parity(self):
        case, model = AGENTS._load_core_inputs()
        control = AGENTS.run_mvp_decision(case, model)
        mission = AGENTS.evaluate(envelope(load_fixture("normal.json")), "mission")
        self.assertEqual(control, mission["core_result"])
        self.assertEqual(control["output_hash"], mission["core_result"]["output_hash"])
        self.assertEqual(AGENTS.sha256_uri(control), mission["core_result_sha256"])

    def test_body_metadata_expected_simultaneous_forgery_is_blocked(self):
        forged_sha = "sha256:" + ("0" * 64)
        result = AGENTS.evaluate(envelope(load_fixture("normal.json"), forged_sha), "mission")
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertEqual("NOT_EVALUATED", result["engineering_gate"])
        self.assertEqual("HOLD", result["assurance_decision"])
        self.assertFalse(result["body_hash_verified"])
        self.assertIn("INPUT_BODY_SHA256_MISMATCH", result["stable_codes"])
        self.assertNotIn("core_result", result)

    def test_metadata_expected_disagreement_is_blocked(self):
        request = envelope(load_fixture("normal.json"))
        request["input_storage"]["metadata_sha256"] = "sha256:" + ("1" * 64)
        result = AGENTS.evaluate(request, "mission")
        self.assertIn("INPUT_SHA256_METADATA_MISMATCH", result["stable_codes"])
        self.assertEqual("HOLD", result["assurance_decision"])

    def test_corrupted_part_hash_is_blocked_by_parts_and_assurance(self):
        request = envelope(load_fixture("corrupted-evidence-hash.json"))
        mission = AGENTS.evaluate(copy.deepcopy(request), "mission")
        parts = AGENTS.evaluate(copy.deepcopy(request), "parts")
        assurance_request = copy.deepcopy(request)
        assurance_request["prior_results"] = {"mission": mission, "parts": parts}
        assurance = AGENTS.evaluate(assurance_request, "assurance")
        self.assertIn("PART_EVIDENCE_HASH_MISMATCH", parts["stable_codes"])
        self.assertIn("PARTS_AGENT_NOT_VALID", assurance["stable_codes"])
        self.assertEqual("HOLD", assurance["assurance_decision"])

    def test_malformed_agent_input_is_structured_hold(self):
        request = envelope(load_fixture("malformed-part.json"))
        result = AGENTS.evaluate(request, "parts")
        self.assertEqual("INVALID_INPUT", result["processing_status"])
        self.assertIn("EXACT_PART_IDENTITY_INVALID", result["stable_codes"])
        self.assertEqual("HOLD", result["assurance_decision"])

    def test_legacy_test_control_fields_have_no_execution_path(self):
        request = envelope(load_fixture("normal.json"))
        request.update({"test_mode": "STRUCTURED_FAILURE", "failure_role": "parts"})
        result = AGENTS.evaluate(request, "parts")
        self.assertEqual("VALID", result["processing_status"])
        self.assertNotIn("AGENT_TEST_FAILURE", result["stable_codes"])

    def test_assurance_recomputes_agent_response_hash(self):
        request = envelope(load_fixture("normal.json"))
        mission = AGENTS.evaluate(copy.deepcopy(request), "mission")
        parts = AGENTS.evaluate(copy.deepcopy(request), "parts")
        mission["core_result"]["case_id"] = "tampered"
        assurance_request = copy.deepcopy(request)
        assurance_request["prior_results"] = {"mission": mission, "parts": parts}
        assurance = AGENTS.evaluate(assurance_request, "assurance")
        self.assertIn("AGENT_RESPONSE_HASH_MISMATCH", assurance["stable_codes"])
        self.assertEqual("HOLD", assurance["assurance_decision"])

    def test_malformed_request_never_raises(self):
        for malformed in (None, [], {}, {"run_id": []}):
            result = AGENTS.evaluate(malformed, "mission")
            self.assertEqual("INVALID_INPUT", result["processing_status"])
            self.assertEqual("HOLD", result["assurance_decision"])
            self.assertIn("AGENT_REQUEST_INVALID", result["stable_codes"])

    def test_workflow_endpoints_are_deployment_bound(self):
        workflow = (ROOT / "workflow.yaml").read_text(encoding="utf-8")
        self.assertIn('sys.get_env("MISSION_URL")', workflow)
        self.assertNotIn("${args.mission_url}", workflow)
        self.assertNotIn("${args.parts_url}", workflow)
        self.assertNotIn("${args.assurance_url}", workflow)
        self.assertIn("ENDPOINT_OVERRIDE_FORBIDDEN", workflow)
        self.assertNotIn("AGENT_TEST_FAILURE", workflow)
        self.assertNotIn("test_mode", workflow)
        self.assertNotIn("failure_role", workflow)

    def test_staged_image_context_excludes_repo_and_private_evidence(self):
        with tempfile.TemporaryDirectory(prefix="spectra-h05-stage-test-") as temp_dir:
            output = Path(temp_dir)
            spec = importlib.util.spec_from_file_location("stage", ROOT / "scripts/stage_build_context.py")
            stage = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(stage)
            old_argv = list(__import__("sys").argv)
            try:
                __import__("sys").argv = ["stage", "--repo-root", str(ROOT.parents[1]), "--output", str(output)]
                self.assertEqual(0, stage.main())
            finally:
                __import__("sys").argv = old_argv
            self.assertTrue((output / "src/spectra_sim/mvp_engine.py").is_file())
            self.assertTrue((output / "simulation/fixtures/mvp-ecc-policy-v2.json").is_file())
            self.assertFalse((output / ".git").exists())
            self.assertFalse((output / "docs").exists())
            staged_valid = sorted(path.name for path in (output / "tests/schema/fixtures/valid").glob("*.json"))
            self.assertEqual(sorted(stage.VALID_FIXTURES), staged_valid)


if __name__ == "__main__":
    unittest.main()
