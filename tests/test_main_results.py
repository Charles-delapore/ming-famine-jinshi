"""Contract tests for the published main-results table."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data" / "derived" / "a3_main_results.csv"


def _metrics():
    df = pd.read_csv(TABLE)
    return dict(zip(df["metric"], df["value"]))


def test_headline_counts():
    m = _metrics()
    assert int(m["fixed_1_5_joint_FDR_grids"]) == 2
    assert int(m["multiscale_1-5_FDR_grids"]) == 8
    assert int(m["multiscale_5-10_FDR_grids"]) == 0
    assert int(m["multiscale_11-20_FDR_grids"]) == 0


def test_lag_search_is_not_the_headline():
    m = _metrics()
    assert int(m["within_grid_Bonferroni_20"]) == 7
    assert int(m["max_lag_20_FDR"]) == 48
    assert int(m["max_lag_20_FDR"]) > int(m["within_grid_Bonferroni_20"]) > int(
        m["fixed_1_5_joint_FDR_grids"]
    )


def test_descriptive_results():
    m = _metrics()
    assert int(m["GWR_significant"]) == 123
    assert int(m["GWR_cells"]) == 159
    assert abs(float(m["GeoDetector_q_severity"]) - 0.3368) < 1e-4
    assert abs(float(m["GWR_coef_r_v02_v03"]) - 0.9914) < 1e-4


def test_readme_uses_the_fixed_window():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "2/135" in text
    assert re.search(r"48/135.*artefact", text)
