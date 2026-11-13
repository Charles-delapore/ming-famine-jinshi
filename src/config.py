"""Central configuration for the analysis layer.

All paths are resolved from environment variables so the pipeline can run on any
machine without private absolute paths:

    MING_DATA           raw data root            (default: <repo>/data/raw)
    MING_DATA_PROCESSED processed data root      (default: <repo>/data/processed)
    MING_OUTPUT         result-table root        (default: <repo>/output)
    MING_PALEO          paleoclimate data root   (default: MING_DATA/paleoclimate)
    MING_OLD_VERSION    legacy tables (optional) (default: MING_DATA/legacy)

`data/README.md` documents the expected file names.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_RAW_DIR = Path(os.environ.get("MING_DATA", PROJECT_ROOT / "data" / "raw"))
DATA_PROCESSED_DIR = Path(
    os.environ.get("MING_DATA_PROCESSED", PROJECT_ROOT / "data" / "processed")
)
OUTPUT_DIR = Path(os.environ.get("MING_OUTPUT", PROJECT_ROOT / "output"))
PALEO_DIR = Path(os.environ.get("MING_PALEO", DATA_RAW_DIR / "paleoclimate"))
LEGACY_DIR = Path(os.environ.get("MING_OLD_VERSION", DATA_RAW_DIR / "legacy"))

DATA_PATHS = {
    # paleoclimate reconstructions (public scientific datasets)
    "mann2009_nhall": PALEO_DIR / "mann2009_nhall.txt",
    "mann2009_amo": PALEO_DIR / "mann2009_amo.txt",
    "schneider2015_temp": PALEO_DIR / "schneider2015_temp.txt",
    "schneider2015_mxd": PALEO_DIR / "schneider2015_mxd.txt",
    # event tables (private research data; see data/README.md)
    "table_citys": DATA_RAW_DIR / "table_citys.xlsx",
    "table_level": DATA_RAW_DIR / "table_level.xlsx",
    "table_levels": DATA_RAW_DIR / "table_levels.xlsx",
    "table_general": DATA_RAW_DIR / "table_general.xlsx",
    "table_general2": DATA_RAW_DIR / "table_general2.xlsx",
    "table_general1627_1644": DATA_RAW_DIR / "table_general1627_1644.xlsx",
    "table_generals1521_1619": DATA_RAW_DIR / "table_generals1521_1619.xlsx",
    "ming_general": DATA_RAW_DIR / "ming_general.csv",
    "merged_data": DATA_RAW_DIR / "merged_data.csv",
    "grid_data_20_load": DATA_RAW_DIR / "grid_data_20_load.csv",
    # optional legacy location (kept for backwards compatibility)
    "legacy_root": LEGACY_DIR,
}

OUTPUT_PATHS = {
    "clustered_levels": OUTPUT_DIR / "clustered_levels.xlsx",
    "clustered_jinshi": OUTPUT_DIR / "clustered_jinshi.xlsx",
    "merged_data": OUTPUT_DIR / "merged_data.xlsx",
    "grid_data": OUTPUT_DIR / "grid_data.csv",
    "similarity_results": OUTPUT_DIR / "similarity_results.xlsx",
    "lagged_similarity_results": OUTPUT_DIR / "lagged_similarity_results.xlsx",
}

CLUSTER_PARAMS = {
    "zaihuang_ssdbcan": {
        "eps": 0.7,
        "min_samples": 9,
        "weights": [1.0, 1.0, 0.3, 0.1],
        "max_cluster_size": 100,
        "important_levels": [4, 5],
    },
    "jinshi_ssdbcan": {
        "eps": 0.7,
        "min_samples": 3,
        "weights": [1.0, 1.0, 0.3, 0.1],
        "max_cluster_size": 100,
        "important_levels": [1, 2],
    },
    "zaihuang_st_dbscan": {
        "eps1": 0.3,
        "eps2": 2,
        "eps3": 1,
        "min_samples": 3,
    },
    "zaihuang_gmm": {
        "n_components_range": range(1, 60),
        "covariance_type": "full",
    },
    "jinshi_gmm": {
        "n_components_range": range(2, 11),
        "covariance_type": "full",
    },
    "grid_st_dbscan": {
        "eps1": 0.5,
        "eps2": 1,
        "min_samples": 5,
    },
}

COMPARE_PARAMS = {
    "max_lag": 20,
    "time_weight": 0.7,
    "space_weight": 0.3,
    "n_permutations": 1000,
    "max_workers": 1,
    "significance_level": 0.05,
}

# NOTE: these legacy bounds are kept as published; y_max looks like an invalid
# latitude (120.257776). Verify before re-running grid_integrator on new data.
GRID_PARAMS = {
    "x_min": 40.850080,
    "x_max": 124.850080,
    "y_min": 18.257776,
    "y_max": 120.257776,
    "grid_size": 1,
    "year_start": 1512,
    "year_end": 1532,
}

VISUALIZATION = {
    "font_sans_serif": ["Arial", "Microsoft YaHei", "DejaVu Sans"],
    "axes_unicode_minus": False,
    "figsize_2d": (12, 8),
    "figsize_3d": (14, 10),
    "dpi": 300,
}
