import copy
import json
import math
import unittest
from pathlib import Path

from src.spectra_gcp_adapter import (
    canonical_event_sha256,
    reduce_live_execution_events,
)


ROOT = Path(__file__).resolve().parents[2]
ANCHOR_PATH = ROOT / "platform/gcp-e2e-h04/live-deployment-anchor.json"
SHA_INPUT = "sha256:" + "1" * 64
SHA_MISSION = "sha256:" + "2" * 64
SHA_PARTS = "sha256:" + "3" * 64
SHA_CORE_OUTPUT = "sha256:" + "4" * 64
SHA_CORE_RESULT = "sha256:" + "5" * 64
SHA_ASSURANCE = "sha256:" + "6" * 64
SHA_RESULT_OBJECT = "sha256:" + "7" * 64


class LiveExecutionEventContractTest(unittest.TestCase):
    def setUp(self):
        self.anchor = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
        self.events = self.complete_events()

    def execution(self):
        return {
            "project_id": self.anchor["project_id"],
            "region": self.anchor["region"],
            "workflow_name": self.anchor["workflow"]["name"],
            "execution_id": "ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34",
            "correlation_id": "spectra-live-ea79cbd9-ada2-4d8c-a584-4ef0c5e0bc34",
        }

    def event(self, event_type, source, payload):
        return {
            "contract_version": "SPECTRA_LIVE_EXECUTION_EVENT_1.0.0",
            "event_id": "pending",
            "sequence": -1,
            "occurred_at": "2026-08-25T00:00:00Z",
            "execution": self.execution(),
            "source": source,
            "event_type": event_type,
            "payload": payload,
            "previous_event_sha256": "GENESIS",
            "event_sha256": "pending",
        }

    def workflow_source(self):
        return {
            "kind": "WORKFLOW",
            "id": self.anchor["workflow"]["name"],
            "revision": self.anchor["workflow"]["revision"],
        }

    def storage_source(self, generation):
        return {
            "kind": "CLOUD_STORAGE",
            "id": self.anchor["storage"]["bucket"],
            "revision": generation,
        }

    def agent_source(self, role):
        return {
            "kind": "CLOUD_RUN_AGENT",
            "id": self.anchor["agents"][role]["service"],
            "revision": self.anchor["agents"][role]["revision"],
        }

    def agent_payload(self, role, response_sha, codes):
        return {
            "role": role,
            "processing_status": "VALID",
            "assurance_decision": "HOLD",
            "input_sha256": SHA_INPUT,
            "response_sha256": response_sha,
            "stable_codes": sorted(codes),
        }

    def rechain(self, events):
        previous = "GENESIS"
        for index, event in enumerate(events):
            event["event_id"] = f"event-{index:02d}"
            event["sequence"] = index
            event["occurred_at"] = f"2026-08-25T00:00:{index:02d}Z"
            event["previous_event_sha256"] = previous
            event["event_sha256"] = canonical_event_sha256(event)
            previous = event["event_sha256"]
        return events

    def complete_events(self):
        input_generation = "1787243596527806"
        result_generation = "1787243600145935"
        events = [
            self.event(
                "WORKFLOW_STARTED",
                self.workflow_source(),
                {"workflow_state": "RUNNING"},
            ),
            self.event(
                "STORAGE_INPUT_BOUND",
                self.storage_source(input_generation),
                {
                    "bucket_id": self.anchor["storage"]["bucket"],
                    "object_name": "inputs/live-control.json",
                    "generation": input_generation,
                    "sha256": SHA_INPUT,
                },
            ),
            self.event(
                "AGENT_COMPLETED",
                self.agent_source("mission"),
                self.agent_payload(
                    "mission",
                    SHA_MISSION,
                    ["PRODUCTION_CORE_BOUND", "REAL_ENVIRONMENT_EVIDENCE_MISSING"],
                ),
            ),
            self.event(
                "AGENT_COMPLETED",
                self.agent_source("parts"),
                self.agent_payload(
                    "parts",
                    SHA_PARTS,
                    ["REAL_PART_TEST_EVIDENCE_MISSING", "SYNTHETIC_EVIDENCE_ONLY"],
                ),
            ),
            self.event(
                "CORE_COMPLETED",
                {
                    "kind": "DETERMINISTIC_CORE",
                    "id": self.anchor["core"]["id"],
                    "revision": self.anchor["core"]["revision"],
                },
                {
                    "processing_status": "VALID",
                    "engineering_gate": "NOT_EVALUATED",
                    "assurance_decision": "HOLD",
                    "run_id": "mvp-cb826edb88ea5b67",
                    "execution_input_sha256": SHA_INPUT,
                    "core_input_sha256": "sha256:" + "8" * 64,
                    "output_sha256": SHA_CORE_OUTPUT,
                    "result_sha256": SHA_CORE_RESULT,
                    "stable_codes": ["SYNTHETIC_ONLY"],
                },
            ),
            self.event(
                "AGENT_COMPLETED",
                self.agent_source("assurance"),
                self.agent_payload(
                    "assurance", SHA_ASSURANCE, ["SYNTHETIC_ONLY"]
                ),
            ),
            self.event(
                "STORAGE_RESULT_BOUND",
                self.storage_source(result_generation),
                {
                    "bucket_id": self.anchor["storage"]["bucket"],
                    "object_name": "results/ea79cbd9.json",
                    "generation": result_generation,
                    "sha256": SHA_RESULT_OBJECT,
                },
            ),
            self.event(
                "WORKFLOW_COMPLETED",
                self.workflow_source(),
                {"workflow_state": "SUCCEEDED"},
            ),
        ]
        return self.rechain(events)

    def reduce(self, events=None, anchor=None, mode="LIVE_API"):
        return reduce_live_execution_events(
            self.events if events is None else events,
            trusted_deployment=self.anchor if anchor is None else anchor,
            observation_mode=mode,
        )

    def assert_invalid(self, result, *codes):
        self.assertEqual(result["processing_status"], "INVALID_INPUT")
        self.assertEqual(result["stream_status"], "INVALID")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertEqual(result["timeline"], [])
        for code in codes:
            self.assertIn(code, result["stable_codes"])

    def test_complete_live_stream_is_visualizable_but_not_business_pass(self):
        result = self.reduce()

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["observation_mode"], "LIVE_API")
        self.assertEqual(result["stream_status"], "COMPLETE")
        self.assertEqual(result["execution_status"], "SUCCEEDED")
        self.assertTrue(result["workflow_succeeded"])
        self.assertFalse(result["workflow_success_is_business_pass"])
        self.assertEqual(
            result["event_chain_authenticity"],
            "INTEGRITY_ONLY_NOT_AUTHENTICATED",
        )
        self.assertEqual(result["evidence_status"], "SYNTHETIC_ONLY")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertEqual(len(result["timeline"]), 8)
        self.assertIsNotNone(result["stream_sha256"])

    def test_snapshot_replay_is_explicitly_distinct_from_live_api(self):
        result = self.reduce(mode="SNAPSHOT_REPLAY")
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["observation_mode"], "SNAPSHOT_REPLAY")
        self.assertEqual(result["execution_status"], "SUCCEEDED")

    def test_partial_valid_stream_remains_in_progress_and_hold(self):
        partial = copy.deepcopy(self.events[:4])
        result = self.reduce(events=partial)

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["stream_status"], "IN_PROGRESS")
        self.assertEqual(result["execution_status"], "RUNNING")
        self.assertFalse(result["workflow_succeeded"])
        self.assertEqual(result["assurance_decision"], "HOLD")

    def test_event_body_hash_tamper_is_rejected(self):
        attacked = copy.deepcopy(self.events)
        attacked[2]["payload"]["processing_status"] = "INVALID_INPUT"
        self.assert_invalid(self.reduce(attacked), "EVENT_SHA256_MISMATCH")

    def test_chain_predecessor_tamper_is_rejected(self):
        attacked = copy.deepcopy(self.events)
        attacked[4]["previous_event_sha256"] = "sha256:" + "0" * 64
        self.assert_invalid(
            self.reduce(attacked),
            "EVENT_CHAIN_PREDECESSOR_MISMATCH",
            "EVENT_SHA256_MISMATCH",
        )

    def test_mixed_execution_cannot_share_one_timeline(self):
        attacked = copy.deepcopy(self.events)
        attacked[3]["execution"]["execution_id"] = "different-execution"
        self.rechain(attacked)
        self.assert_invalid(self.reduce(attacked), "MIXED_EXECUTION_STREAM")

    def test_sequence_time_and_event_id_must_be_monotonic_and_unique(self):
        attacked = copy.deepcopy(self.events)
        attacked[3]["event_id"] = attacked[2]["event_id"]
        attacked[3]["sequence"] = 9
        attacked[3]["occurred_at"] = "2026-08-24T23:59:00Z"
        previous = attacked[2]["event_sha256"]
        attacked[3]["previous_event_sha256"] = previous
        attacked[3]["event_sha256"] = canonical_event_sha256(attacked[3])
        for index in range(4, len(attacked)):
            attacked[index]["previous_event_sha256"] = attacked[index - 1][
                "event_sha256"
            ]
            attacked[index]["event_sha256"] = canonical_event_sha256(
                attacked[index]
            )

        self.assert_invalid(
            self.reduce(attacked),
            "EVENT_ID_INVALID_OR_DUPLICATE",
            "EVENT_SEQUENCE_INVALID",
            "EVENT_TIME_REGRESSION",
        )

    def test_agent_revision_must_match_deployment_anchor(self):
        attacked = copy.deepcopy(self.events)
        attacked[2]["source"]["revision"] = "attacker-revision"
        self.rechain(attacked)
        self.assert_invalid(self.reduce(attacked), "AGENT_SOURCE_MISMATCH")

    def test_every_agent_and_core_must_bind_the_input_object_hash(self):
        attacked = copy.deepcopy(self.events)
        attacked[4]["payload"]["execution_input_sha256"] = "sha256:" + "9" * 64
        self.rechain(attacked)
        self.assert_invalid(
            self.reduce(attacked), "EXECUTION_INPUT_HASH_MISMATCH"
        )

    def test_succeeded_terminal_requires_complete_component_set(self):
        attacked = copy.deepcopy(self.events)
        attacked.pop(4)
        self.rechain(attacked)
        self.assert_invalid(
            self.reduce(attacked), "TERMINAL_EVENT_SET_INCOMPLETE"
        )

    def test_completion_cannot_precede_result_events(self):
        attacked = copy.deepcopy(self.events)
        completion = attacked.pop()
        attacked.insert(4, completion)
        self.rechain(attacked)
        self.assert_invalid(
            self.reduce(attacked), "EVENT_CAUSAL_ORDER_INVALID"
        )

    def test_assurance_cannot_precede_mission_parts_and_core(self):
        attacked = copy.deepcopy(self.events)
        assurance = attacked.pop(5)
        attacked.insert(2, assurance)
        self.rechain(attacked)
        self.assert_invalid(
            self.reduce(attacked), "EVENT_CAUSAL_ORDER_INVALID"
        )

    def test_failed_workflow_can_end_without_downstream_success(self):
        failed = [copy.deepcopy(self.events[0]), copy.deepcopy(self.events[-1])]
        failed[-1]["payload"]["workflow_state"] = "FAILED"
        self.rechain(failed)
        result = self.reduce(failed)

        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["stream_status"], "COMPLETE")
        self.assertEqual(result["execution_status"], "FAILED")
        self.assertFalse(result["workflow_succeeded"])
        self.assertEqual(result["assurance_decision"], "HOLD")

    def test_synthetic_assurance_promotion_is_rejected(self):
        attacked = copy.deepcopy(self.events)
        attacked[5]["payload"]["assurance_decision"] = "PASS"
        self.rechain(attacked)
        self.assert_invalid(
            self.reduce(attacked), "SYNTHETIC_ASSURANCE_PROMOTION_REJECTED"
        )

    def test_deployment_anchor_cannot_self_promote_or_rebind(self):
        promoted = copy.deepcopy(self.anchor)
        promoted["data_class"] = "ACTUAL"
        promoted["max_assurance_decision"] = "PASS"
        rebound = copy.deepcopy(self.anchor)
        rebound["agents"]["parts"]["revision"] = "attacker-revision"

        promoted_result = self.reduce(anchor=promoted)
        rebound_result = self.reduce(anchor=rebound)
        self.assert_invalid(
            promoted_result,
            "DEPLOYMENT_DATA_CLASS_UNSUPPORTED",
            "DEPLOYMENT_ASSURANCE_BOUNDARY_INVALID",
        )
        self.assert_invalid(rebound_result, "AGENT_SOURCE_MISMATCH")

    def test_duplicate_agent_role_and_missing_role_fail_closed(self):
        attacked = copy.deepcopy(self.events)
        attacked[3]["payload"]["role"] = "mission"
        attacked[3]["source"] = self.agent_source("mission")
        self.rechain(attacked)
        self.assert_invalid(
            self.reduce(attacked),
            "AGENT_EVENT_DUPLICATE",
            "TERMINAL_AGENT_SET_INCOMPLETE",
        )

    def test_malformed_nonfinite_and_unknown_fields_do_not_escape(self):
        attacked = copy.deepcopy(self.events)
        attacked[2]["payload"]["latency_ms"] = math.nan
        result = self.reduce(attacked)
        self.assert_invalid(
            result,
            "INPUT_FIELD_FORBIDDEN",
            "EVENT_CANONICALIZATION_FAILED",
            "EVENT_SHA256_MISMATCH",
        )

    def test_reported_codes_are_data_not_validator_success(self):
        result = self.reduce()
        self.assertEqual(result["stable_codes"], [])
        self.assertTrue(
            {
                "SYNTHETIC_ONLY",
                "REAL_ENVIRONMENT_EVIDENCE_MISSING",
                "REAL_PART_TEST_EVIDENCE_MISSING",
            }.issubset(result["reported_codes"])
        )

    def test_reducer_does_not_claim_authenticated_live_transport(self):
        result = self.reduce()
        self.assertEqual(
            result["limitations"],
            [
                "GCP_API_NOT_CALLED_BY_REDUCER",
                "LIVE_TRANSPORT_AUTHENTICITY_NOT_ESTABLISHED",
                "SCIENTIFIC_EVIDENCE_NOT_VALIDATED",
            ],
        )


if __name__ == "__main__":
    unittest.main()
