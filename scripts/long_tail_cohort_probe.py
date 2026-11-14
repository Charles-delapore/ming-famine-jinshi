"""Exploratory birth-cohort probe for the 20-year claim.

The thesis reports a 20-year lag peak from cluster similarity. This probe asks
whether the same claim appears in a cohort design: count future Jinshi by birth
grid and birth year, merge famine exposure at birth / ages 0-5, and estimate
two-way fixed-effects models.

This is NOT a causal test: famine and Jinshi records share documentation
intensity, so a positive coefficient is expected under reporting bias. It is
recorded to show that the 20-year claim does not replicate in an independent
design, not to support a new claim.

Output: data/derived/long_tail_cohort_probe.csv
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
RAW = Path(r"data/private/明进士.xlsx")
OUT = ROOT / "data" / "derived" / "long_tail_cohort_probe.csv"
BIRTH_YEARS = range(1506, 1590)


def build() -> pd.DataFrame:
    panel = pd.read_csv(PANEL)
    raw = pd.read_excel(RAW)
    raw["entry"] = pd.to_numeric(raw["EntryYear"], errors="coerce")
    raw["birth"] = pd.to_numeric(raw["IndexYear"], errors="coerce")
    sub = raw[raw.entry.between(1521, 1619)].dropna(subset=["birth", "X", "Y"]).copy()
    sub["age"] = sub.entry - sub.birth
    sub = sub[sub.age.between(15, 60)].copy()
    sub["grid_x"] = np.floor(sub["X"]) + 0.5
    sub["grid_y"] = np.floor(sub["Y"]) + 0.5
    counts = (sub.groupby(["grid_x", "grid_y", "birth"]).size()
              .rename("jinshi").reset_index())

    grids = panel[["grid_x", "grid_y"]].drop_duplicates()
    years = pd.DataFrame({"year": list(BIRTH_YEARS)})
    full = grids.merge(years, how="cross")
    full = full.merge(counts.rename(columns={"birth": "year"}),
                      on=["grid_x", "grid_y", "year"], how="left")
    full["jinshi"] = full["jinshi"].fillna(0)

    z = panel[["year", "grid_x", "grid_y", "zaihuang_severity"]].copy()
    full = full.merge(z, on=["year", "grid_x", "grid_y"], how="left")
    full["zaihuang_severity"] = full["zaihuang_severity"].fillna(0)
    z_idx = z.set_index(["grid_x", "grid_y", "year"])["zaihuang_severity"]
    full["sev_birth"] = full["zaihuang_severity"]
    full["sev_0_5"] = [
        float(sum(z_idx.get((r.grid_x, r.grid_y, r.year + k), 0.0) for k in range(6)))
        for r in full.itertuples()
    ]
    return full


def twoway(v: np.ndarray, g: np.ndarray, t: np.ndarray, iters: int = 40) -> np.ndarray:
    x = np.asarray(v, dtype=float).copy()
    for _ in range(iters):
        x = x - pd.Series(x).groupby(g).transform("mean").values
        x = x - pd.Series(x).groupby(t).transform("mean").values
    return x


def main() -> None:
    full = build()
    g = (full.grid_x.astype(str) + "_" + full.grid_y.astype(str)).values
    t = full.year.values
    rows = []
    for outcome_name, y in (("log1p_count", np.log1p(full.jinshi.values)),
                            ("any_jinshi", (full.jinshi.values > 0).astype(float))):
        for exposure in ("sev_birth", "sev_0_5"):
            xd = twoway(full[exposure].values, g, t)
            yd = twoway(y, g, t)
            res = sm.OLS(yd, sm.add_constant(xd)).fit(
                cov_type="cluster", cov_kwds={"groups": g})
            rows.append({
                "outcome": outcome_name,
                "exposure": exposure,
                "coef": float(res.params[1]),
                "se": float(res.bse[1]),
                "p": float(res.pvalues[1]),
                "n_cells": int(len(full)),
                "share_cells_with_jinshi": float((full.jinshi > 0).mean()),
            })
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.round(5).to_string(index=False))


if __name__ == "__main__":
    main()
