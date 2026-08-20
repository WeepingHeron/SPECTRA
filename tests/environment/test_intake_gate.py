from __future__ import annotations

import json
import hashlib
import sys
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_env_adapter import assess_import  # noqa: E402
from spectra_env_adapter.gate import REFERENCE_MISSION, REQUIRED_ROLES, _rights_codes  # noqa: E402


SYNTHETIC_DOSE_OUTPUT = """'SPENVIS 4.6.14.3582 - 20-Aug-2026 00:00:00'
'PRJ_DEF', -1, 'SYNTHETIC_PROJECT'
'PRJ_HDR', -1, 'SYNTHETIC INTAKE FIXTURE'
'MIS_DUR', 1, 3.650000E+02, 'days'
'PLT_HDR', -1, '4pi Dose at Centre of Al Spheres'
'Mission start: 01/01/2027 00:00:00'
'Mission end: 01/01/2028 00:00:00'
'Thick', 'mm', 1, 'Aluminium Absorber Thickness'
'Dose', 'rad', 5, 'Dose in Si'
1.0, 10, 1, 2, 3, 4
2.0, 20, 2, 3, 4, 5
3.0, 30, 3, 4, 5, 6
4.0, 40, 4, 5, 6, 7
"""


class EnvironmentIntakeGateTests(unittest.TestCase):
    def assess(self, request_path: Path):
        return assess_import(
            request_path,
            schema_root=ROOT / "schemas",
            repository_root=ROOT,
            now=datetime(2026, 8, 20, tzinfo=timezone.utc),
        )

    def make_bundle(self, tmp: str) -> tuple[Path, dict, dict]:
        raw_root = Path(tmp) / "bundle"
        raw_root.mkdir()
        artifacts = []
        artifact_files = []
        for index, role in enumerate(sorted(REQUIRED_ROLES), start=1):
            relative_path = f"raw/{index:02d}-{role.lower()}.txt"
            path = raw_root / relative_path
            path.parent.mkdir(exist_ok=True)
            content = SYNTHETIC_DOSE_OUTPUT if role == "DOSE_OUTPUT" else f"synthetic {role}\n"
            path.write_text(content, encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            artifact_id = f"artifact-{index:02d}"
            artifacts.append({
                "artifact_id": artifact_id,
                "artifact_revision_id": f"revision-{index:02d}",
                "tenant_id": "synthetic-tenant",
                "zone": "Z5_SYNTHETIC",
                "storage_ref": {
                    "project_id": "synthetic-project",
                    "bucket_id": "synthetic-bucket",
                    "object_name": relative_path,
                    "generation": str(index),
                },
                "integrity": {
                    "sha256": f"sha256:{digest}",
                    "byte_size": path.stat().st_size,
                    "declared_mime": "text/plain",
                    "detected_mime": "text/plain",
                },
                "source": {"locator": f"fixture://{relative_path}", "retrieved_at": "2026-08-20T00:02:00Z"},
                "rights_snapshot_id": "synthetic-rights-001",
                "validation": {
                    "quarantine_status": "VALIDATED",
                    "malware_scan": {
                        "status": "PASS", "engine": "synthetic-scanner",
                        "engine_version": "1", "scanned_at": "2026-08-20T00:03:00Z",
                    },
                    "mime_check": "MATCH", "hash_check": "MATCH",
                },
                "lineage": {"derived_record_ids": [], "deletion_state": "ACTIVE"},
            })
            artifact_files.append({"role": role, "artifact_id": artifact_id, "path": relative_path})

        manifest = {
            "contract_version": "2.0.0", "manifest_id": "synthetic-manifest-001",
            "run_id": "synthetic-run-001", "tenant_id": "synthetic-tenant", "zone": "Z5_SYNTHETIC",
            "bundle_hash": f"sha256:{'8' * 64}", "create_precondition": "IF_GENERATION_MATCH_0",
            "provider": {
                "platform_name": "SPENVIS", "platform_version": "4.6.14.3582",
                "platform_build": "4.6.14.3582", "provider_job_reference": "synthetic-job-001",
            },
            "timestamps": {
                "submitted_at": "2026-08-20T00:00:00Z", "completed_at": "2026-08-20T00:01:00Z",
                "downloaded_at": "2026-08-20T00:02:00Z",
            },
            "rights_snapshot": {
                "rights_snapshot_id": "synthetic-rights-001", "snapshot_version": "1",
                "status": "PRIVATE_COPY_ALLOWED", "tenant_id": "synthetic-tenant",
                "approval_target_hash": f"sha256:{'1' * 64}", "valid_from": "2026-08-19T00:00:00Z",
                "action_grants": [
                    {"action": action, "grant_status": "ALLOWED", "scope_hash": f"sha256:{'2' * 64}"}
                    for action in ("FETCH", "PRIVATE_STORE")
                ],
                "history_anchor_ref": "fixture://rights-history",
            },
            "artifacts": artifacts,
            "parser": {
                "name": "synthetic-parser", "version": "1", "commit": "test-only",
                "input_bundle_hash": f"sha256:{'8' * 64}", "output_hash": f"sha256:{'3' * 64}",
            },
            "metadata": {
                "data_class": "SYNTHETIC", "version": "2.0.0", "created_at": "2026-08-20T00:00:00Z",
                "content_hash": f"sha256:{'4' * 64}", "review_status": "READY_FOR_REVIEW",
                "calculation_run": {
                    "run_id": "synthetic-run-001", "engine": "synthetic-fixture-generator", "engine_version": "1",
                    "input_hash": f"sha256:{'5' * 64}", "output_hash": f"sha256:{'4' * 64}",
                    "executed_at": "2026-08-20T00:00:00Z",
                },
            },
        }
        request = {
            "mission": REFERENCE_MISSION, "raw_root": str(raw_root),
            "manifest_path": "manifest.json", "artifact_files": artifact_files,
        }
        return raw_root, manifest, request

    def write_case(self, tmp: str, manifest: dict, request: dict) -> Path:
        raw_root = Path(request["raw_root"])
        (raw_root / request["manifest_path"]).write_text(json.dumps(manifest), encoding="utf-8")
        request_path = Path(tmp) / "request.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        return request_path

    def assert_provenance_code(self, tmp: str, manifest: dict, request: dict, code: str):
        result = self.assess(self.write_case(tmp, manifest, request))
        self.assertEqual(result["gate_status"], "HOLD")
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertIn(code, result["error_codes"])
        self.assertIsNone(result["normalized_environment"])

    def test_missing_request_holds_without_creating_artifact(self):
        result = self.assess(Path("/definitely/not/a/spenvis-request.json"))
        self.assertEqual(result["gate_status"], "HOLD")
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertIn("IMPORT_REQUEST_MISSING", result["error_codes"])
        self.assertIsNone(result["normalized_environment"])

    def test_reference_mission_mismatch_is_out_of_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            request_path.write_text(
                json.dumps({"mission": REFERENCE_MISSION | {"segment_count": 2}}),
                encoding="utf-8",
            )
            result = self.assess(request_path)
        self.assertEqual(result["processing_status"], "OUT_OF_MODEL_SCOPE")
        self.assertIn("REFERENCE_MISSION_MISMATCH", result["error_codes"])

    def test_raw_bundle_inside_repository_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            request_path.write_text(
                json.dumps({
                    "mission": REFERENCE_MISSION,
                    "raw_root": str(ROOT / "environment"),
                    "manifest_path": "manifest.json",
                }),
                encoding="utf-8",
            )
            result = self.assess(request_path)
        self.assertIn("RAW_BUNDLE_INSIDE_GIT_WORKTREE", result["error_codes"])

    def test_unconfirmed_fetch_and_storage_rights_hold(self):
        rights = {
            "status": "RIGHTS_UNCONFIRMED",
            "valid_from": "2026-08-19T00:00:00Z",
            "action_grants": [
                {"action": "FETCH", "grant_status": "UNCONFIRMED"},
                {"action": "PRIVATE_STORE", "grant_status": "UNCONFIRMED"},
            ],
        }
        codes = _rights_codes(rights, datetime(2026, 8, 20, tzinfo=timezone.utc))
        self.assertEqual(codes, {"RIGHTS_GATE_HOLD", "RIGHTS_ACTION_GRANT_MISSING"})

    def test_expired_rights_are_stale(self):
        rights = {
            "status": "PRIVATE_COPY_ALLOWED",
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-08-19T00:00:00Z",
            "action_grants": [
                {"action": "FETCH", "grant_status": "ALLOWED"},
                {"action": "PRIVATE_STORE", "grant_status": "ALLOWED"},
            ],
        }
        codes = _rights_codes(rights, datetime(2026, 8, 20, tzinfo=timezone.utc))
        self.assertEqual(codes, {"RIGHTS_SNAPSHOT_NOT_ACTIVE"})

    def test_required_role_missing_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"].pop()
            self.assert_provenance_code(tmp, manifest, request, "SOURCE_ROLE_MISSING")

    def test_required_role_duplicated_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"].append(deepcopy(request["artifact_files"][0]))
            self.assert_provenance_code(tmp, manifest, request, "SOURCE_ROLE_DUPLICATED")

    def test_artifact_id_reused_across_roles_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"][1]["artifact_id"] = request["artifact_files"][0]["artifact_id"]
            self.assert_provenance_code(tmp, manifest, request, "ARTIFACT_ID_REUSED_ACROSS_ROLES")

    def test_resolved_path_reused_across_roles_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"][1]["path"] = request["artifact_files"][0]["path"]
            self.assert_provenance_code(tmp, manifest, request, "RESOLVED_PATH_REUSED_ACROSS_ROLES")

    def test_duplicate_artifact_id_in_manifest_fails_before_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            duplicate = deepcopy(manifest["artifacts"][0])
            duplicate["artifact_revision_id"] = "duplicate-revision"
            duplicate["storage_ref"]["generation"] = "99"
            manifest["artifacts"].append(duplicate)
            self.assert_provenance_code(tmp, manifest, request, "DUPLICATE_ARTIFACT_ID_IN_MANIFEST")

    def test_path_alias_resolving_to_same_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            original = Path(request["artifact_files"][0]["path"])
            request["artifact_files"][1]["path"] = str(original.parent / "alias" / ".." / original.name)
            self.assert_provenance_code(tmp, manifest, request, "RESOLVED_PATH_REUSED_ACROSS_ROLES")

    def test_symlink_resolving_to_same_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw_root, manifest, request = self.make_bundle(tmp)
            original = raw_root / request["artifact_files"][0]["path"]
            alias = raw_root / "raw" / "symlink-alias.txt"
            alias.symlink_to(original)
            request["artifact_files"][1]["path"] = str(alias.relative_to(raw_root))
            self.assert_provenance_code(tmp, manifest, request, "RESOLVED_PATH_REUSED_ACROSS_ROLES")

    def test_unexpected_role_fails_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"].append({
                "role": "UNEXPECTED_ROLE", "artifact_id": "artifact-01",
                "path": request["artifact_files"][0]["path"],
            })
            self.assert_provenance_code(tmp, manifest, request, "SOURCE_ROLE_UNEXPECTED")

    def test_invalid_artifact_index_type_fails_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"][0] = {"role": request["artifact_files"][0]["role"]}
            self.assert_provenance_code(tmp, manifest, request, "ARTIFACT_INDEX_INVALID")

    def test_embedded_nul_path_fails_without_exception(self):
        for contaminated_path in ("\0bad-path", "bad\0path", "bad-path\0"):
            with self.subTest(path_position=contaminated_path.index("\0")):
                with tempfile.TemporaryDirectory() as tmp:
                    _, manifest, request = self.make_bundle(tmp)
                    request["artifact_files"][0]["path"] = contaminated_path
                    self.assert_provenance_code(tmp, manifest, request, "ARTIFACT_PATH_INVALID")

    def test_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw_root, manifest, request = self.make_bundle(tmp)
            (raw_root / request["artifact_files"][0]["path"]).write_text("tampered\n", encoding="utf-8")
            self.assert_provenance_code(tmp, manifest, request, "RAW_ARTIFACT_HASH_MISMATCH")

    def test_file_operation_os_error_fails_without_exception(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request_path = self.write_case(tmp, manifest, request)
            with patch("spectra_env_adapter.gate._sha256", side_effect=PermissionError("denied")):
                result = self.assess(request_path)
        self.assertEqual(result["processing_status"], "PROVENANCE_FAILURE")
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertIn("RAW_ARTIFACT_UNREADABLE", result["error_codes"])
        self.assertIsNone(result["normalized_environment"])

    def test_path_outside_bundle_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            outside = Path(tmp) / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            request["artifact_files"][0]["path"] = "../outside.txt"
            self.assert_provenance_code(tmp, manifest, request, "RAW_ARTIFACT_MISSING")

    def test_missing_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            request["artifact_files"][0]["path"] = "raw/does-not-exist.txt"
            self.assert_provenance_code(tmp, manifest, request, "RAW_ARTIFACT_MISSING")

    def test_valid_synthetic_structure_reaches_emission_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest, request = self.make_bundle(tmp)
            result = self.assess(self.write_case(tmp, manifest, request))
        self.assertEqual(result["processing_status"], "MODEL_FAILURE")
        self.assertEqual(result["error_codes"], ["CONTRACT_EMISSION_NOT_APPROVED"])
        self.assertEqual(result["parsed_candidate_count"], 4)


if __name__ == "__main__":
    unittest.main()
