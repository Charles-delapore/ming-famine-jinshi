"""Synthetic checks for the grid-level Granger helper."""

import numpy as np
import pandas as pd

from src.analysis.grid_analysis import GridGrangerCausality


def _panel(x, y):
    return pd.DataFrame({
        "year": np.arange(1500, 1500 + len(x)),
        "grid_x": 115.5,
        "grid_y": 28.5,
        "zaihuang_severity": x,
        "jinshi_count": y,
    })


def test_detects_lagged_dependence():
    rng = np.random.default_rng(20261119)
    n = 120
    x = np.abs(rng.normal(1.0, 0.3, n))
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.6 * x[t - 1] + rng.normal(0, 0.2)
    y = np.clip(y, 0, None)
    result = GridGrangerCausality(max_lag=5, significance=0.05, min_obs=30)
    out = result.analyze_grid_causality(_panel(x, y))
    assert len(out) == 1
    assert bool(out.iloc[0]["gc_z_to_j_causal"])
    assert int(out.iloc[0]["gc_z_to_j_lag"]) == 1


def test_constant_series_is_not_causal():
    n = 120
    x = np.ones(n)
    y = np.ones(n)
    result = GridGrangerCausality(max_lag=5, significance=0.05, min_obs=30)
    out = result.analyze_grid_causality(_panel(x, y))
    assert not bool(out.iloc[0]["gc_z_to_j_causal"])
