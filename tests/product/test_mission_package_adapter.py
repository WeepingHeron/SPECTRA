from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from spectra_document_adapter import MissionPackageError, adapt_mission_package  # noqa: E402
from spectra_sim import synthesize_mission_case  # noqa: E402


PACKAGE = ROOT / "demo/data/mission-package"


def documents() -> list[dict]:
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    return [
        {
            "role": item["role"],
            "document_id": item["document_id"],
            "declared_sha256": item["sha256"],
            "content": (PACKAGE / item["filename"]).read_bytes(),
        }
        for item in manifest["documents"]
    ]


def trust_contracts() -> tuple[dict, dict, dict]:
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    policy = json.loads((PACKAGE / "approval-policy.json").read_text(encoding="utf-8"))
    trust_store = json.loads(
        (ROOT / "simulation/config/mission-package-trust-store.json").read_text(encoding="utf-8")
    )
    return manifest, policy, trust_store


def adapt(source_documents: list[dict] | None = None) -> dict:
    manifest, policy, trust_store = trust_contracts()
    return adapt_mission_package(
        source_documents or documents(),
        mission_case_id="console-mission-case",
        raw_manifest=manifest,
        approval_policy=policy,
        trust_store=trust_store,
    )


def canonical_hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class MissionPackageAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.model = json.loads(
            (ROOT / "simulation/config/synthetic-model.json").read_text(encoding="utf-8")
        )

    def test_raw_documents_are_hash_bound_and_linked_to_core(self) -> None:
        receipt = adapt()
        self.assertEqual(receipt["status"], "SOURCE_BOUND")
        self.assertEqual(receipt["document_count"], 3)
        self.assertTrue(
            all(item["hash_status"] == "MATCH" for item in receipt["document_receipts"])
        )
        self.assertTrue(
            all(
                binding["source_locator"].startswith("synthetic://mission-package/")
                for item in receipt["document_receipts"]
                for binding in item["field_bindings"]
            )
        )
        result = synthesize_mission_case(receipt["mission_case"], self.model)
        self.assertEqual(result["questions"]["exact_part_identity"]["status"], "EXACT_MATCH")
        self.assertEqual(result["questions"]["event_coverage"]["status"], "COMPLETE")
        self.assertEqual(result["questions"]["mission_test_applicability"]["status"], "NOT_EVALUATED")
        self.assertEqual(result["assurance_decision"], "HOLD")
        binding = receipt["mission_case"]["evidence_binding"]
        self.assertEqual(len(binding["document_hashes"]), 3)
        self.assertEqual(
            {item["role"] for item in binding["document_hashes"]},
            {"MISSION_CONDITIONS", "APPROVED_BOM", "RADIATION_TEST"},
        )

    def test_changed_document_is_rejected_before_parsing(self) -> None:
        attacked = documents()
        attacked[2] = copy.deepcopy(attacked[2])
        attacked[2]["content"] += b"\n# tampered\n"
        with self.assertRaisesRegex(MissionPackageError, "DOCUMENT_HASH_MISMATCH"):
            adapt(attacked)

    def test_missing_field_and_unknown_field_fail_closed(self) -> None:
        for replacement, code in (
            (b"PACKAGE: QFP-64\n", "DOCUMENT_REQUIRED_FIELD_MISSING"),
            (b"UNKNOWN: injected\n", "DOCUMENT_FIELD_FORBIDDEN"),
        ):
            attacked = documents()
            attacked[1] = copy.deepcopy(attacked[1])
            attacked[1]["content"] = replacement
            attacked[1]["declared_sha256"] = "sha256:" + hashlib.sha256(replacement).hexdigest()
            with self.subTest(code=code):
                with self.assertRaisesRegex(MissionPackageError, code):
                    adapt(attacked)

    def test_rehashed_self_approval_cannot_replace_external_anchor(self) -> None:
        attacked = documents()
        attacked[1] = copy.deepcopy(attacked[1])
        attacked[1]["content"] = attacked[1]["content"].replace(
            b"MANUFACTURER: Example Semiconductor", b"MANUFACTURER: Forged Semiconductor"
        )
        attacked[1]["declared_sha256"] = "sha256:" + hashlib.sha256(
            attacked[1]["content"]
        ).hexdigest()
        manifest, policy, trust_store = trust_contracts()
        manifest["documents"][1]["sha256"] = attacked[1]["declared_sha256"]
        manifest["bundle_hash"] = canonical_hash(
            {
                "manifest_id": manifest["manifest_id"],
                "mission_case_id": manifest["mission_case_id"],
                "documents": [
                    {key: item[key] for key in ("role", "document_id", "sha256")}
                    for item in manifest["documents"]
                ],
            }
        )
        manifest["rights_snapshot"]["approval_target_hash"] = manifest["bundle_hash"]
        for grant in manifest["rights_snapshot"]["action_grants"]:
            grant["scope_hash"] = manifest["bundle_hash"]
        # Even after a separately authorized rights rebind, the deployment-owned
        # approval anchor still pins the exact approved BOM bytes.
        trust_store["rights_snapshot"]["bundle_hash"] = manifest["bundle_hash"]
        with self.assertRaisesRegex(MissionPackageError, "APPROVAL_TRUST_ANCHOR_MISMATCH"):
            adapt_mission_package(
                attacked,
                mission_case_id="console-mission-case",
                raw_manifest=manifest,
                approval_policy=policy,
                trust_store=trust_store,
            )

    def test_current_contract_cannot_bypass_evidence_binding(self) -> None:
        case = copy.deepcopy(adapt()["mission_case"])
        del case["evidence_binding"]
        result = synthesize_mission_case(case, self.model)
        self.assertEqual(result["processing_status"], "INVALID_INPUT")
        self.assertIn("EVIDENCE_BINDING_MISSING", result["stable_codes"])

    def test_evidence_binding_changes_core_hashes(self) -> None:
        receipt = adapt()
        baseline = synthesize_mission_case(receipt["mission_case"], self.model)
        changed_case = copy.deepcopy(receipt["mission_case"])
        changed_case["evidence_binding"]["trust_store_hash"] = "sha256:" + "f" * 64
        changed = synthesize_mission_case(changed_case, self.model)
        self.assertNotEqual(baseline["input_hash"], changed["input_hash"])
        self.assertNotEqual(baseline["output_hash"], changed["output_hash"])


if __name__ == "__main__":
    unittest.main()
