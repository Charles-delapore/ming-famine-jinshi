"""Tests for the A2 spillover unit builder."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "scripts" / "a2_spillover_analysis.py"
    spec = importlib.util.spec_from_file_location("a2_spillover", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


a2 = _load()


def _fixture(tmp_path):
    df = pd.DataFrame({
        "EntryRank": ["第一甲第一名", "第2甲第3名", "第3甲第10名"],
        "EntryYear": [1521, 1521, 1522],
        "X": [115.2, 115.8, 120.2],
        "Y": [28.3, 28.8, 30.2],
    })
    path = tmp_path / "jinshi.xlsx"
    df.to_excel(path, index=False)
    return path


def test_build_units_is_a_full_rectangle(tmp_path, monkeypatch):
    monkeypatch.setattr(a2, "RAW", _fixture(tmp_path))
    units = a2.build_units()

    assert {"grid_x", "grid_y", "year", "jinshi_count", "grid_id", "exam_year"} <= set(units.columns)
    assert units["jinshi_count"].sum() == 3
    assert units["grid_id"].nunique() == 2
    assert len(units) == units["grid_id"].nunique() * units["year"].nunique()
    assert (units["jinshi_count"] >= 0).all()


def test_build_units_aggregates_same_grid_year(tmp_path, monkeypatch):
    monkeypatch.setattr(a2, "RAW", _fixture(tmp_path))
    units = a2.build_units()
    cell = units[(units["grid_id"] == "115.5_28.5") & (units["exam_year"] == 1521)]
    assert int(cell["jinshi_count"].iloc[0]) == 2
