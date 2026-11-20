#!/usr/bin/env python
"""Check that release metadata agrees across files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path) -> list[str]:
    problems = []
    citation = yaml.safe_load((root / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = json.loads((root / ".zenodo.json").read_text(encoding="utf-8"))
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")

    versions = {
        "CITATION.cff": str(citation.get("version", "")),
        ".zenodo.json": str(zenodo.get("version", "")),
    }
    unique = set(versions.values())
    if len(unique) != 1:
        problems.append(f"version mismatch: {versions}")
        return problems
    version = unique.pop()
    if not re.search(rf"^## {re.escape(version)}\b", changelog, re.MULTILINE):
        problems.append(f"CHANGELOG.md has no section for {version}")

    if "2/135" not in readme:
        problems.append("README.md does not state the fixed-window result")
    if "48/135" in readme and "artefact" not in readme.lower():
        problems.append("README.md mentions 48/135 without the artefact note")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    problems = check(args.root)
    if problems:
        print("release check failed:")
        for item in problems:
            print("  -", item)
        return 1
    print("release metadata ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
