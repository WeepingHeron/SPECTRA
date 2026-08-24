#!/usr/bin/env python3
"""Stage only the H05 service, production Core, contracts, and fixed fixtures."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


VALID_FIXTURES = (
    "synthetic-hold.json",
    "synthetic-tid-only-hold.json",
    "synthetic-v2-hold.json",
)


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    bundle = repo / "platform/gcp-e2e-h04"
    copy_file(bundle / "service/main.py", output / "service/main.py")
    copy_file(bundle / "service/Dockerfile", output / "Dockerfile")
    copy_file(bundle / "service/requirements.txt", output / "requirements.txt")
    shutil.copytree(bundle / "shared", output / "shared", dirs_exist_ok=True)
    shutil.copytree(repo / "src/spectra_sim", output / "src/spectra_sim", dirs_exist_ok=True)
    shutil.copytree(repo / "schemas", output / "schemas", dirs_exist_ok=True)
    shutil.copytree(repo / "simulation/schemas", output / "simulation/schemas", dirs_exist_ok=True)
    copy_file(repo / "simulation/fixtures/mvp-ecc-policy-v2.json", output / "simulation/fixtures/mvp-ecc-policy-v2.json")
    copy_file(repo / "simulation/config/synthetic-model.json", output / "simulation/config/synthetic-model.json")
    copy_file(repo / "tests/schema/validate_contracts.py", output / "tests/schema/validate_contracts.py")
    for name in VALID_FIXTURES:
        copy_file(repo / "tests/schema/fixtures/valid" / name, output / "tests/schema/fixtures/valid" / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
