from __future__ import annotations

import pathlib
import json
import hashlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_evidence_console import evaluate_uploaded_candidate_bundle  # noqa: E402


def documents(test_part: str = "EX-100-A") -> list[dict]:
    return [
        {
            "role": "MISSION_CONDITIONS",
            "filename": "mission.txt",
            "content": (
                b"Mission name: DemoSat\n"
                b"Orbit: LEO\n"
                b"Mission duration: 2 years\n"
                b"Shielding thickness: 2 mm Al\n"
            ),
        },
        {
            "role": "PART_SPEC",
            "filename": "part.txt",
            "content": (
                b"Manufacturer: Example Semiconductor\n"
                b"Orderable part number: EX-100-A\n"
            ),
        },
        {
            "role": "RADIATION_TEST",
            "filename": "test.txt",
            "content": (
                "Manufacturer: Example Semiconductor\n"
                f"Orderable part number: {test_part}\n"
                "TID test result: 25 krad(Si)\n"
            ).encode("utf-8"),
        },
    ]


class CandidateBundleTests(unittest.TestCase):
    def test_three_documents_cross_link_candidates_but_remain_hold(self) -> None:
        payload = evaluate_uploaded_candidate_bundle(
            documents(),
            expected_part="EX-100-A",
            manufacturer="Example Semiconductor",
            local_review_rights_confirmed=True,
        )

        result = payload["result"]
        self.assertEqual(result["processing_status"], "VALID")
        self.assertEqual(result["bundle_status"], "CANDIDATES_LINKED_FOR_REVIEW")
        self.assertEqual(
            result["questions"]["part_test_identity"]["status"],
            "EXACT_TEXT_MATCH",
        )
        self.assertEqual(
            result["questions"]["event_evidence_candidates"]["complete_events"],
            ["TID"],
        )
        self.assertEqual(result["assurance_decision"], "HOLD")
        self.assertFalse(result["used_for_decision"])
        self.assertEqual(payload["events"][-1]["event"], "decision.completed")
        self.assertEqual(payload["events"][-1]["status"], "HOLD")
        self.assertFalse(payload["boundary"]["raw_documents_persisted"])
        self.assertFalse(payload["boundary"]["review_packet_persisted"])
        packet = payload["review_packet"]
        self.assertEqual(packet["packet_class"], "CANDIDATE_REVIEW_ONLY")
        self.assertEqual(len(packet["document_hashes"]), 3)
        self.assertEqual(
            packet["part_test_identity_review"]["status"],
            "EXACT_TEXT_MATCH",
        )
        self.assertEqual(packet["event_evidence_review"]["complete_events"], ["TID"])
        self.assertEqual(packet["final_review"]["assurance_decision"], "HOLD")
        self.assertTrue(packet["review_packet_sha256"].startswith("sha256:"))
        unsigned = dict(packet)
        packet_hash = unsigned.pop("review_packet_sha256")
        canonical = json.dumps(
            unsigned,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(packet_hash, "sha256:" + hashlib.sha256(canonical).hexdigest())
        serialized = json.dumps(packet).lower()
        for forbidden in ("raw_text", "filename", "local_path"):
            self.assertNotIn(f'"{forbidden}"', serialized)

    def test_conflicting_declared_test_identity_is_reported_not_inferred(self) -> None:
        payload = evaluate_uploaded_candidate_bundle(
            documents("EX-200-B"),
            expected_part="EX-100-A",
            manufacturer="Example Semiconductor",
            local_review_rights_confirmed=True,
        )

        identity = payload["result"]["questions"]["part_test_identity"]
        self.assertEqual(identity["status"], "CONFLICT")
        part_number = next(
            item
            for item in identity["fields"]
            if item["field"] == "ORDERABLE_PART_NUMBER"
        )
        self.assertEqual(part_number["part_candidates"], ["EX-100-A"])
        self.assertEqual(part_number["test_candidates"], ["EX-200-B"])
        self.assertEqual(payload["result"]["bundle_status"], "CANDIDATE_CONFLICT")
        self.assertEqual(payload["result"]["assurance_decision"], "HOLD")
        packet_identity = payload["review_packet"]["part_test_identity_review"]
        self.assertEqual(packet_identity["status"], "CONFLICT")

    def test_review_packet_is_deterministic_and_changes_with_source(self) -> None:
        first = evaluate_uploaded_candidate_bundle(
            documents(),
            expected_part="EX-100-A",
            manufacturer="Example Semiconductor",
            local_review_rights_confirmed=True,
        )["review_packet"]
        second = evaluate_uploaded_candidate_bundle(
            documents(),
            expected_part="EX-100-A",
            manufacturer="Example Semiconductor",
            local_review_rights_confirmed=True,
        )["review_packet"]
        conflict = evaluate_uploaded_candidate_bundle(
            documents("EX-200-B"),
            expected_part="EX-100-A",
            manufacturer="Example Semiconductor",
            local_review_rights_confirmed=True,
        )["review_packet"]

        self.assertEqual(first, second)
        self.assertNotEqual(first["review_packet_sha256"], conflict["review_packet_sha256"])

    def test_unconfirmed_rights_blocks_all_three_document_intakes(self) -> None:
        payload = evaluate_uploaded_candidate_bundle(
            documents(),
            expected_part="EX-100-A",
            manufacturer="Example Semiconductor",
            local_review_rights_confirmed=False,
        )

        self.assertEqual(payload["result"]["processing_status"], "DATA_UNAVAILABLE")
        self.assertEqual(payload["result"]["bundle_status"], "DOCUMENT_INTAKE_BLOCKED")
        self.assertTrue(
            all(
                item["processing_status"] == "PROVENANCE_FAILURE"
                for item in payload["result"]["document_receipts"]
            )
        )
        self.assertEqual(payload["result"]["assurance_decision"], "HOLD")

    def test_duplicate_or_missing_role_set_is_rejected(self) -> None:
        malformed = documents()
        malformed[-1]["role"] = "PART_SPEC"
        with self.assertRaisesRegex(ValueError, "DOCUMENT_ROLE_SET_INVALID"):
            evaluate_uploaded_candidate_bundle(
                malformed,
                expected_part="EX-100-A",
                manufacturer="Example Semiconductor",
                local_review_rights_confirmed=True,
            )


if __name__ == "__main__":
    unittest.main()
