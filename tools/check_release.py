#!/usr/bin/env python
"""Check that release metadata agrees across files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    versions = {
        "CITATION.cff": str(citation.get("version", "")),
        ".zenodo.json": str(zenodo.get("version", "")),
    }
    unique = set(versions.values())
    if len(unique) != 1:
        print("version mismatch:", versions)
        return 1
    version = unique.pop()
    if not re.search(rf"^## {re.escape(version)}\b", changelog, re.MULTILINE):
        print(f"CHANGELOG.md has no section for {version}")
        return 1

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "2/135" not in readme:
        print("README.md does not state the fixed-window result")
        return 1
    if "48/135" in readme and "artefact" not in readme.lower():
        print("README.md mentions 48/135 without the artefact note")
        return 1

    print(f"release metadata ok ({version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
