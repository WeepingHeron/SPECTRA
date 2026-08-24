from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_env_adapter import assess_issuance  # noqa: E402
from spectra_env_adapter.gate import REFERENCE_MISSION, REQUIRED_ROLES  # noqa: E402
from spectra_env_adapter.issuance_gate import (  # noqa: E402
    REQUIRED_ISSUANCE_ACTIONS,
    TRUST_STORE_AUDIENCE,
    TRUST_STORE_SCOPE,
    freeze_deployment_trust_store_snapshot,
    issuance_anchor_digest,
    issuance_review_hash,
    issuance_trust_store_hash,
)


NOW = datetime(2026, 8, 24, tzinfo=timezone.utc)


def synthetic_control() -> dict:
    scope_hash = f"sha256:{'1' * 64}"
    rights_id = "synthetic-rights-control"
    bundle_hash = f"sha256:{'2' * 64}"
    manifest_hash = f"sha256:{'3' * 64}"
    roles = sorted(REQUIRED_ROLES | {"ORBIT_OUTPUT", "SOLAR_ATTENUATION"})
    return {
        "evidence_class": "SYNTHETIC_CONTROL",
        "provider": {
            "provider_job_reference": "synthetic-provider-job",
            "reference_status": "VERIFIED_PROVIDER_RECORD",
            "source_locator": "fixture://provider-record",
            "source_location": "synthetic field provider_job_reference",
            "record_hash": f"sha256:{'4' * 64}",
            "reviewer": "synthetic-provider-reviewer",
            "history_anchor_ref": "fixture://provider-review-history",
        },
        "rights_snapshot": {
            "status": "APPROVED",
            "rights_snapshot_id": rights_id,
            "required_scope_hash": scope_hash,
            "subject": "synthetic-product-consumer",
            "approver": "synthetic-rights-approver",
            "valid_from": "2026-08-01T00:00:00Z",
            "valid_until": "2027-08-24T00:00:00Z",
            "action_grants": [
                {
                    "action": action,
                    "grant_status": "ALLOWED",
                    "scope_hash": scope_hash,
                    "subject": "synthetic-product-consumer",
                    "approver": "synthetic-rights-approver",
                    "source_locator": f"fixture://rights/{action.lower()}",
                    "source_location": "synthetic grant record",
                    "valid_from": "2026-08-01T00:00:00Z",
                    "valid_until": "2027-08-24T00:00:00Z",
                }
                for action in sorted(REQUIRED_ISSUANCE_ACTIONS)
            ],
        },
        "approved_storage": {
            "status": "APPROVED",
            "immutable": True,
            "identity": {
                "project_id": "synthetic-project",
                "bucket_id": "synthetic-bucket",
                "object_name": "synthetic/environment-bundle",
                "generation": "1",
            },
        },
        "raw_manifest": {
            "status": "APPROVED",
            "contract_version": "2.0.0",
            "manifest_hash": manifest_hash,
            "bundle_hash": bundle_hash,
            "storage_generation": "1",
            "rights_snapshot_id": rights_id,
            "parser_input_hash": bundle_hash,
            "parser_output_hash": f"sha256:{'5' * 64}",
            "history_anchor_ref": "fixture://manifest-history",
            "validation": {
                "quarantine_status": "VALIDATED",
                "malware_scan": "PASS",
                "mime_check": "MATCH",
                "hash_check": "MATCH",
                "review_status": "APPROVED",
            },
        },
        "artifact_identity": {
            "checksum_verified": True,
            "checksum_count": 9,
            "artifact_set_hash": bundle_hash,
            "artifacts": [
                {
                    "role": role,
                    "identity_sha256": f"sha256:{index:064x}",
                    "resolved_path": f"/synthetic/raw/{index:02d}-{role.lower()}",
                }
                for index, role in enumerate(roles, start=1)
            ],
        },
        "model_conditions": {
            "mission": REFERENCE_MISSION,
            "source_completeness": "COMPLETE_MISSION",
            "platform_build": "4.6.14.3582",
            "geometry": "CENTRE_OF_AL_SPHERES_4PI",
            "target_material": "SILICON",
            "dose_unit": "rad(Si)",
            "shielding_depths_mm_al": [1.0, 2.0, 3.0, 4.0],
            "model_chain": {
                "trapped": {"name": "AE9/AP9", "version": "1.50", "run_mode": "MEAN", "verification_status": "VERIFIED_REPORT"},
                "solar": {"name": "SAPPHIRE", "mode": "TOTAL_FLUENCE", "confidence_percent": 95, "verification_status": "VERIFIED_REPORT"},
                "dose": {"name": "SHIELDOSE-2", "version": "2.10", "verification_status": "VERIFIED_REPORT"},
            },
        },
        "scientific_crosscheck": {
            "status": "PASSED",
            "protocol_status": "APPROVED_BEFORE_RESULTS",
            "protocol_hash": f"sha256:{'6' * 64}",
            "criteria_source": "fixture://crosscheck-criteria",
            "reviewer": "synthetic-science-reviewer",
            "result_hash": f"sha256:{'7' * 64}",
        },
        "emission_authorization": {
            "status": "APPROVED",
            "approval_target_hash": manifest_hash,
            "approver": "synthetic-emission-approver",
            "history_anchor_ref": "fixture://emission-history",
        },
    }


def trusted_anchor_for(evidence: dict) -> dict:
    return {
        "anchor_id": "out-of-band-test-anchor",
        "status": "APPROVED",
        "approver": "independent-test-approver",
        "history_anchor_ref": "fixture://independent-anchor-history",
        "review_payload_hash": issuance_review_hash(evidence),
        "provider_record_hash": evidence["provider"]["record_hash"],
        "provider_job_reference": evidence["provider"]["provider_job_reference"],
        "rights_snapshot_id": evidence["rights_snapshot"]["rights_snapshot_id"],
        "rights_scope_hash": evidence["rights_snapshot"]["required_scope_hash"],
        "raw_manifest_hash": evidence["raw_manifest"]["manifest_hash"],
        "raw_bundle_hash": evidence["raw_manifest"]["bundle_hash"],
        "raw_storage_generation": evidence["raw_manifest"]["storage_generation"],
        "scientific_crosscheck_result_hash": evidence["scientific_crosscheck"]["result_hash"],
        "emission_authorization_target_hash": evidence["emission_authorization"]["approval_target_hash"],
    }


def trust_store_for(anchor: dict, **entry_overrides) -> dict:
    entry = {
        "anchor_id": anchor["anchor_id"],
        "anchor_digest": issuance_anchor_digest(anchor),
        "approver": anchor["approver"],
        "audience": TRUST_STORE_AUDIENCE,
        "scope": TRUST_STORE_SCOPE,
        "evidence_class": "ACTUAL_REVIEW",
        "valid_from": "2026-08-01T00:00:00Z",
        "valid_until": "2027-08-24T00:00:00Z",
        "revoked": False,
    }
    entry.update(entry_overrides)
    store = {
        "store_schema_version": "1.0.0",
        "snapshot_id": "fixture://deployment-trust-store/snapshot-001",
        "snapshot_hash": "",
        "audience": TRUST_STORE_AUDIENCE,
        "scope": TRUST_STORE_SCOPE,
        "immutable": True,
        "entries": [entry],
    }
    store["snapshot_hash"] = issuance_trust_store_hash(store)
    return store


def refresh_store_hash(store: dict) -> None:
    store["snapshot_hash"] = issuance_trust_store_hash(store)


def freeze_store(store: dict):
    snapshot = freeze_deployment_trust_store_snapshot(store)
    if snapshot is None:
        raise AssertionError("test trust store must be canonical JSON")
    return snapshot


class EnvironmentIssuanceGateTests(unittest.TestCase):
    def assess(self, evidence: dict, trusted_anchor=None, deployment_trust_store=None) -> dict:
        return assess_issuance(
            evidence,
            now=NOW,
            trusted_anchor=trusted_anchor,
            deployment_trust_store=deployment_trust_store,
        )

    def assert_hold_code(self, evidence: dict, code: str):
        result = self.assess(evidence)
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertIn(code, result["error_codes"])
        self.assertIsNone(result["normalized_environment"])

    def test_synthetic_control_is_valid_but_never_issuable(self):
        result = self.assess(synthetic_control())
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["error_codes"], ["SYNTHETIC_CONTROL_ONLY"])
        self.assertTrue(result["control_only"])
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")

    def test_naive_evaluation_time_holds_without_assuming_timezone(self):
        result = assess_issuance(
            synthetic_control(),
            now=datetime(2026, 8, 24),
        )
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertEqual(result["error_codes"], ["ISSUANCE_EVALUATION_TIME_INVALID"])
        self.assertIsNone(result["normalized_environment"])

    def test_invalid_evaluation_time_types_hold_without_exception(self):
        invalid_times = ("2026-08-24T00:00:00Z", 0, False, {}, [])
        for invalid_time in invalid_times:
            with self.subTest(invalid_time=invalid_time):
                result = assess_issuance(synthetic_control(), now=invalid_time)
                self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
                self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
                self.assertEqual(
                    result["error_codes"],
                    ["ISSUANCE_EVALUATION_TIME_INVALID"],
                )
                self.assertIsNone(result["normalized_environment"])

    def test_evidence_class_promotion_without_anchor_holds(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        self.assert_hold_code(evidence, "ISSUANCE_TRUST_ANCHOR_MISSING")

    def test_payload_self_declared_approvals_cannot_replace_anchor(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        evidence["trusted_anchor"] = trusted_anchor_for(evidence)
        result = self.assess(evidence)
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_TRUST_ANCHOR_MISSING", result["error_codes"])
        self.assertIn("ISSUANCE_TRUST_ANCHOR_IN_PAYLOAD", result["error_codes"])

    def test_out_of_band_anchor_target_hash_mismatch_holds(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        anchor["raw_manifest_hash"] = f"sha256:{'8' * 64}"
        result = self.assess(evidence, anchor)
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH", result["error_codes"])

    def test_classification_change_invalidates_prior_anchor_target(self):
        evidence = synthetic_control()
        anchor = trusted_anchor_for(evidence)
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        result = self.assess(evidence, anchor)
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH", result["error_codes"])

    def test_out_of_band_anchor_rights_snapshot_mismatch_holds(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        anchor["rights_snapshot_id"] = "other-rights-snapshot"
        result = self.assess(evidence, anchor)
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_TRUST_ANCHOR_RIGHTS_MISMATCH", result["error_codes"])

    def test_exact_match_plain_json_anchor_cannot_authenticate(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        result = self.assess(evidence, trusted_anchor_for(evidence))
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED", result["error_codes"])
        self.assertFalse(result["control_only"])

    def test_attacker_self_issued_anchor_metadata_cannot_authenticate(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        anchor["anchor_id"] = "attacker-selected-anchor"
        anchor["approver"] = "attacker-selected-approver"
        anchor["history_anchor_ref"] = "attacker://self-issued-history"
        result = self.assess(evidence, anchor)
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_AUTHENTICATOR_NOT_CONFIGURED", result["error_codes"])
        self.assertIsNone(result["normalized_environment"])

    def test_deployment_store_exact_match_reaches_test_candidate_only(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        result = self.assess(evidence, anchor, freeze_store(trust_store_for(anchor)))
        self.assertEqual(result["issuance_status"], "ISSUABLE_CANDIDATE")
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertEqual(result["error_codes"], [])
        self.assertIsNone(result["normalized_environment"])

    def test_payload_cannot_supply_trust_store_or_self_allowlist(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        evidence["deployment_trust_store"] = store
        evidence["issuance_allowlist"] = [anchor["anchor_id"]]
        result = self.assess(evidence, trusted_anchor_for(evidence), freeze_store(store))
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_TRUST_STORE_IN_PAYLOAD", result["error_codes"])

    def test_unknown_anchor_id_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        anchor["anchor_id"] = "not-allowlisted"
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_ANCHOR_UNKNOWN", result["error_codes"])
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")

    def test_allowlisted_anchor_payload_tamper_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        anchor["raw_manifest_hash"] = f"sha256:{'8' * 64}"
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH", result["error_codes"])
        self.assertIn("ISSUANCE_TRUST_STORE_ANCHOR_DIGEST_MISMATCH", result["error_codes"])

    def test_stale_trust_store_entry_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor, valid_until="2026-08-23T00:00:00Z")
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_ENTRY_NOT_ACTIVE", result["error_codes"])

    def test_not_yet_active_trust_store_entry_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor, valid_from="2026-08-25T00:00:00Z")
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_ENTRY_NOT_ACTIVE", result["error_codes"])

    def test_revoked_trust_store_entry_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor, revoked=True)
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_ENTRY_REVOKED", result["error_codes"])

    def test_wrong_trust_store_audience_or_scope_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor, audience="OTHER_AUDIENCE")
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_SCOPE_MISMATCH", result["error_codes"])

    def test_duplicate_anchor_id_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        duplicate = deepcopy(store["entries"][0])
        duplicate["anchor_digest"] = f"sha256:{'9' * 64}"
        store["entries"].append(duplicate)
        refresh_store_hash(store)
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_DUPLICATE_ANCHOR_ID", result["error_codes"])

    def test_duplicate_anchor_digest_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        duplicate = deepcopy(store["entries"][0])
        duplicate["anchor_id"] = "second-anchor-id"
        store["entries"].append(duplicate)
        refresh_store_hash(store)
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_DUPLICATE_ANCHOR_DIGEST", result["error_codes"])

    def test_store_snapshot_identity_or_hash_tamper_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        store["snapshot_id"] = "fixture://deployment-trust-store/tampered"
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_SNAPSHOT_MISMATCH", result["error_codes"])

    def test_malformed_or_unknown_trust_store_fields_are_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor)
        store["entries"][0]["unknown"] = {"nested": "field"}
        refresh_store_hash(store)
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_STORE_INVALID", result["error_codes"])

    def test_evidence_class_change_invalidates_allowlisted_anchor(self):
        evidence = synthetic_control()
        anchor = trusted_anchor_for(evidence)
        store = trust_store_for(anchor, evidence_class="SYNTHETIC_CONTROL")
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        result = self.assess(evidence, anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH", result["error_codes"])
        self.assertIn("ISSUANCE_TRUST_STORE_EVIDENCE_CLASS_MISMATCH", result["error_codes"])

    def test_past_anchor_replay_against_new_review_is_rejected(self):
        old_evidence = synthetic_control()
        old_evidence["evidence_class"] = "ACTUAL_REVIEW"
        old_anchor = trusted_anchor_for(old_evidence)
        store = trust_store_for(old_anchor)
        new_evidence = deepcopy(old_evidence)
        new_evidence["provider"]["provider_job_reference"] = "synthetic-provider-job-new"
        result = self.assess(new_evidence, old_anchor, freeze_store(store))
        self.assertIn("ISSUANCE_TRUST_ANCHOR_TARGET_MISMATCH", result["error_codes"])

    def test_raw_mutable_store_argument_is_rejected(self):
        evidence = synthetic_control()
        evidence["evidence_class"] = "ACTUAL_REVIEW"
        anchor = trusted_anchor_for(evidence)
        result = self.assess(evidence, anchor, trust_store_for(anchor))
        self.assertEqual(result["issuance_status"], "HOLD_NOT_ISSUED")
        self.assertIn("ISSUANCE_TRUST_STORE_INVALID", result["error_codes"])

    def test_missing_provider_reference_holds(self):
        evidence = synthetic_control()
        evidence["provider"]["provider_job_reference"] = None
        self.assert_hold_code(evidence, "PROVIDER_JOB_REFERENCE_MISSING")

    def test_forged_provider_reference_holds(self):
        evidence = synthetic_control()
        evidence["provider"]["reference_status"] = "SELF_ASSERTED"
        self.assert_hold_code(evidence, "PROVIDER_JOB_REFERENCE_UNVERIFIED")

    def test_missing_rights_action_holds(self):
        evidence = synthetic_control()
        evidence["rights_snapshot"]["action_grants"].pop()
        self.assert_hold_code(evidence, "RIGHTS_ACTION_GRANT_MISSING")

    def test_expired_rights_action_holds(self):
        evidence = synthetic_control()
        evidence["rights_snapshot"]["action_grants"][0]["valid_until"] = "2026-08-23T00:00:00Z"
        self.assert_hold_code(evidence, "RIGHTS_ACTION_GRANT_STALE")

    def test_wrong_rights_scope_holds(self):
        evidence = synthetic_control()
        evidence["rights_snapshot"]["action_grants"][0]["scope_hash"] = f"sha256:{'9' * 64}"
        self.assert_hold_code(evidence, "RIGHTS_ACTION_SCOPE_MISMATCH")

    def test_manifest_generation_mismatch_holds(self):
        evidence = synthetic_control()
        evidence["raw_manifest"]["storage_generation"] = "2"
        self.assert_hold_code(evidence, "RAW_GENERATION_MISMATCH")

    def test_manifest_bundle_hash_mismatch_holds(self):
        evidence = synthetic_control()
        evidence["artifact_identity"]["artifact_set_hash"] = f"sha256:{'8' * 64}"
        self.assert_hold_code(evidence, "RAW_BUNDLE_HASH_MISMATCH")

    def test_manifest_rights_binding_mismatch_holds(self):
        evidence = synthetic_control()
        evidence["raw_manifest"]["rights_snapshot_id"] = "other-rights"
        self.assert_hold_code(evidence, "RAW_RIGHTS_SNAPSHOT_MISMATCH")

    def test_source_role_identity_reuse_holds(self):
        evidence = synthetic_control()
        required = [item for item in evidence["artifact_identity"]["artifacts"] if item["role"] in REQUIRED_ROLES]
        required[1]["identity_sha256"] = required[0]["identity_sha256"]
        self.assert_hold_code(evidence, "ARTIFACT_ID_REUSED_ACROSS_ROLES")

    def test_model_version_drift_holds(self):
        evidence = synthetic_control()
        evidence["model_conditions"]["platform_build"] = "drifted-build"
        self.assert_hold_code(evidence, "MODEL_VERSION_DRIFT")

    def test_crosscheck_missing_holds(self):
        evidence = synthetic_control()
        evidence["scientific_crosscheck"] = {"status": "NOT_EVALUATED"}
        self.assert_hold_code(evidence, "SCIENTIFIC_CROSSCHECK_NOT_EVALUATED")

    def test_crosscheck_failure_holds(self):
        evidence = synthetic_control()
        evidence["scientific_crosscheck"]["status"] = "FAILED"
        self.assert_hold_code(evidence, "SCIENTIFIC_CROSSCHECK_FAILED")

    def test_emission_authorization_tamper_holds(self):
        evidence = synthetic_control()
        evidence["emission_authorization"]["approval_target_hash"] = f"sha256:{'0' * 64}"
        self.assert_hold_code(evidence, "EMISSION_AUTHORIZATION_TARGET_MISMATCH")

    def test_emission_authorization_status_tamper_holds(self):
        evidence = synthetic_control()
        evidence["emission_authorization"]["status"] = "APPROVED_TAMPERED"
        self.assert_hold_code(evidence, "CONTRACT_EMISSION_NOT_APPROVED")

    def test_unapproved_storage_and_manifest_hold(self):
        evidence = synthetic_control()
        evidence["approved_storage"] = {"status": "LOCAL_FILESYSTEM_ONLY", "immutable": False}
        evidence["raw_manifest"] = {"status": "MISSING"}
        self.assert_hold_code(evidence, "RAW_ARTIFACT_MANIFEST_V2_MISSING")
        self.assert_hold_code(evidence, "APPROVED_STORAGE_UNAVAILABLE")

    def test_malformed_rights_action_fails_without_exception(self):
        evidence = synthetic_control()
        evidence["rights_snapshot"]["action_grants"][0]["action"] = []
        self.assert_hold_code(evidence, "RIGHTS_ACTION_SET_INVALID")

    def test_malformed_artifact_role_fails_without_exception(self):
        evidence = synthetic_control()
        evidence["artifact_identity"]["artifacts"][0]["role"] = []
        self.assert_hold_code(evidence, "ARTIFACT_IDENTITY_NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
