#!/usr/bin/env python3
"""Direct contract tests for the bounded Change Impact demo."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT / "demo/change-impact.html"
SOURCE_PATH = ROOT / "demo/data/mvp-product-result.json"


class ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sources: list[str] = []
        self.inline: list[str] = []
        self._capture = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        source = dict(attrs).get("src")
        if source:
            self.sources.append(source)
        else:
            self._capture = True
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._capture:
            self.inline.append("".join(self._buffer))
            self._capture = False


def node_path() -> str:
    found = shutil.which("node")
    if found:
        return found
    raise unittest.SkipTest("Node.js runtime unavailable")


class ChangeImpactDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
        parser = ScriptParser()
        parser.feed(cls.html)
        cls.parser = parser
        cls.script = "\n".join(parser.inline)

    def resolve(self, operation: str) -> dict:
        harness = r"""
const fs = require('fs');
const {webcrypto} = require('crypto');
global.crypto = webcrypto;
eval(fs.readFileSync(process.argv[2], 'utf8'));
let text = fs.readFileSync(process.argv[3], 'utf8');
const op = process.argv[1];
if (op === 'missing-impact') {
  const parsed = JSON.parse(text); parsed.mvp_decision.change_impact = null; text = JSON.stringify(parsed);
} else if (op === 'impact-hash') {
  const parsed = JSON.parse(text);
  text = text.replace('"baseline_hash":"' + parsed.mvp_decision.change_impact.baseline_hash + '"', '"baseline_hash":"sha256:' + '0'.repeat(64) + '"');
} else if (op === 'output-hash') {
  const parsed = JSON.parse(text);
  text = text.replace('"output_hash":"' + parsed.mvp_decision.output_hash + '"', '"output_hash":"sha256:' + '0'.repeat(64) + '"');
} else if (op === 'state') {
  text = text.replace('"mvp_decision":{"assurance_decision":"HOLD"', '"mvp_decision":{"assurance_decision":"PASS"');
} else if (op === 'actual') {
  text = text.replace('{"data_class":"SYNTHETIC"', '{"data_class":"ACTUAL"');
}
(async () => process.stdout.write(JSON.stringify(await globalThis.SPECTRA_CHANGE_IMPACT.resolveText(text))))().catch(error => { console.error(error); process.exit(1); });
"""
        script_path = ROOT / "demo/change-impact.html"
        # The harness needs only the inline JavaScript, so materialize it through stdin-free -e.
        js_literal = json.dumps(self.script)
        command = harness.replace("fs.readFileSync(process.argv[2], 'utf8')", js_literal, 1)
        completed = subprocess.run(
            [node_path(), "-e", command, operation, str(script_path), str(SOURCE_PATH)],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def assert_fail_closed(self, model: dict, reason: str) -> None:
        self.assertFalse(model["ready"])
        self.assertEqual(model["processing"], "DATA_UNAVAILABLE")
        self.assertEqual(model["engineering"], "NOT_EVALUATED")
        self.assertEqual(model["assurance"], "HOLD")
        self.assertEqual(model["reason"], reason)
        for forbidden in ["caseId", "runId", "baseline", "variant", "impact"]:
            self.assertNotIn(forbidden, model)

    def test_authoritative_generated_result_resolves_without_recalculation(self) -> None:
        model = self.resolve("valid")
        top = self.payload["mvp_decision"]
        self.assertTrue(model["ready"])
        self.assertEqual(model["caseId"], top["case_id"])
        self.assertEqual(model["runId"], top["run_id"])
        self.assertEqual(model["impact"], top["change_impact"])
        self.assertEqual(model["baseline"]["result_id"], top["baseline"]["result_id"])
        self.assertEqual(model["variant"]["result_id"], top["variant"]["result_id"])
        self.assertEqual((model["engineering"], model["assurance"]), ("NOT_EVALUATED", "HOLD"))

    def test_missing_change_impact_fails_closed(self) -> None:
        self.assert_fail_closed(self.resolve("missing-impact"), "CHANGE_IMPACT_INVALID")

    def test_tampered_change_impact_hash_fails_closed(self) -> None:
        self.assert_fail_closed(self.resolve("impact-hash"), "CHANGE_IMPACT_HASH_MISMATCH")

    def test_tampered_parent_output_hash_fails_closed(self) -> None:
        self.assert_fail_closed(self.resolve("output-hash"), "MVP_OUTPUT_HASH_MISMATCH")

    def test_optimistic_state_fails_closed(self) -> None:
        self.assert_fail_closed(self.resolve("state"), "MVP_STATE_INVALID")

    def test_unsupported_actual_claim_fails_closed(self) -> None:
        self.assert_fail_closed(self.resolve("actual"), "UNSUPPORTED_ACTUAL_CLAIM")

    def test_static_boundary_reset_and_no_remote_dependency(self) -> None:
        self.assertEqual(self.parser.sources, [])
        self.assertIn("data/mvp-product-result.json", self.html)
        self.assertIn("SYNTHETIC · GENERATED RESULT ONLY", self.html)
        self.assertIn("NOT ACTUAL EVIDENCE · NOT SUITABILITY · NOT ASSURANCE", self.html)
        self.assertIn("Synthetic policy APPROVED", self.html)
        self.assertIn("SYNTHETIC_", self.html)
        self.assertIn("id=\"reset\"", self.html)
        self.assertRegex(self.script, r"\$\('reset'\)\.addEventListener\('click'.*model=SAFE")
        for forbidden in [
            "impact-ec33a03f8d94eca3",
            "result-2ac48c19edb2f179",
            "result-619f2bd08363a162",
            "0.063072",
            "0.013072",
        ]:
            self.assertNotIn(forbidden, self.html)
        self.assertIsNone(re.search(r"https?://", self.html))


if __name__ == "__main__":
    unittest.main()
