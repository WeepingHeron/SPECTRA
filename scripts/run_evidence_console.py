#!/usr/bin/env python3
"""Serve a local-only raw Evidence Console without triggering GCP mutations.

POST /api/intake streams JSONL events from the real local PDF/TXT intake path.
GET /api/gcp-snapshot-logs returns the stored H05 Cloud Logging evidence only.
The server binds to loopback and never accepts or forwards a remote URL.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

from intake_local_document_candidate import MAX_BYTES, intake_document


REPO_ROOT = Path(__file__).resolve().parents[1]
GCP_LOG_EVIDENCE = (
    REPO_ROOT
    / "docs/workstreams/70-platform-gcp/evidence/h05-gcp-inventory-and-logs.json"
)
ALLOWED_SUFFIXES = frozenset({".pdf", ".txt"})


def ensure_pdf_runtime() -> None:
    """Re-exec with the bundled local runtime when system Python lacks pypdf."""
    if importlib.util.find_spec("pypdf") is not None:
        return
    bundled = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
    )
    if bundled.is_file() and Path(sys.executable).resolve() != bundled.resolve():
        print("SPECTRA Evidence Console: switching to bundled PDF runtime")
        os.execv(str(bundled), [str(bundled), str(Path(__file__).resolve()), *sys.argv[1:]])


def _json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _event(
    sequence: int,
    run_id: str,
    stage: str,
    event: str,
    status: str,
    message: str,
    **evidence: Any,
) -> dict[str, Any]:
    return {
        "event_version": "1.0.0",
        "sequence": sequence,
        "run_id": run_id,
        "stage": stage,
        "event": event,
        "status": status,
        "message": message,
        "evidence": evidence,
    }


def local_intake_events(
    filename: str,
    content: bytes,
    *,
    expected_part: str,
    manufacturer: str | None,
    local_review_rights_confirmed: bool,
) -> Iterator[dict[str, Any]]:
    """Run the real local intake and emit its unedited event payloads in order."""
    safe_name = Path(filename).name
    suffix = Path(safe_name).suffix.lower()
    digest = hashlib.sha256(content).hexdigest()
    run_id = f"local-{digest[:16]}"
    sequence = 1
    yield _event(
        sequence,
        run_id,
        "INGEST",
        "run.started",
        "RUNNING",
        "로컬 문서 검사를 시작했습니다.",
        filename=safe_name,
        byte_count=len(content),
        content_sha256=f"sha256:{digest}",
        decision_use=False,
    )
    sequence += 1

    if suffix not in ALLOWED_SUFFIXES:
        yield _event(
            sequence,
            run_id,
            "INGEST",
            "run.blocked",
            "DATA_UNAVAILABLE",
            "지원하지 않는 파일 형식입니다.",
            stable_code="DOCUMENT_TYPE_UNSUPPORTED",
            assurance_decision="HOLD",
        )
        return
    if not content or len(content) > MAX_BYTES:
        yield _event(
            sequence,
            run_id,
            "INGEST",
            "run.blocked",
            "DATA_UNAVAILABLE",
            "파일 크기가 허용 범위를 벗어났습니다.",
            stable_code="DOCUMENT_SIZE_OUT_OF_RANGE",
            assurance_decision="HOLD",
        )
        return

    yield _event(
        sequence,
        run_id,
        "DOCUMENT_PARSER",
        "parser.started",
        "RUNNING",
        "PDF/TXT 텍스트와 원문 지문을 추출합니다.",
        suffix=suffix,
        raw_path_exposed=False,
        raw_text_exposed=False,
    )
    sequence += 1

    with tempfile.TemporaryDirectory(prefix="spectra-console-") as directory:
        document = Path(directory) / ("document" + suffix)
        document.write_bytes(content)
        receipt = intake_document(
            document,
            expected_part=expected_part,
            manufacturer=manufacturer,
            local_review_rights_confirmed=local_review_rights_confirmed,
        )

    source = receipt.get("source", {})
    yield _event(
        sequence,
        run_id,
        "DOCUMENT_PARSER",
        "parser.completed",
        receipt["processing_status"],
        "파서가 decision-use가 금지된 extraction receipt를 생성했습니다.",
        extraction_status=receipt["extraction_status"],
        extraction_engine=source.get("extraction_engine"),
        page_count=source.get("page_count"),
        candidate_count=receipt["candidate_count"],
        blocker_codes=receipt["blocker_codes"],
        assurance_decision=receipt["assurance_decision"],
        used_for_decision=receipt["used_for_decision"],
    )
    sequence += 1

    for candidate in receipt.get("candidates", []):
        yield _event(
            sequence,
            run_id,
            "DOCUMENT_PARSER",
            "candidate.found",
            candidate["candidate_status"],
            "원문 위치에 결속된 미승인 후보를 찾았습니다.",
            candidate_id=candidate["candidate_id"],
            field=candidate["field"],
            value=candidate["value"],
            unit=candidate["unit"],
            source_span=candidate["source_span"],
        )
        sequence += 1

    summary = receipt["review_summary"]
    if receipt["processing_status"] == "VALID":
        yield _event(
            sequence,
            run_id,
            "PARTS_REVIEW",
            "approved_target.blocked",
            "NOT_EVALUATED",
            summary["blocking_reason"],
            stable_code="APPROVED_BOM_TARGET_MISSING",
            problem_location=summary["problem_location"],
            confirmed_facts=summary["confirmed_facts"],
            assurance_decision="HOLD",
        )
        sequence += 1
    else:
        yield _event(
            sequence,
            run_id,
            "PARTS_REVIEW",
            "review.not_called",
            "NOT_CALLED",
            "문서 입력 단계가 닫혀 부품 검토를 호출하지 않았습니다.",
            blocker_codes=receipt["blocker_codes"],
            assurance_decision="HOLD",
        )
        sequence += 1

    yield _event(
        sequence,
        run_id,
        "ASSURANCE",
        "assurance.not_called",
        "NOT_CALLED",
        "앞 단계가 HOLD이므로 최종 승인 Agent를 호출하지 않았습니다.",
        upstream_status=receipt["processing_status"],
        assurance_decision="HOLD",
    )
    sequence += 1
    yield _event(
        sequence,
        run_id,
        "DECISION",
        "decision.completed",
        "HOLD",
        summary["headline"],
        processing_status=receipt["processing_status"],
        problem_location=summary["problem_location"],
        confirmed_facts=summary["confirmed_facts"],
        blocking_reason=summary["blocking_reason"],
        next_action=summary["next_action"],
        approval_status="NOT_EVALUATED",
        use_status="NOT_FOR_DECISION",
        assurance_decision="HOLD",
    )


def load_gcp_snapshot_logs() -> dict[str, Any]:
    payload = json.loads(GCP_LOG_EVIDENCE.read_text(encoding="utf-8"))
    logs = payload.get("cloud_run_structured_logs")
    if (
        payload.get("schema_version") != "1.0.0"
        or payload.get("project_id") != "iceu-686"
        or payload.get("region") != "asia-northeast3"
        or not isinstance(logs, list)
        or not logs
        or any(not isinstance(item, dict) for item in logs)
    ):
        raise ValueError("GCP_SNAPSHOT_LOG_EVIDENCE_INVALID")
    return {
        "boundary": {
            "source_classification": "CONTROL_TOWER_VERIFIED_H05_SNAPSHOT",
            "live": False,
            "project_id": payload["project_id"],
            "region": payload["region"],
            "log_count": len(logs),
            "assurance_decision": "HOLD",
        },
        "logs": logs,
    }


class EvidenceConsoleHandler(SimpleHTTPRequestHandler):
    server_version = "SPECTRAEvidenceConsole/1.0"

    def _send_json(self, status: int, value: Any) -> None:
        body = _json(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json(200, {"status": "READY", "gcp_live": False})
            return
        if parsed.path == "/api/gcp-snapshot-logs":
            try:
                self._send_json(200, load_gcp_snapshot_logs())
            except (OSError, ValueError, json.JSONDecodeError):
                self._send_json(
                    500,
                    {
                        "status": "DATA_UNAVAILABLE",
                        "stable_code": "GCP_SNAPSHOT_LOG_EVIDENCE_INVALID",
                        "assurance_decision": "HOLD",
                    },
                )
            return
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/api/intake":
            self._send_json(404, {"status": "NOT_FOUND"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BYTES:
            self._send_json(
                413,
                {
                    "status": "DATA_UNAVAILABLE",
                    "stable_code": "DOCUMENT_SIZE_OUT_OF_RANGE",
                    "assurance_decision": "HOLD",
                },
            )
            return
        params = urllib.parse.parse_qs(parsed.query)
        expected_part = params.get("expected_part", [""])[0].strip()
        manufacturer = params.get("manufacturer", [""])[0].strip() or None
        rights = params.get("confirm_local_review_rights", ["false"])[0] == "true"
        filename = Path(self.headers.get("X-Spectra-Filename", "document.bin")).name
        if not expected_part or len(expected_part) > 120 or len(filename) > 180:
            self._send_json(
                400,
                {
                    "status": "INVALID_INPUT",
                    "stable_code": "CONSOLE_INPUT_INVALID",
                    "assurance_decision": "HOLD",
                },
            )
            return
        content = self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        for event in local_intake_events(
            filename,
            content,
            expected_part=expected_part,
            manufacturer=manufacturer,
            local_review_rights_confirmed=rights,
        ):
            self.wfile.write(_json(event) + b"\n")
            self.wfile.flush()

    def log_message(self, format: str, *args: Any) -> None:
        print("[evidence-console] " + (format % args))


def main() -> int:
    ensure_pdf_runtime()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    handler = partial(EvidenceConsoleHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"SPECTRA Evidence Console: http://127.0.0.1:{args.port}/demo/evidence-console.html")
    print("LOCAL LIVE parser enabled · GCP logs are stored H05 snapshot only · no GCP mutation")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
