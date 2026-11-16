#!/usr/bin/env python
"""Check that the public tree contains no private or machine-specific content.

Checks
  1. absolute paths (I:/D:/E:... and C:/Users)
  2. process language ("local only", "no push")
  3. person-level columns in published CSV headers
  4. files that must not be published

Exit code 1 on any finding. Use --paths to check an explicit list (tests).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".html", ".yml", ".yaml", ".toml", ".cff",
                 ".json", ".txt", ".rst", ".cfg", ".ini"}
ABS_PATH = re.compile(r"(?<![A-Za-z])(?:[IDEFGH]):\\|C:\\Users", re.IGNORECASE)
PROCESS = re.compile(r"local only|no push", re.IGNORECASE)
PRIVATE_COLUMNS = {"personid", "person_id", "c_personid", "namechn"}
SKIP = {
    "tools/check_public_tree.py",
    "tests/test_public_tree.py",
}
FORBIDDEN_NAMES = {
    "a14_network_edges.csv",
    "a18_ego_degrees.csv",
    "a9_person_addr_link.csv",
    "a9_jinshi_1627_1644.csv",
    "a12_full_ming_famine.csv",
    "a12_full_ming_panel.csv.gz",
    "a10_coordinate_tiers.csv",
}


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True, encoding="utf-8", check=True)
    return [ROOT / line for line in out.stdout.splitlines() if line]


def check_file(path: Path) -> list[str]:
    problems = []
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        rel = str(path)
    if rel in SKIP:
        return problems
    if path.name in FORBIDDEN_NAMES:
        problems.append(f"{rel}: file must not be published")
        return problems
    if path.suffix.lower() == ".csv":
        try:
            header = path.open(encoding="utf-8", errors="replace").readline()
        except OSError:
            return problems
        fields = {f.strip().strip('"').lower() for f in header.split(",")}
        if fields & PRIVATE_COLUMNS:
            problems.append(f"{rel}: person-level column in published CSV")
        return problems
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return problems
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return problems
    for n, line in enumerate(lines, 1):
        if ABS_PATH.search(line):
            problems.append(f"{rel}:{n}: absolute path")
        if PROCESS.search(line):
            problems.append(f"{rel}:{n}: process language")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.paths if args.paths else tracked_files()
    problems = []
    for path in paths:
        if path.is_file():
            problems.extend(check_file(path))
    if problems:
        print("public-tree check failed:")
        for item in problems:
            print("  -", item)
        return 1
    print(f"public-tree check passed ({len(paths)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
