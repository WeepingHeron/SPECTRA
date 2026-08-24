#!/usr/bin/env python3
"""Direct tests for the bounded H05 security posture screen."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML_PATH = ROOT / "demo/security-posture.html"
SNAPSHOT_PATH = ROOT / "demo/data/security-posture-h05-snapshot.json"


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
    if not found:
        raise unittest.SkipTest("Node.js runtime unavailable")
    return found


class SecurityPostureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.snapshot_text = SNAPSHOT_PATH.read_text(encoding="utf-8")
        cls.snapshot = json.loads(cls.snapshot_text)
        parser = ScriptParser()
        parser.feed(cls.html)
        cls.parser = parser
        cls.script = "\n".join(parser.inline)

    def run_node(self, operation: str) -> dict:
        command = r"""
const fs=require('fs');const {webcrypto}=require('crypto');global.crypto=webcrypto;
eval(SCRIPT_LITERAL);const payload=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const op=process.argv[1];
const byId=id=>payload.controls.find(item=>item.control_id===id);
if(op==='kms')byId('KMS_CMEK').status='VERIFIED_BOUNDED';
else if(op==='rbac')byId('ACTUAL_CUSTOMER_RBAC').status='VERIFIED_BOUNDED';
else if(op==='pentest')byId('PENETRATION_TEST').status='VERIFIED_BOUNDED';
else if(op==='complete')payload.posture_status='COMPLETE';
else if(op==='pass')payload.assurance_decision='PASS';
else if(op==='unknown')payload.controls[0].control_id='UNKNOWN_SECURITY_CONTROL';
else if(op==='duplicate')payload.controls[1].control_id=payload.controls[0].control_id;
else if(op==='hash')payload.snapshot_sha256='sha256:'+'0'.repeat(64);
else if(op==='sensitive-label')byId('KMS_CMEK').label_ko='/Users/private/region-policy';
else if(op==='sensitive-value')byId('KMS_CMEK').observed_value='https://secret.example/internal';
(async()=>{if(op==='sensitive-label'||op==='sensitive-value'){const preimage={...payload};delete preimage.snapshot_sha256;payload.snapshot_sha256=await globalThis.SPECTRA_SECURITY_POSTURE.digest(preimage)}const model=await globalThis.SPECTRA_SECURITY_POSTURE.resolveSnapshot(payload);const out=op==='export'&&model.ready?globalThis.SPECTRA_SECURITY_POSTURE.buildExport(model):model;process.stdout.write(JSON.stringify(out))})().catch(error=>{console.error(error);process.exit(1)});
""".replace("SCRIPT_LITERAL", json.dumps(self.script))
        completed = subprocess.run(
            [node_path(), "-e", command, operation, str(SNAPSHOT_PATH)],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)

    def assert_fail_closed(self, model: dict, reason: str) -> None:
        self.assertFalse(model["ready"])
        self.assertEqual(model["processing"], "DATA_UNAVAILABLE")
        self.assertEqual(model["assurance"], "HOLD")
        self.assertEqual(model["reason"], reason)
        self.assertNotIn("snapshot", model)

    def test_bounded_snapshot_accepts_only_exact_expected_posture(self) -> None:
        model = self.run_node("valid")
        self.assertTrue(model["ready"])
        self.assertEqual(model["assurance"], "HOLD")
        controls = {item["control_id"]: item for item in model["snapshot"]["controls"]}
        self.assertEqual(sum(item["status"] == "VERIFIED_BOUNDED" for item in controls.values()), 5)
        self.assertEqual(controls["PUBLIC_IAM_PRINCIPALS"]["observed_value"], "0_PUBLIC_PRINCIPALS")
        self.assertEqual(controls["KMS_CMEK"]["status"], "NOT_IMPLEMENTED")
        self.assertEqual(controls["PENETRATION_TEST"]["status"], "NOT_EVALUATED")

    def test_optimistic_kms_rbac_and_pen_test_promotions_fail_closed(self) -> None:
        for operation in ["kms", "rbac", "pentest"]:
            with self.subTest(operation=operation):
                self.assert_fail_closed(self.run_node(operation), "OPTIMISTIC_CONTROL_REJECTED")

    def test_complete_or_pass_claim_fails_closed(self) -> None:
        self.assert_fail_closed(self.run_node("complete"), "OPTIMISTIC_POSTURE_REJECTED")
        self.assert_fail_closed(self.run_node("pass"), "OPTIMISTIC_POSTURE_REJECTED")

    def test_unknown_and_duplicate_controls_fail_closed(self) -> None:
        self.assert_fail_closed(self.run_node("unknown"), "UNKNOWN_CONTROL_REJECTED")
        # The duplicate replaces a known id, but duplicate detection must win before set completeness.
        self.assert_fail_closed(self.run_node("duplicate"), "DUPLICATE_CONTROL_REJECTED")

    def test_snapshot_hash_tamper_fails_closed(self) -> None:
        self.assert_fail_closed(self.run_node("hash"), "SNAPSHOT_HASH_MISMATCH")

    def test_recomputed_hash_cannot_authorize_display_text(self) -> None:
        self.assert_fail_closed(self.run_node("sensitive-label"), "CONTROL_CONTENT_MISMATCH")
        self.assert_fail_closed(self.run_node("sensitive-value"), "CONTROL_CONTENT_MISMATCH")

    def test_allowlist_export_contains_only_bounded_fields(self) -> None:
        exported = self.run_node("export")
        self.assertEqual(exported["export_kind"], "SECURITY_POSTURE_ALLOWLIST")
        self.assertEqual(exported["assurance_decision"], "HOLD")
        self.assertFalse(exported["live"])
        self.assertEqual(len(exported["controls"]), 10)
        serialized = json.dumps(exported, ensure_ascii=False)
        for forbidden in ["label_ko", "observed_value", "captured_at", "snapshot_sha256", "@", "gs://", "inputs/", "results/", "roles/"]:
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(set(exported["controls"][0]), {"control_id", "status", "evidence_refs"})

    def test_snapshot_and_screen_expose_no_sensitive_resource_identity(self) -> None:
        combined = self.snapshot_text + self.html
        for forbidden in ["@iceu-686", "gs://", "inputs/", "results/", "roles/", "serviceAccount:", "private_key", "client_secret"]:
            self.assertNotIn(forbidden, combined)
        self.assertIsNone(re.search(r"https?://", self.html))
        self.assertEqual(self.parser.sources, [])
        self.assertIn("NOT LIVE · NOT PEN TEST · NOT ASSURANCE", self.html)
        self.assertIn("NO SECRET · NO IAM MEMBER · NO OBJECT PATH", self.html)

    def test_reset_hides_posture_and_disables_export(self) -> None:
        self.assertIn('id="snapshot-id">—', self.html)
        self.assertIn('id="export" type="button" aria-disabled="true"', self.html)
        self.assertRegex(self.script, r"\$\('reset'\)\.addEventListener\('click'.*model=SAFE.*render\(\)")
        for identifier in ["3f5d9221", "df49b5c1", "000005-32c"]:
            self.assertNotIn(identifier, self.html)


if __name__ == "__main__":
    unittest.main()
