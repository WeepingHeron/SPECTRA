#!/usr/bin/env python3
"""Direct tests for the presentation-first three-step Roadmap Lab."""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HTML = ROOT / "demo" / "roadmap-lab.html"
ROUTES = {
    "evidence-intake.html",
    "cots-candidate-library.html",
    "document-review.html",
    "ai-processing-readiness.html",
    "change-impact.html",
    "cad-linkage-readiness.html",
    "security-posture.html",
}


class RoadmapLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML.read_text(encoding="utf-8")
        scripts = re.findall(r"<script>([\s\S]*?)</script>", cls.html)
        assert len(scripts) == 1
        cls.script = scripts[0]

    def stage_data(self) -> list[dict]:
        command = (
            "eval(" + json.dumps(self.script) + ");"
            "process.stdout.write(JSON.stringify(globalThis.SPECTRA_ROADMAP_DEMO.STAGES));"
        )
        completed = subprocess.run(
            ["node", "-e", command], check=True, capture_output=True, text=True
        )
        return json.loads(completed.stdout)

    def test_story_is_three_steps_not_seven_equal_priority_cards(self) -> None:
        self.assertEqual(len(re.findall(r'<button class="step(?: active)?"', self.html)), 3)
        self.assertNotIn("7 routes", self.html)
        self.assertNotIn('class="card"', self.html)
        for label in ("자료 연결", "AI 보조 검토", "판단과 다음 행동"):
            self.assertIn(label, self.html)

    def test_three_stage_contract_is_exact_and_fail_closed(self) -> None:
        stages = self.stage_data()
        self.assertEqual(len(stages), 3)
        self.assertEqual(
            [stage["status"] for stage in stages],
            ["BLOCKED_EXTERNAL", "IMPLEMENTED_BOUNDED", "IMPLEMENTED_BOUNDED"],
        )
        self.assertTrue(all(len(stage["nodes"]) == 3 for stage in stages))
        self.assertTrue(all(len(stage["actions"]) == 2 for stage in stages))
        self.assertTrue(all("HOLD" in stage["answerState"] for stage in stages))

    def test_all_seven_detailed_tools_remain_q_and_a_only(self) -> None:
        stages = self.stage_data()
        links = {href for stage in stages for _label, href in stage["links"]}
        self.assertEqual(links, ROUTES)
        self.assertEqual([len(stage["links"]) for stage in stages], [2, 2, 3])
        for route in links:
            self.assertTrue((HTML.parent / route).is_file(), route)
        self.assertIn("세부 도구는 Q&amp;A에서 연다.", self.html)

    def test_plain_language_product_definition_is_prominent(self) -> None:
        for text in (
            "흩어진 근거를 연결해",
            "판단 가능한지 먼저 확인한다.",
            "SPECTRA는 무엇인가?",
            "방사선 수치를 만들어 주는 AI가 아니라",
            "부족한 다음 행동을 보여 주는 제품이다.",
        ):
            self.assertIn(text, self.html)

    def test_truth_boundary_and_demo_time_are_adjacent(self) -> None:
        for text in (
            "SYNTHETIC DEMO",
            "실제 environment·part evidence 0건",
            "FINAL ASSURANCE · HOLD",
            "권장 시연 40초",
        ):
            self.assertIn(text, self.html)

    def test_no_remote_dependency_api_or_storage(self) -> None:
        lowered = self.html.lower()
        self.assertNotRegex(
            lowered,
            r"https?://|//cdn|<script[^>]+src=|fetch\s*\(|xmlhttprequest|websocket|sendbeacon",
        )
        self.assertNotIn("localStorage", self.html)
        self.assertNotIn("sessionStorage", self.html)

    def test_presentation_visual_contract_and_fixed_viewport(self) -> None:
        for token in (
            "--bg:#050505",
            "letter-spacing:.22em",
            "border-bottom:1px solid var(--line)",
            "height:100vh",
            "overflow:hidden",
            "grid-template-columns:205px minmax(0,1fr) 280px",
            "@media(max-height:760px)",
        ):
            self.assertIn(token, self.html)

    def test_javascript_syntax_and_next_reset_loop(self) -> None:
        completed = subprocess.run(
            ["node", "--check", "-"], input=self.script, text=True, capture_output=True
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("index=index<2?index+1:0", self.script)
        self.assertIn("처음부터 다시 보기 ↺", self.script)


if __name__ == "__main__":
    unittest.main()
