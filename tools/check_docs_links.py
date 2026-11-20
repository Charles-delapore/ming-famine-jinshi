#!/usr/bin/env python
"""Check relative Markdown links in the public documentation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)]+)\)")
ROOT_FILES = ["README.md", "README.zh.md", "CONTRIBUTING.md",
              "DATA_AVAILABILITY.md", "CHANGELOG.md"]


def files() -> list[Path]:
    out = [ROOT / name for name in ROOT_FILES if (ROOT / name).exists()]
    out.extend(sorted((ROOT / "docs").glob("*.md")))
    return out


def main() -> int:
    missing = []
    total = 0
    for path in files():
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#",
                                  "sandbox://")):
                continue
            total += 1
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    if missing:
        print("broken links:")
        for item in missing:
            print("  -", item)
        return 1
    print(f"doc links ok ({total} relative links)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
