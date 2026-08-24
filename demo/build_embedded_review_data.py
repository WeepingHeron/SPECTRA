#!/usr/bin/env python3
"""Bundle demo JSON as a file://-safe JavaScript fallback."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "demo/data"
OUTPUT = DATA_DIR / "embedded-review-data.js"
FILES = (
    "demo-case-clean-control.json",
    "demo-case-tampered.json",
    "demo-case-wrong-part.json",
    "actual-environment-bundle-receipt.json",
    "actual-part-bundle-receipt.json",
    "evidence-source-readiness-synthetic.json",
    "nasa-snapshot-gate-receipt.json",
    "readiness-environment-hold-v1.json",
    "local-bundle-binding-receipt.json",
    "document-intake-receipts.json",
    "exact-part-readiness-receipt.json",
    "actual-evidence-review-receipts.json",
    "review-audit-receipts.json",
    "mvp-product-result.json",
    "cad-change-receipts.json",
    "change-impact-receipts.json",
)


def main() -> int:
    payload = {
        f"data/{name}": (DATA_DIR / name).read_text(encoding="utf-8")
        for name in FILES
    }
    OUTPUT.write_text(
        "globalThis.SPECTRA_EMBEDDED_TEXT=Object.freeze("
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ");\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT} ({len(payload)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
