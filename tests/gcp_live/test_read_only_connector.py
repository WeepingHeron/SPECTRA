import copy
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from src.spectra_gcp_adapter import (
    build_read_only_commands,
    collect_read_only_execution,
    subprocess_gcloud_runner,
)


ROOT = Path(__file__).resolve().parents[2]
ANCHOR = json.loads(
    (ROOT / "platform/gcp-e2e-h04/live-deployment-anchor.json").read_text(
        encoding="utf-8"
    )
)
EXECUTION_ID = "ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34"
INPUT_SHA = "sha256:" + "1" * 64


def canonical_sha(value):
    raw = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def finished_agent(role, codes, **extra):
    result = {
        "schema_version": "1.0.0",
        "run_id": EXECUTION_ID,
        "correlation_id": f"spectra-h05-{EXECUTION_ID}",
        "agent": role,
        "data_class": "SYNTHETIC",
        "processing_status": "VALID",
        "engineering_gate": "NOT_EVALUATED",
        "assurance_decision": "HOLD",
        "input_sha256": INPUT_SHA,
        "latency_ms": 10,
        "stable_codes": sorted(codes),
        **extra,
    }
    result["response_sha256"] = canonical_sha(result)
    return result


class FakeRunner:
    def __init__(self, responses):
        self.responses = list(responses)
        self.commands = []

    def __call__(self, command):
        self.commands.append(command)
        if not self.responses:
            raise AssertionError("unexpected command")
        return self.responses.pop(0)


class ReadOnlyConnectorTest(unittest.TestCase):
    def setUp(self):
        self.core = {
            "run_id": "mvp-cb826edb88ea5b67",
            "data_class": "SYNTHETIC",
            "input_hash": "sha256:" + "2" * 64,
            "output_hash": "sha256:" + "3" * 64,
            "processing_status": "VALID",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
        }
        self.mission = finished_agent(
            "mission",
            ["PRODUCTION_CORE_BOUND", "REAL_ENVIRONMENT_EVIDENCE_MISSING"],
            body_hash_verified=True,
            body_sha256=INPUT_SHA,
            core_result=self.core,
            core_result_sha256=canonical_sha(self.core),
        )
        self.parts = finished_agent(
            "parts",
            ["REAL_PART_TEST_EVIDENCE_MISSING", "SYNTHETIC_EVIDENCE_ONLY"],
        )
        self.assurance = finished_agent("assurance", ["SYNTHETIC_ONLY"])
        self.stored = {
            "schema_version": "1.0.0",
            "run_id": EXECUTION_ID,
            "correlation_id": f"spectra-h05-{EXECUTION_ID}",
            "data_class": "SYNTHETIC",
            "processing_status": "VALID",
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "stable_codes": ["SYNTHETIC_ONLY"],
            "input_storage": {
                "project_id": ANCHOR["project_id"],
                "bucket_id": ANCHOR["storage"]["bucket"],
                "object_name": "inputs/live-control.json",
                "generation": "111",
                "metadata_sha256": INPUT_SHA,
                "expected_sha256": INPUT_SHA,
            },
            "agent_results": {
                "mission": self.mission,
                "parts": self.parts,
                "assurance": self.assurance,
            },
        }
        self.workflow_result = {
            "execution_id": EXECUTION_ID,
            "correlation_id": f"spectra-h05-{EXECUTION_ID}",
            "result_storage": {
                "bucket_id": ANCHOR["storage"]["bucket"],
                "object_name": f"results/{EXECUTION_ID}.json",
                "generation": "222",
            },
            "result": self.stored,
        }
        self.execution = {
            "name": (
                f"projects/841895608290/locations/{ANCHOR['region']}/workflows/"
                f"{ANCHOR['workflow']['name']}/executions/{EXECUTION_ID}"
            ),
            "workflowRevisionId": ANCHOR["workflow"]["revision"],
            "state": "SUCCEEDED",
            "startTime": "2026-08-25T00:00:00Z",
            "endTime": "2026-08-25T00:00:05Z",
            "argument": json.dumps(
                {
                    "bucket": ANCHOR["storage"]["bucket"],
                    "input_object": "inputs/live-control.json",
                    "input_generation": "111",
                    "input_sha256": INPUT_SHA,
                }
            ),
            "result": json.dumps(self.workflow_result),
        }
        self.logs = []
        for offset, role, result in (
            (1, "mission", self.mission),
            (2, "parts", self.parts),
            (3, "assurance", self.assurance),
        ):
            self.logs.append(
                {
                    "timestamp": f"2026-08-25T00:00:0{offset}Z",
                    "jsonPayload": {
                        "message": "spectra_h05_agent_result",
                        "run_id": EXECUTION_ID,
                        "correlation_id": f"spectra-h05-{EXECUTION_ID}",
                        "agent": role,
                        "processing_status": result["processing_status"],
                        "assurance_decision": result["assurance_decision"],
                        "stable_codes": result["stable_codes"],
                    },
                    "resource": {
                        "labels": {
                            "service_name": ANCHOR["agents"][role]["service"],
                            "revision_name": ANCHOR["agents"][role]["revision"],
                        }
                    },
                }
            )

    def runner(self, *, stored=None, before="222", after="222"):
        body = json.dumps(
            self.stored if stored is None else stored,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return FakeRunner(
            [
                json.dumps(self.execution),
                json.dumps(self.logs),
                json.dumps({"generation": before}),
                body,
                json.dumps({"generation": after}),
            ]
        )

    def test_commands_are_fixed_read_only_resource_queries(self):
        commands = build_read_only_commands(
            EXECUTION_ID, trusted_deployment=ANCHOR
        )
        flattened = [token for command in commands.values() for token in command]
        for forbidden in ("run", "execute", "cp", "rm", "delete", "deploy", "set-iam-policy"):
            self.assertNotIn(forbidden, flattened)
        self.assertEqual(commands["execution"][:4], ["gcloud", "workflows", "executions", "describe"])
        self.assertEqual(commands["result_body"][:3], ["gcloud", "storage", "cat"])

    def test_completed_execution_becomes_valid_hold_receipt(self):
        runner = self.runner()
        result = collect_read_only_execution(
            EXECUTION_ID,
            trusted_deployment=ANCHOR,
            command_runner=runner,
        )
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["connector_status"], "OBSERVED")
        self.assertFalse(result["mutation_attempted"])
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertEqual(result["event_receipt"]["stream_status"], "COMPLETE")
        self.assertTrue(result["event_receipt"]["workflow_succeeded"])
        self.assertFalse(result["event_receipt"]["workflow_success_is_business_pass"])
        self.assertEqual(len(runner.commands), 5)
        self.assertIn('timestamp>="2026-08-25T00:00:00Z"', runner.commands[1][3])
        self.assertIn('timestamp<="2026-08-25T00:00:05Z"', runner.commands[1][3])

    def test_invalid_execution_id_is_rejected_before_any_command(self):
        runner = FakeRunner([])
        result = collect_read_only_execution(
            "../../attacker;gcloud workflows run x",
            trusted_deployment=ANCHOR,
            command_runner=runner,
        )
        self.assertEqual(result["stable_codes"], ["EXECUTION_ID_INVALID"])
        self.assertEqual(runner.commands, [])

    def test_generation_must_match_before_and_after_body_read(self):
        runner = self.runner(after="223")
        result = collect_read_only_execution(
            EXECUTION_ID, trusted_deployment=ANCHOR, command_runner=runner
        )
        self.assertEqual(
            result["stable_codes"], ["RESULT_GENERATION_CHANGED_OR_MISMATCHED"]
        )
        self.assertIsNone(result["event_receipt"])

    def test_storage_body_must_equal_workflow_returned_result(self):
        attacked = copy.deepcopy(self.stored)
        attacked["stable_codes"] = ["ATTACKER_EDIT"]
        runner = self.runner(stored=attacked)
        result = collect_read_only_execution(
            EXECUTION_ID, trusted_deployment=ANCHOR, command_runner=runner
        )
        self.assertEqual(
            result["stable_codes"], ["WORKFLOW_AND_STORAGE_RESULT_MISMATCH"]
        )

    def test_agent_response_hash_tamper_fails_closed(self):
        attacked = copy.deepcopy(self.stored)
        attacked["agent_results"]["parts"]["latency_ms"] = 999
        self.execution["result"] = json.dumps(
            {**self.workflow_result, "result": attacked}
        )
        runner = self.runner(stored=attacked)
        result = collect_read_only_execution(
            EXECUTION_ID, trusted_deployment=ANCHOR, command_runner=runner
        )
        self.assertEqual(
            result["stable_codes"], ["AGENT_RESPONSE_SHA256_MISMATCH"]
        )

    def test_deployment_anchor_cannot_promote_assurance(self):
        attacked = copy.deepcopy(ANCHOR)
        attacked["max_assurance_decision"] = "SUPPORTED_WITH_MITIGATION"
        runner = FakeRunner([])
        result = collect_read_only_execution(
            EXECUTION_ID, trusted_deployment=attacked, command_runner=runner
        )
        self.assertEqual(result["stable_codes"], ["DEPLOYMENT_ANCHOR_INVALID"])
        self.assertEqual(runner.commands, [])

    def test_nonfinite_gcp_json_fails_closed(self):
        runner = FakeRunner(['{"state":"SUCCEEDED","latency":NaN}'])
        result = collect_read_only_execution(
            EXECUTION_ID, trusted_deployment=ANCHOR, command_runner=runner
        )
        self.assertEqual(result["stable_codes"], ["EXECUTION_RESPONSE_INVALID"])
        self.assertEqual(len(runner.commands), 1)

    def test_gcloud_reauthentication_error_has_stable_nonsecret_code(self):
        failure = subprocess.CalledProcessError(
            1,
            ["gcloud", "workflows", "executions", "describe"],
            stderr=b"Reauthentication failed. Please run gcloud auth login",
        )
        with mock.patch("subprocess.run", side_effect=failure):
            with self.assertRaisesRegex(ValueError, "GCLOUD_AUTH_REAUTH_REQUIRED"):
                subprocess_gcloud_runner(failure.cmd)


if __name__ == "__main__":
    unittest.main()
