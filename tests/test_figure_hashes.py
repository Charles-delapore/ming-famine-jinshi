"""Tests for the figure hash checker."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "tools" / "check_figure_hashes.py"
    spec = importlib.util.spec_from_file_location("check_figure_hashes", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load()


def _fixture(tmp_path, digest):
    (tmp_path / "figures").mkdir()
    figure = tmp_path / "figures" / "fig.png"
    figure.write_bytes(b"payload")
    with (tmp_path / "figures" / "figure_manifest.csv").open(
            "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["file", "sha256"])
        writer.writeheader()
        writer.writerow({"file": "figures/fig.png", "sha256": digest})
    return tmp_path


def test_matching_hash(tmp_path):
    digest = hashlib.sha256(b"payload").hexdigest()
    assert checker.check(_fixture(tmp_path, digest)) == []


def test_mismatched_hash(tmp_path):
    assert checker.check(_fixture(tmp_path, "0" * 64))
