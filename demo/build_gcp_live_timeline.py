#!/usr/bin/env python3
"""Build the H08 live-or-snapshot Product timeline payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.spectra_gcp_adapter import build_product_timeline  # noqa: E402


DEFAULT_RECEIPT = ROOT / "docs/workstreams/70-platform-gcp/evidence/h07-live-execution-receipt.json"
DEFAULT_SNAPSHOT = ROOT / "demo/data/h05-gcp-snapshot.json"
DEFAULT_JSON = ROOT / "demo/data/gcp-product-timeline.json"
DEFAULT_JS = ROOT / "demo/data/gcp-product-timeline.js"
JS_PREFIX = "globalThis.SPECTRA_GCP_PRODUCT_TIMELINE="


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--javascript", type=Path, default=DEFAULT_JS)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    payload = build_product_timeline(receipt, verified_snapshot=snapshot)
    compact = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(compact + "\n", encoding="utf-8")
    args.javascript.write_text(JS_PREFIX + compact + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
