"""Tests for the A1 rank-share unit builder."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "scripts" / "a1_rank_analysis.py"
    spec = importlib.util.spec_from_file_location("a1_rank", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


a1 = _load()


def _fixture(tmp_path):
    rows = []
    for year in range(1521, 1526):
        rows.extend([
            {"EntryRank": "第一甲第一名", "EntryYear": year, "X": 115.2, "Y": 28.3},
            {"EntryRank": "第2甲第3名", "EntryYear": year, "X": 115.2, "Y": 28.3},
            {"EntryRank": "第3甲第10名", "EntryYear": year, "X": 115.2, "Y": 28.3},
        ])
    path = tmp_path / "jinshi.xlsx"
    pd.DataFrame(rows).to_excel(path, index=False)
    return path


def test_rank_units_share_and_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr(a1, "RAW", _fixture(tmp_path))
    units = a1.build_units()
    assert len(units) == 5
    assert set(units["total"]) == {3}
    assert units["share_top"].round(6).eq(round(2 / 3, 6)).all()
    assert units["grid_id"].nunique() == 1
    assert units["log_total"].round(6).eq(round(float(np.log(3)), 6)).all()
