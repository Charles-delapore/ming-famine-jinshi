"""Generate deterministic, synthetic sample data for the portfolio repo.

The samples mirror the column names and dtypes of the Work_ming v5 result
tables, but **no value is a real historical record**. They exist so that the
analysis code and figure scripts can be exercised without redistributing the
private event tables or the CHGIS basemap.

Seed: 20261113.
"""

from __future__ import annotations

import io
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261113)

EXAM_YEARS = [1523, 1526, 1529, 1532, 1535, 1538, 1541, 1544, 1547, 1550,
              1553, 1556, 1559, 1562, 1565, 1568, 1571, 1574, 1577, 1580,
              1583, 1586, 1589, 1592, 1595, 1598, 1601, 1604, 1607, 1610,
              1613, 1616, 1619]

GRID_X = [100.5 + 2 * i for i in range(10)]
GRID_Y = [20.5 + 3 * j for j in range(6)]
GRIDS = [(x, y) for y in GRID_Y for x in GRID_X]


def make_events() -> None:
    n = 400
    df = pd.DataFrame(
        {
            "_id_level": np.arange(1, n + 1),
            "title_level": [f"Sample event {i:04d}" for i in range(1, n + 1)],
            "year": RNG.integers(1522, 1620, n),
            "code": RNG.integers(100000, 999999, n),
            "level": RNG.choice([1, 2, 3, 4, 5], n, p=[0.05, 0.35, 0.30, 0.25, 0.05]),
            "_id_city": RNG.integers(100000, 999999, n),
            "title_city": [f"Sample city {i:02d}" for i in RNG.integers(1, 40, n)],
            "type": "Point",
            "x": RNG.uniform(100, 122, n),
            "y": RNG.uniform(18, 41, n),
            "cluster": RNG.integers(1, 13, n),
        }
    ).sort_values("year")
    df.to_excel(OUT / "clustered_levels.xlsx", index=False)

    n = 120
    jinshi = pd.DataFrame(
        {
            "NameChn": [f"Sample graduate {i:03d}" for i in range(1, n + 1)],
            "IndexYear": RNG.choice(EXAM_YEARS, n),
            "EntryChn": "Sample exam",
            "EntryYear": RNG.choice(EXAM_YEARS, n),
            "EntryRank": [f"第2甲第{i}名" for i in RNG.integers(1, 200, n)],
            "AddrName": [f"Sample place {i:02d}" for i in RNG.integers(1, 40, n)],
            "AddrChn": [f"样例地点{i:02d}" for i in RNG.integers(1, 40, n)],
            "X": np.clip(RNG.normal(116, 3.2, n), 101, 122),
            "Y": np.clip(RNG.normal(31, 3.6, n), 20, 40),
            "xy_count": RNG.integers(1, 10, n),
            "level": RNG.choice([1, 2], n, p=[0.04, 0.96]),
            "cluster": RNG.integers(1, 9, n),
        }
    ).sort_values("EntryYear")
    jinshi.to_excel(OUT / "clustered_jinshi.xlsx", index=False)


def make_grid_outputs() -> None:
    gwr = pd.DataFrame(
        {
            "grid_x": [g[0] for g in GRIDS],
            "grid_y": [g[1] for g in GRIDS],
            "zaihuang_severity": RNG.gamma(2, 0.15, len(GRIDS)),
            "jinshi_count": RNG.poisson(0.8, len(GRIDS)),
            "gwr_coef": np.clip(RNG.normal(0.65, 0.45, len(GRIDS)), -0.30, 2.0),
            "gwr_tval": RNG.normal(1.8, 1.2, len(GRIDS)),
            "gwr_local_r2": RNG.beta(2.5, 2.0, len(GRIDS)) * 0.9,
        }
    )
    # a few negative coefficients in the southwest, to exercise the diverging map
    for idx in [0, 1, 10]:
        gwr.loc[idx, "gwr_coef"] = -0.18
    gwr["gwr_sig"] = gwr["gwr_tval"].abs() > 1.96
    gwr.to_excel(OUT / "gwr_coefficients.xlsx", index=False)

    pvals = RNG.uniform(0, 1, len(GRIDS))
    qvals = np.clip(pvals * 1.6, 0, 1)
    granger = pd.DataFrame(
        {
            "grid_x": [g[0] for g in GRIDS],
            "grid_y": [g[1] for g in GRIDS],
            "n_years": 114,
            "zaihuang_years": RNG.integers(3, 30, len(GRIDS)),
            "jinshi_years": RNG.integers(3, 20, len(GRIDS)),
            "gc_z_to_j_causal": pvals < 0.05,
            "gc_z_to_j_lag": RNG.integers(1, 10, len(GRIDS)),
            "gc_z_to_j_fstat": RNG.gamma(3, 2, len(GRIDS)),
            "gc_z_to_j_pval": pvals,
            "gc_j_to_z_causal": RNG.uniform(0, 1, len(GRIDS)) < 0.05,
            "gc_j_to_z_lag": RNG.integers(1, 10, len(GRIDS)),
            "gc_j_to_z_fstat": RNG.gamma(2, 1.5, len(GRIDS)),
            "gc_j_to_z_pval": RNG.uniform(0, 1, len(GRIDS)),
            "causal_direction": RNG.choice(
                ["none", "z->j", "j->z", "bidirectional"], len(GRIDS),
                p=[0.45, 0.25, 0.20, 0.10],
            ),
            "gc_z_to_j_qval": qvals,
            "gc_z_to_j_fdr_sig": qvals < 0.05,
        }
    )
    granger.to_excel(OUT / "grid_granger_causality.xlsx", index=False)

    # 20-year sample panel for the graphical abstract
    years = np.arange(1520, 1540)
    rows = []
    for x, y in GRIDS:
        base_sev = RNG.gamma(2, 0.05)
        base_j = RNG.poisson(0.1)
        for year in years:
            rows.append(
                {
                    "year": year,
                    "grid_x": x,
                    "grid_y": y,
                    "zaihuang_level": RNG.choice([0, 1, 2, 3, 4, 5], p=[0.8, 0.08, 0.05, 0.04, 0.02, 0.01]),
                    "zaihuang_count": RNG.poisson(0.2),
                    "zaihuang_severity": max(0.0, base_sev + RNG.normal(0, 0.02)),
                    "jinshi_count": max(0, base_j + RNG.poisson(0.03)),
                    "cumulative_severity": 0.0,
                    "drought_duration": 0,
                    "consecutive_drought_years": 0,
                    "max_severity_5yr": 0.0,
                    "drought_frequency_10yr": 0.0,
                    "zaihuang_lag1": 0.0,
                    "zaihuang_lag3": 0.0,
                    "zaihuang_lag5": 0.0,
                    "zaihuang_lag10": 0.0,
                    "zaihuang_lag15": 0.0,
                    "zaihuang_lag20": 0.0,
                    "jinshi_lag1": 0.0,
                    "jinshi_lag3": 0.0,
                    "zaihuang_ma5": 0.0,
                    "jinshi_ma5": 0.0,
                    "severity_intensity": 0.0,
                }
            )
    pd.DataFrame(rows).to_csv(OUT / "grid_data_enriched.csv", index=False)

    # multiscale models: short has a few signals, medium/long are null by design
    for horizon, n_sig in [("short", 6), ("medium", 0), ("long", 0)]:
        p = RNG.uniform(0, 1, len(GRIDS))
        sig = np.zeros(len(GRIDS), dtype=bool)
        sig[:n_sig] = True
        df = pd.DataFrame(
            {
                "grid_x": [g[0] for g in GRIDS],
                "grid_y": [g[1] for g in GRIDS],
                "r_squared": RNG.uniform(0.005, 0.08, len(GRIDS)),
                "f_stat": RNG.gamma(2, 1, len(GRIDS)),
                "p_value": p,
                "significant": p < 0.05,
                "n_obs": 114,
                "has_collinearity": False,
                "model_type": "ols",
                "selected_features": "lag1",
                "n_features": 1,
                "coef_lag1": RNG.normal(0, 0.05, len(GRIDS)),
                "vif_lag1": 1.0,
                "max_vif": 1.0,
                "coef_lag3": np.nan,
                "vif_lag3": np.nan,
                "coef_lag5": np.nan,
                "vif_lag5": np.nan,
                "q_value": np.where(sig, RNG.uniform(0.001, 0.04, len(GRIDS)), 1.0),
                "fdr_significant": sig,
            }
        )
        df.to_excel(OUT / f"multiscale_causal_{horizon}_term.xlsx", index=False)

    pd.DataFrame(
        {
            "q_zaihuang_severity": [0.35],
            "q_longitude": [0.19],
            "q_latitude": [0.13],
            "n_cells": [len(GRIDS)],
        }
    ).to_excel(OUT / "geodetector_results.xlsx", index=False)


def make_supplementary() -> None:
    n = 80
    pd.DataFrame(
        {
            "jinshi_cluster": RNG.integers(1, 9, n),
            "zaihuang_cluster": RNG.integers(1, 13, n),
            "max_similarity": RNG.uniform(0.2, 0.9, n),
            "best_lag": RNG.integers(-20, 21, n),
            "p_value": RNG.uniform(0, 1, n),
            "cross_correlation": RNG.normal(0, 0.2, n),
            "p_value_corr": RNG.uniform(0, 1, n),
            "significant": RNG.uniform(0, 1, n) < 0.1,
            "significant_corr": RNG.uniform(0, 1, n) < 0.1,
        }
    ).to_excel(OUT / "lagged_similarity_results.xlsx", index=False)

    n = len(GRIDS)
    pd.DataFrame(
        {
            "grid_x": [g[0] for g in GRIDS],
            "grid_y": [g[1] for g in GRIDS],
            "n_obs": 114,
            "var_trend": RNG.uniform(0, 1, n),
            "var_seasonal": RNG.uniform(0, 1, n),
            "var_resid": RNG.uniform(0, 2, n),
            "corr_trend_jinshi": RNG.normal(0, 0.2, n),
            "pval_trend_jinshi": RNG.uniform(0, 1, n),
            "corr_resid_jinshi": RNG.normal(0, 0.2, n),
            "pval_resid_jinshi": RNG.uniform(0, 1, n),
            "sig_trend": RNG.uniform(0, 1, n) < 0.1,
            "sig_resid": RNG.uniform(0, 1, n) < 0.1,
        }
    ).to_excel(OUT / "stl_decomposition_results.xlsx", index=False)

    n = len(GRIDS)
    pd.DataFrame(
        {
            "paleoclimate_var": "sample_reconstruction",
            "grid_x": [g[0] for g in GRIDS],
            "grid_y": [g[1] for g in GRIDS],
            "n_obs": 114,
            "partial_corr_z_j": RNG.normal(0, 0.1, n),
            "partial_corr_pval": RNG.uniform(0, 1, n),
            "partial_corr_sig": RNG.uniform(0, 1, n) < 0.05,
        }
    ).to_excel(OUT / "paleoclimate_partial_correlation.xlsx", index=False)

    n = 30
    pd.DataFrame(
        {
            "grid_x": RNG.choice([g[0] for g in GRIDS], n),
            "grid_y": RNG.choice([g[1] for g in GRIDS], n),
            "n_obs": 61,
            "max_rho_Z_to_MJ": RNG.uniform(0, 0.6, n),
            "max_rho_J_to_MZ": RNG.uniform(0, 0.6, n),
            "max_L_Z_to_MJ": RNG.integers(5, 40, n),
            "max_L_J_to_MZ": RNG.integers(5, 40, n),
            "first_rho_Z_to_MJ": RNG.normal(0, 0.2, n),
            "last_rho_Z_to_MJ": RNG.normal(0, 0.2, n),
            "first_rho_J_to_MZ": RNG.normal(0, 0.2, n),
            "last_rho_J_to_MZ": RNG.normal(0, 0.2, n),
            "convergence_Z_to_MJ": RNG.uniform(0, 1, n) < 0.2,
            "convergence_J_to_MZ": RNG.uniform(0, 1, n) < 0.2,
            "ccm_direction": "None",
        }
    ).to_excel(OUT / "ccm_summary.xlsx", index=False)

    n = 12
    pd.DataFrame(
        {
            "cluster_id": np.arange(n),
            "n_events": RNG.integers(5, 100, n),
            "start_year": RNG.integers(1522, 1600, n),
            "end_year": RNG.integers(1560, 1620, n),
            "duration": RNG.integers(1, 90, n),
            "centroid_x": RNG.uniform(100, 122, n),
            "centroid_y": RNG.uniform(18, 41, n),
            "volume": RNG.uniform(10, 200, n),
            "severity": RNG.uniform(1, 50, n),
            "max_level": RNG.integers(1, 6, n),
            "avg_severity": RNG.uniform(1, 20, n),
            "total_severity": RNG.uniform(10, 200, n),
            "n_locations": RNG.integers(1, 10, n),
        }
    ).to_excel(OUT / "cluster_characteristics_enhanced.xlsx", index=False)


def ensure_basemap() -> None:
    """Download Natural Earth 110m countries and keep a simplified China polygon."""
    target = OUT / "basemap_china.geojson"
    if target.exists():
        print(f"basemap exists: {target}")
        return
    url = "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
    try:
        data = urllib.request.urlopen(url, timeout=60).read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            zf.extractall(OUT / "_ne_tmp")
        import geopandas as gpd

        shp = next((OUT / "_ne_tmp").glob("*.shp"))
        world = gpd.read_file(shp)
        china = world[world["ADMIN"].isin(["China"])].to_crs(4326)
        china = china[["ADMIN", "geometry"]].copy()
        china["source"] = "Natural Earth 1:110m admin-0 (public domain)"
        china.to_file(target, driver="GeoJSON")
        shutil.rmtree(OUT / "_ne_tmp", ignore_errors=True)
        print(f"basemap written: {target}")
    except Exception as exc:  # network or GDAL issue
        print(f"basemap download failed ({exc}); writing a coarse synthetic placeholder")
        import geopandas as gpd
        from shapely.geometry import box

        gdf = gpd.GeoDataFrame(
            {"ADMIN": ["Synthetic placeholder"], "source": ["not a real boundary"]},
            geometry=[box(98, 18, 123, 42)],
            crs=4326,
        )
        gdf.to_file(target, driver="GeoJSON")


if __name__ == "__main__":
    make_events()
    make_grid_outputs()
    make_supplementary()
    ensure_basemap()
    print("sample data written to", OUT)

