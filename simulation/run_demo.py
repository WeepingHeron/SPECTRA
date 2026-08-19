#!/usr/bin/env python3
"""Print a deterministic Stage 2 comparison matrix; no files are written."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spectra_sim import SimulationOptions, run_simulation  # noqa: E402


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    packet = load(ROOT / "tests/schema/fixtures/valid/synthetic-hold.json")
    model = load(ROOT / "simulation/config/synthetic-model.json")
    scenarios = [
        ("shield-1mm-ecc", SimulationOptions(shielding_mm=1, ecc_enabled=True)),
        ("shield-2mm-ecc", SimulationOptions(shielding_mm=2, ecc_enabled=True)),
        ("shield-4mm-ecc", SimulationOptions(shielding_mm=4, ecc_enabled=True)),
        ("shield-2mm-no-ecc", SimulationOptions(shielding_mm=2, ecc_enabled=False)),
        ("out-of-scope-5mm", SimulationOptions(shielding_mm=5, ecc_enabled=True)),
    ]
    print("SPECTRA SYNTHETIC BASELINE — NOT PHYSICAL EVIDENCE")
    print("scenario\tstatus\tshielded_tid_krad\tresidual_seu\tengineering\tassurance")
    for name, options in scenarios:
        result = run_simulation(packet, model, options)
        tid = result["metrics"]["shielded_tid"]
        seu = result["metrics"]["residual_seu"]
        print(
            f"{name}\t{result['processing_status']}\t"
            f"{tid['value']:.6g}" if tid else f"{name}\t{result['processing_status']}\t-",
            end="",
        )
        print(
            f"\t{seu['value']:.6g}" if seu else "\t-",
            f"\t{result['engineering_gate']}\t{result['assurance_decision']}",
            sep="",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
