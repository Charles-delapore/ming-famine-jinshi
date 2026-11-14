"""Null calibration for the lag-selected Granger panel (local analysis).

Within each grid, permute the Jinshi series across years (famine fixed), rerun
the identical max-F Granger + BH FDR pipeline, and record the number of FDR
grids and the lag distribution among nominally significant grids.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r".")
sys.path.insert(0, str(ROOT))
from src.analysis.grid_analysis import GridGrangerCausality, fdr_correction  # noqa: E402

PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
OUT = ROOT / "data" / "derived" / "long_tail_null_permutation.csv"

REPS = 50
SEED = 20261114


def main() -> None:
    panel = pd.read_csv(PANEL)
    groups = panel.groupby(["grid_x", "grid_y"], sort=False)
    analyzer = GridGrangerCausality(max_lag=20, significance=0.05, min_obs=30)
    rows = []
    for rep in range(REPS):
        rng = np.random.default_rng(SEED + rep)
        p = panel.copy()
        p["jinshi_count"] = groups["jinshi_count"].transform(
            lambda s: rng.permutation(s.values)
        )
        r = analyzer.analyze_grid_causality(p)
        sig, _ = fdr_correction(r["gc_z_to_j_pval"].values, alpha=0.05)
        r["fdr"] = sig
        nom = r[r["gc_z_to_j_pval"] < 0.05]
        lags = nom["gc_z_to_j_lag"]
        rows.append({
            "rep": rep,
            "grids_tested": len(r),
            "nominal_p05": int(len(nom)),
            "fdr_sig": int(sig.sum()),
            "nominal_short_share": float((lags <= 5).mean()) if len(lags) else np.nan,
            "nominal_long15_share": float((lags >= 15).mean()) if len(lags) else np.nan,
            "nominal_median_lag": float(lags.median()) if len(lags) else np.nan,
        })
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print(rep, rows[-1], flush=True)


if __name__ == "__main__":
    main()
