#!/usr/bin/env python3
"""SPECTRA Live Demo Bridge Server.

Serves the presentation slides and handles live Google Cloud Workflows execution triggers,
allowing the slide deck to create and record real executions in GCP Console in real time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS_DECK = Path.home() / "Downloads" / "spectra_presentation.html"
DEFAULT_DECK = DOWNLOADS_DECK if DOWNLOADS_DECK.exists() else (REPO_ROOT / "demo" / "index.html")
FIXTURES_DIR = REPO_ROOT / "platform" / "gcp-e2e-h04" / "fixtures"

PROJECT_ID = "iceu-686"
REGION = "asia-northeast3"
WORKFLOW_NAME = "spectra-h04-e2e"
BUCKET = f"spectra-h04-{PROJECT_ID}"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def run_cmd(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
    return completed.stdout.strip()


def run_gcp_workflow(scenario: str) -> dict[str, Any]:
    """Execute real case in GCP Workflows using gcloud CLI."""
    start_perf = time.perf_counter()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    object_name = f"inputs/{timestamp}-{uuid.uuid4().hex[:8]}-{scenario}.json"

    forged_sha = "sha256:" + ("0" * 64)
    extra_args: dict[str, Any] = {}

    if scenario == "normal":
        fixture_path = FIXTURES_DIR / "normal.json"
        metadata_sha = None
        expected_sha = None
    elif scenario == "mission_fail":
        fixture_path = FIXTURES_DIR / "malformed-part.json"
        metadata_sha = None
        expected_sha = None
    elif scenario == "parts_fail":
        fixture_path = FIXTURES_DIR / "corrupted-evidence-hash.json"
        metadata_sha = None
        expected_sha = None
    elif scenario == "assurance_fail":
        fixture_path = FIXTURES_DIR / "normal.json"
        metadata_sha = forged_sha
        expected_sha = forged_sha
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    if not fixture_path.exists():
        # Fallback inline fixture if fixture file is missing
        fixture_val = {"data_class": "SYNTHETIC", "scenario": scenario, "timestamp": timestamp}
    else:
        fixture_val = json.loads(fixture_path.read_text(encoding="utf-8"))

    fixture_sha = canonical_sha256(fixture_val)
    decl_metadata_sha = metadata_sha or fixture_sha
    decl_expected_sha = expected_sha or fixture_sha

    # 1. Upload input object to Cloud Storage
    with tempfile.TemporaryDirectory(prefix="spectra-live-") as temp_dir:
        input_tmp = Path(temp_dir) / "input.json"
        input_tmp.write_bytes(canonical_json_bytes(fixture_val))
        run_cmd([
            "gcloud", "storage", "cp", str(input_tmp), f"gs://{BUCKET}/{object_name}",
            "--project", PROJECT_ID, "--if-generation-match=0",
            f"--custom-metadata=sha256={decl_metadata_sha}",
        ])

    # 2. Get generation metadata
    meta_raw = run_cmd([
        "gcloud", "storage", "objects", "describe", f"gs://{BUCKET}/{object_name}",
        "--project", PROJECT_ID, "--format=json",
    ])
    meta_json = json.loads(meta_raw)
    generation = str(meta_json["generation"])

    # 3. Trigger GCP Workflow execution
    workflow_args = {
        "bucket": BUCKET,
        "input_object": object_name,
        "input_generation": generation,
        "input_sha256": decl_expected_sha,
    }
    workflow_args.update(extra_args)

    exec_raw = run_cmd([
        "gcloud", "workflows", "run", WORKFLOW_NAME,
        "--project", PROJECT_ID, "--location", REGION,
        "--data", json.dumps(workflow_args, separators=(",", ":")),
        "--format=json",
    ])
    exec_json = json.loads(exec_raw)
    duration = round(time.perf_counter() - start_perf, 3)

    exec_name = exec_json.get("name", "")
    exec_id = exec_name.split("/")[-1] if "/" in exec_name else exec_name
    console_exec_url = f"https://console.cloud.google.com/workflows/workflow/{REGION}/{WORKFLOW_NAME}/execution/{REGION}/{exec_id}?project={PROJECT_ID}"

    # Parse result if available
    workflow_state = exec_json.get("state", "SUCCEEDED")
    result_payload = {}
    if "result" in exec_json:
        try:
            result_payload = json.loads(exec_json["result"])
        except Exception:
            result_payload = {}

    return {
        "status": "OK",
        "live_gcp": True,
        "scenario": scenario,
        "execution_id": exec_id,
        "execution_name": exec_name,
        "console_url": console_exec_url,
        "workflow_state": workflow_state,
        "duration_seconds": duration,
        "start_time": start_iso,
        "input_object": object_name,
        "input_generation": generation,
        "input_sha256": decl_expected_sha,
        "result": result_payload,
    }


class SpectraLiveHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/trigger-workflow":
            params = urllib.parse.parse_qs(parsed.query)
            scenario = params.get("scenario", ["normal"])[0]
            try:
                data = run_gcp_workflow(scenario)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                err_data = {"status": "ERROR", "error": str(e), "scenario": scenario}
                self.wfile.write(json.dumps(err_data, ensure_ascii=False).encode("utf-8"))
            return

        if parsed.path == "/" or parsed.path == "/index.html":
            target = DOWNLOADS_DECK if DOWNLOADS_DECK.exists() else (REPO_ROOT / "demo" / "index.html")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(target.read_bytes())
            return

        super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser(description="SPECTRA Live GCP Demo Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    args = parser.parse_args()

    server_address = ("", args.port)
    httpd = HTTPServer(server_address, SpectraLiveHandler)
    print(f"==================================================")
    print(f"🚀 SPECTRA Live GCP Demo Bridge Running!")
    print(f"📍 Local Slide URL: http://localhost:{args.port}")
    print(f"⚡ Live API: http://localhost:{args.port}/api/trigger-workflow?scenario=normal")
    print(f"🌐 Target GCP Project: {PROJECT_ID} ({REGION})")
    print(f"🎯 Target Workflow: {WORKFLOW_NAME}")
    print(f"==================================================")
    print(f"Opening http://localhost:{args.port} in Google Chrome...")
    try:
        res = subprocess.run(["open", "-a", "Google Chrome", f"http://localhost:{args.port}"], check=False, capture_output=True)
        if res.returncode != 0:
            subprocess.run(["open", f"http://localhost:{args.port}"], check=False)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping SPECTRA Live Demo Server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
