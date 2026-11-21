"""Tests for STL and GeoDetector with synthetic data."""

import numpy as np
import pandas as pd

import src.analysis.sensitivity_analysis as sa


def _panel(cells=20, years=40, seed=20261121):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(cells):
        for t in range(years):
            z = 2.0 + 1.5 * np.sin(2 * np.pi * t / 7) + rng.normal(0, 0.1)
            j = max(0.0, 0.8 * z + rng.normal(0, 0.2))
            rows.append({
                "year": 1500 + t,
                "grid_x": 100.5 + i,
                "grid_y": 30.5,
                "zaihuang_severity": z,
                "zaihuang_count": 1,
                "jinshi_count": j,
            })
    return pd.DataFrame(rows)


def test_stl_returns_one_row_per_grid(tmp_path, monkeypatch):
    monkeypatch.setattr(sa, "OUTPUT_DIR", str(tmp_path))
    df, decomp = sa.run_stl_decomposition(_panel())
    assert len(df) == 20
    assert {"var_trend", "var_seasonal", "var_resid", "sig_trend", "sig_resid"} <= set(df.columns)
    assert len(decomp) == 20 * 40


def test_geodetector_returns_q_values(tmp_path, monkeypatch):
    monkeypatch.setattr(sa, "OUTPUT_DIR", str(tmp_path))
    result = sa.run_geodetector(_panel())
    assert result is not None
    assert result["n_cells"] >= 10
    for key in ("q_zaihuang_severity", "q_longitude", "q_latitude"):
        assert 0.0 <= result[key] <= 1.0

