#!/usr/bin/env python3
"""Export deterministic bounded human-review receipts for the Product demo."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_review_adapter import record_review_action  # noqa: E402

DEFAULT_OUTPUT = ROOT / "demo/data/review-audit-receipts.json"


def build_receipts() -> dict:
    candidate_hash = hashlib.sha256(b"SPECTRA synthetic candidate EX-100").hexdigest()
    reviewer = hashlib.sha256(b"independent-reviewer-demo").hexdigest()
    author = hashlib.sha256(b"candidate-author-demo").hexdigest()
    definitions = {
        "REQUEST_EVIDENCE": "EVIDENCE_GAP_UNRESOLVED",
        "EXCLUDE_CANDIDATE": "CANDIDATE_NOT_DECISION_ELIGIBLE",
        "RECORD_REVIEW": "REVIEW_BOUNDARY_RECORDED",
    }
    return {
        action: record_review_action(
            {
                "candidate_content_sha256": candidate_hash,
                "reviewer_action": action,
                "review_reason_code": reason,
                "reviewer_role": "INDEPENDENT_REVIEWER",
                "reviewer_subject_sha256": reviewer,
                "candidate_author_subject_sha256": author,
                "sequence": 1,
                "prior_receipt_sha256": "GENESIS",
                "recorded_at": "2026-08-24T12:00:00Z",
            }
        )
        for action, reason in definitions.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_receipts(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
