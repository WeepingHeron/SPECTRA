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
        self.assertIn('src="test-catalog.html?embedded=1"', console)
        self.assertIn("임무·부품·방사선 시험", console)

    def test_cloud_catalog_ui_is_safe_and_has_local_fallback(self) -> None:
        catalog = (ROOT / "demo" / "test-catalog.html").read_text(encoding="utf-8")
        for marker in (
            "spectra-public-test-catalog-iceu-686/v1",
            "/demo/data/test-catalog",
            "문서별 처리 결과",
            "세 입력 연결 결과",
            "감사 기록",
            "판단 보류",
            "deployment-receipt.json",
            "공개 객체 확인",
        ):
            self.assertIn(marker, catalog)
        self.assertNotIn("innerHTML=", catalog)
        scripts = re.findall(r"<script>([\s\S]*?)</script>", catalog)
        self.assertEqual(len(scripts), 1)
        subprocess.run(["node", "--check", "-"], input=scripts[0], text=True, check=True)

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

    def test_architecture_slide_matches_the_current_evidence_to_decision_flow(self) -> None:
        sections = re.findall(r'<section class="slide"[\s\S]*?</section>', self.deck)
        architecture = next(
            section for section in sections if 'data-title="전체 흐름"' in section
        )
        for marker in (
            "06 · SPECTRA · EVIDENCE TO DECISION",
            "흩어진 문서가,",
            "입력 자료",
            "근거 연결",
            "부품 · 시험 · 조건의 연결 상태 확인",
            "3개 Agent",
            "검증 Gate",
            "판단과 행동",
            "문제 위치 · 이유 · 다음 조치",
            "Mission · Parts · Assurance",
        ):
            self.assertIn(marker, architecture)
        self.assertEqual(architecture.count('class="system-node'), 5)
        self.assertEqual(architecture.count('class="system-arrow"'), 4)
        for removed_copy in ("future-plug", "FUTURE · NOT CONNECTED", "Document AI + Gemini가"):
            self.assertNotIn(removed_copy, architecture)
        self.assertNotIn("IMPLEMENTATION TOOLS &amp; TECH STACK", self.deck)


if __name__ == "__main__":
    unittest.main()
