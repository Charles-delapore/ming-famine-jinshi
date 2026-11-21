#!/usr/bin/env python
"""Check relative Markdown links in the public documentation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)]+)\)")
ROOT_FILES = ["README.md", "README.zh.md", "CONTRIBUTING.md",
              "DATA_AVAILABILITY.md", "CHANGELOG.md"]


def files(root: Path) -> list[Path]:
    out = [root / name for name in ROOT_FILES if (root / name).exists()]
    out.extend(sorted((root / "docs").glob("*.md")))
    return out


def check(root: Path) -> list[str]:
    missing = []
    for path in files(root):
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#",
                                  "sandbox://")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                missing.append(f"{path.relative_to(root)} -> {target}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    missing = check(args.root)
    if missing:
        print("broken links:")
        for item in missing:
            print("  -", item)
        return 1
    print("doc links ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
