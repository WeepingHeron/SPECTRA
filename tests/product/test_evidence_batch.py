#!/usr/bin/env python3
"""Changed-scope tests for the batch evidence table and early architecture slide."""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from run_evidence_console import local_intake_events  # noqa: E402


class EvidenceBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (ROOT / "demo" / "evidence-batch.html").read_text(encoding="utf-8")
        cls.deck = (ROOT / "demo" / "index.html").read_text(encoding="utf-8")
        cls.manifest = json.loads(
            (ROOT / "demo" / "data" / "synthetic-batch-manifest.json").read_text(
                encoding="utf-8"
            )
        )

    def test_batch_ui_is_multi_file_fail_closed_and_safe(self) -> None:
        for marker in (
            'type="file" multiple',
            "LOCAL BATCH · NO DOCUMENT AI CALL",
            "추출된 근거 · 원문 위치",
            "멈춘 관문",
            "합성 control 대조",
            "FIXED SYNTHETIC REFERENCE ≠ REAL DOCUMENT ACCURACY",
            'href="evidence-console.html"',
            'id="runtime-alert"',
            "python3 scripts/run_evidence_console.py --port 8765",
        ):
            self.assertIn(marker, self.html)
        self.assertNotIn("innerHTML", self.html)
        self.assertNotIn("WebSocket", self.html)
        self.assertNotRegex(self.html, r'https?://')
        scripts = re.findall(r"<script>([\s\S]*?)</script>", self.html)
        self.assertEqual(len(scripts), 2)
        for script in scripts:
            subprocess.run(["node", "--check", "-"], input=script, text=True, check=True)

        console = (ROOT / "demo" / "evidence-console.html").read_text(encoding="utf-8")
        self.assertIn('id="tab-batch"', console)
        self.assertIn('src="evidence-batch.html?embedded=1"', console)

    def test_fixed_manifest_has_three_distinct_hold_controls(self) -> None:
        self.assertEqual(self.manifest["source_classification"], "SYNTHETIC_CONTROL")
        self.assertEqual(self.manifest["expected_decision"], "HOLD")
        self.assertEqual(len(self.manifest["samples"]), 3)
        self.assertEqual(
            {item["expected_processing_status"] for item in self.manifest["samples"]},
            {"VALID", "CONTENT_REJECTED", "PROVENANCE_FAILURE"},
        )
        self.assertIn("DOCUMENT_AI_EXECUTION", self.manifest["not_claimed"])

    def test_attack_and_rights_controls_stop_at_expected_boundaries(self) -> None:
        for sample in self.manifest["samples"][1:]:
            content = (ROOT / sample["path"].lstrip("/")).read_bytes()
            events = list(
                local_intake_events(
                    sample["filename"],
                    content,
                    expected_part=self.manifest["expected_part"],
                    manufacturer=self.manifest["manufacturer"],
                    local_review_rights_confirmed=sample["rights"],
                )
            )
            parser = next(item for item in events if item["event"] == "parser.completed")
            self.assertEqual(parser["status"], sample["expected_processing_status"])
            self.assertIn(sample["expected_blocker"], parser["evidence"]["blocker_codes"])
            self.assertFalse(any(item["event"] == "candidate.found" for item in events))
            self.assertEqual(events[-1]["status"], "HOLD")

    def test_architecture_is_slide_three_without_the_future_connector(self) -> None:
        sections = re.findall(r'<section class="slide"[\s\S]*?</section>', self.deck)
        self.assertEqual(sections[2].count("data-title=\"전체 흐름\""), 1)
        for marker in (
            "03 · EVIDENCE-TO-DECISION",
            "흩어진 문서가,",
            "근거 후보",
            "3개 Agent",
            "검증 Gate",
            "판단과 행동",
            "Mission · Parts · Assurance",
            "NOW</b> pypdf 로컬 파싱",
            "GCP</b> 저장된 합성 Agent 경로",
            'href="http://127.0.0.1:8765/demo/evidence-console.html"',
            'target="spectra-demo"',
            "Document AI·Gemini API 호출 0건",
        ):
            self.assertIn(marker, sections[2])
        self.assertEqual(sections[2].count('class="system-node'), 5)
        self.assertEqual(sections[2].count('class="system-arrow"'), 4)
        for removed_copy in ("future-plug", "FUTURE · NOT CONNECTED", "Document AI + Gemini가"):
            self.assertNotIn(removed_copy, sections[2])
        self.assertNotIn("IMPLEMENTATION TOOLS &amp; TECH STACK", self.deck)


if __name__ == "__main__":
    unittest.main()
