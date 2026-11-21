#!/usr/bin/env python
"""Verify that the figure manifest hashes match the files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path) -> list[str]:
    manifest = root / "figures" / "figure_manifest.csv"
    rows = list(csv.DictReader(manifest.open(encoding="utf-8")))
    problems = []
    for row in rows:
        path = root / row["file"]
        if not path.exists():
            problems.append(f"{row['file']}: missing")
            continue
        expected = row.get("sha256", "")
        if not expected:
            problems.append(f"{row['file']}: no sha256")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append(f"{row['file']}: hash mismatch")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    problems = check(args.root)
    if problems:
        print("figure hash check failed:")
        for item in problems:
            print("  -", item)
        return 1
    print("figure hashes ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
