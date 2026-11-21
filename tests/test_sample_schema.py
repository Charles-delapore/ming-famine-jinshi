"""The synthetic sample must keep the production column contract."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"


def test_sample_csv_columns():
    df = pd.read_csv(SAMPLE / "grid_data_enriched.csv")
    required = {"year", "grid_x", "grid_y", "zaihuang_severity", "jinshi_count"}
    assert required <= set(df.columns)
    assert len(df) > 0


def test_sample_workbooks_exist():
    expected = [
        "clustered_jinshi.xlsx",
        "clustered_levels.xlsx",
        "geodetector_results.xlsx",
        "gwr_coefficients.xlsx",
        "grid_granger_causality.xlsx",
        "multiscale_causal_short_term.xlsx",
        "stl_decomposition_results.xlsx",
    ]
    for name in expected:
        assert (SAMPLE / name).exists(), name
