#!/usr/bin/env python3
"""Export deterministic CAD manifest change receipts for the Product demo."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_cad_adapter import assess_cad_change  # noqa: E402

DEFAULT_OUTPUT = ROOT / "demo/data/cad-change-receipts.json"


def _digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _manifest(revision: str, label: str, regions: tuple[str, ...] = ("shield-main",)) -> dict:
    return {
        "revision_id": revision,
        "content_sha256": _digest(label),
        "length_unit": "mm",
        "coordinate_frame": "spacecraft-body",
        "material_map": [
            {"region_id": region, "material_id": "aluminum-6061"} for region in regions
        ],
        "shielding_region_ids": list(regions),
    }


def _payload(baseline: dict, variant: dict) -> dict:
    return {
        "candidate_class": "SYNTHETIC_CONTROL",
        "baseline": baseline,
        "variant": variant,
        "requested_outcome": {
            "engineering_gate": "NOT_EVALUATED",
            "assurance_decision": "HOLD",
            "suitability": "NOT_EVALUATED",
            "geometry_calculated": False,
        },
    }


def build_receipts() -> dict:
    baseline = _manifest("cad-r1", "cad-baseline")
    return {
        "ecc": assess_cad_change(_payload(baseline, dict(baseline))),
        "shield": assess_cad_change(
            _payload(baseline, _manifest("cad-r2", "cad-shield-4mm"))
        ),
        "scope": assess_cad_change(
            _payload(
                baseline,
                _manifest("cad-r3", "cad-unsupported-region", ("shield-main", "shield-aux")),
            )
        ),
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
