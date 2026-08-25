from __future__ import annotations

import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from intake_local_document_candidate import intake_document  # noqa: E402
from run_evidence_console import local_intake_events  # noqa: E402
from spectra_document_adapter import link_event_candidates  # noqa: E402


def candidate(text: str, field: str, value: str, occurrence: int = 0) -> dict:
    start = -1
    cursor = 0
    for _ in range(occurrence + 1):
        start = text.index(value, cursor)
        cursor = start + len(value)
    return {
        "candidate_id": f"candidate-{field.lower()}-{start}",
        "field": field,
        "value": value,
        "unit": None,
        "source_span": {"start": start, "end": start + len(value)},
    }


class EvidenceCandidateLinkageTests(unittest.TestCase):
    def test_groups_only_same_line_candidates_and_reports_missing_fields(self) -> None:
        text = (
            "TID: 25 krad(Si)\n"
            "SEU discussed\n"
            "SEL fluence 1e10 particles/cm2 sample size 3 observed events 0\n"
        )
        candidates = [
            candidate(text, "EVIDENCE_EVENT_MENTION", "TID"),
            candidate(text, "TID_DOSE", "25 krad(Si)"),
            candidate(text, "EVIDENCE_EVENT_MENTION", "SEU"),
            candidate(text, "EVIDENCE_EVENT_MENTION", "SEL"),
            candidate(text, "PARTICLE_FLUENCE", "1e10 particles/cm2"),
            candidate(text, "SAMPLE_SIZE", "3"),
            candidate(text, "OBSERVED_EVENT_COUNT", "0"),
        ]

        receipt = link_event_candidates(text, candidates)

        self.assertEqual(receipt["linkage_status"], "PARTIAL_EVENT_CANDIDATES")
        self.assertEqual(receipt["event_group_count"], 3)
        by_event = {item["event_type"]: item for item in receipt["event_groups"]}
        self.assertEqual(by_event["TID"]["status"], "REQUIRED_FIELDS_PRESENT")
        self.assertEqual(by_event["SEU"]["missing_fields"], ["SEE_CROSS_SECTION"])
        self.assertEqual(by_event["SEL"]["status"], "REQUIRED_FIELDS_PRESENT")
        self.assertFalse(receipt["used_for_decision"])
        self.assertEqual(receipt["assurance_decision"], "HOLD")

    def test_does_not_link_measurement_from_another_line(self) -> None:
        text = "SEU\n1e-6 cm2/device\n"
        candidates = [
            candidate(text, "EVIDENCE_EVENT_MENTION", "SEU"),
            candidate(text, "SEE_CROSS_SECTION", "1e-6 cm2/device"),
        ]

        receipt = link_event_candidates(text, candidates)

        group = receipt["event_groups"][0]
        self.assertEqual(group["status"], "MISSING_REQUIRED_FIELDS")
        self.assertEqual(group["linked_candidates"], [])
        self.assertEqual(len(receipt["unassigned_measurement_candidates"]), 1)

    def test_links_one_unique_document_tid_dose_across_lines(self) -> None:
        text = "TID test summary\nPublished result: 39 krad(Si)\n"
        candidates = [
            candidate(text, "EVIDENCE_EVENT_MENTION", "TID"),
            candidate(text, "TID_DOSE", "39 krad(Si)"),
        ]

        receipt = link_event_candidates(text, candidates)

        group = receipt["event_groups"][0]
        self.assertEqual(group["status"], "REQUIRED_FIELDS_PRESENT")
        self.assertEqual(
            group["linked_candidates"][0]["link_basis"],
            "UNIQUE_DOCUMENT_TID_DOSE",
        )

    def test_repeated_document_tid_doses_are_not_guessed(self) -> None:
        text = "TID test summary\n10 krad(Si)\n20 krad(Si)\n"
        candidates = [
            candidate(text, "EVIDENCE_EVENT_MENTION", "TID"),
            candidate(text, "TID_DOSE", "10 krad(Si)"),
            candidate(text, "TID_DOSE", "20 krad(Si)"),
        ]

        receipt = link_event_candidates(text, candidates)

        self.assertEqual(
            receipt["event_groups"][0]["status"], "MISSING_REQUIRED_FIELDS"
        )
        self.assertEqual(len(receipt["unassigned_measurement_candidates"]), 2)

    def test_local_parser_extracts_observed_event_count_into_linkage(self) -> None:
        content = (
            b"Example Semiconductor EX-100-A\n"
            b"SEL 1e10 particles/cm2 sample size: 3 observed events: 0\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "sel-test.txt"
            path.write_bytes(content)
            receipt = intake_document(
                path,
                expected_part="EX-100-A",
                manufacturer="Example Semiconductor",
                local_review_rights_confirmed=True,
            )

        fields = set(receipt["candidate_fields"])
        self.assertIn("OBSERVED_EVENT_COUNT", fields)
        group = receipt["evidence_candidate_linkage"]["event_groups"][0]
        self.assertEqual(group["event_type"], "SEL")
        self.assertEqual(group["status"], "REQUIRED_FIELDS_PRESENT")

    def test_console_emits_review_linkage_without_promoting_decision(self) -> None:
        events = list(
            local_intake_events(
                "tid-test.txt",
                b"Example Semiconductor EX-100-A TID 25 krad(Si)\n",
                expected_part="EX-100-A",
                manufacturer="Example Semiconductor",
                local_review_rights_confirmed=True,
            )
        )

        linked = next(item for item in events if item["event"] == "evidence_candidates.grouped")
        self.assertEqual(linked["status"], "VALID")
        self.assertEqual(linked["evidence"]["complete_event_group_count"], 1)
        self.assertFalse(linked["evidence"]["used_for_decision"])
        self.assertEqual(linked["evidence"]["assurance_decision"], "HOLD")
        self.assertEqual(events[-1]["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
