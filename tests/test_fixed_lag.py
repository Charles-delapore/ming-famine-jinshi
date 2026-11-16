"""Tests for the fixed-lag joint Granger test used in Route A."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    path = ROOT / "scripts" / "long_tail_analysis.py"
    spec = importlib.util.spec_from_file_location("long_tail_analysis", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load_module()


def _statsmodels_p(x, y, lags=(1, 2, 3, 4, 5)):
    m = max(lags)
    n = len(y)
    y_t = y[m:]
    X_r = np.column_stack([y[m - l:n - l] for l in lags])
    X_u = np.column_stack([X_r] + [x[m - l:n - l] for l in lags])
    ur = sm.OLS(y_t, sm.add_constant(X_u)).fit()
    rr = sm.OLS(y_t, sm.add_constant(X_r)).fit()
    test = ur.f_test(np.eye(X_u.shape[1] + 1)[X_r.shape[1] + 1:])
    return float(test.pvalue)


def test_detects_dependence():
    rng = np.random.default_rng(20261116)
    n = 160
    x = rng.normal(size=n)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.6 * y[t - 1] + 0.5 * x[t - 1] + rng.normal(scale=0.3)
    assert mod.fixed_lag_pvalue(x, y, (1, 2, 3, 4, 5)) < 0.01


def test_null_is_not_significant():
    rng = np.random.default_rng(20261117)
    n = 160
    x = rng.normal(size=n)
    y = rng.normal(size=n)
    assert mod.fixed_lag_pvalue(x, y, (1, 2, 3, 4, 5)) > 0.05


def test_matches_statsmodels():
    rng = np.random.default_rng(20261118)
    n = 140
    x = rng.normal(size=n)
    y = 0.4 * np.roll(x, 2) + rng.normal(scale=0.8, size=n)
    ours = mod.fixed_lag_pvalue(x, y, (1, 2, 3, 4, 5))
    ref = _statsmodels_p(x, y)
    assert ours == pytest.approx(ref, rel=1e-9, abs=1e-12)
