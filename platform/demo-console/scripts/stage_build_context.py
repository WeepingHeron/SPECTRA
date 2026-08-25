#!/usr/bin/env python3
"""Stage only the files required by the public SPECTRA demo console."""

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
    bundle = repo / "platform/demo-console"
    output.mkdir(parents=True, exist_ok=True)

    copy_file(bundle / "Dockerfile", output / "Dockerfile")
    copy_file(bundle / "requirements.txt", output / "requirements.txt")
    copy_file(repo / "scripts/run_evidence_console.py", output / "scripts/run_evidence_console.py")
    copy_file(repo / "scripts/intake_local_document_candidate.py", output / "scripts/intake_local_document_candidate.py")
    shutil.copytree(repo / "src", output / "src", dirs_exist_ok=True)
    shutil.copytree(repo / "schemas", output / "schemas", dirs_exist_ok=True)
    shutil.copytree(repo / "simulation", output / "simulation", dirs_exist_ok=True)
    shutil.copytree(repo / "demo", output / "demo", dirs_exist_ok=True)
    shutil.copytree(repo / "output/pdf", output / "output/pdf", dirs_exist_ok=True)
    copy_file(repo / "tests/schema/validate_contracts.py", output / "tests/schema/validate_contracts.py")
    for name in VALID_FIXTURES:
        copy_file(
            repo / "tests/schema/fixtures/valid" / name,
            output / "tests/schema/fixtures/valid" / name,
        )
    copy_file(
        repo / "docs/workstreams/70-platform-gcp/evidence/h05-gcp-inventory-and-logs.json",
        output / "docs/workstreams/70-platform-gcp/evidence/h05-gcp-inventory-and-logs.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
