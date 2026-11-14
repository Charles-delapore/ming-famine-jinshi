"""Robustness check: does the rank-encoding defect change the grid results?

Two grid panels are built from the same famine series:

  v02  ming_general + the old literal-filter Jinshi extension (918 records)
  v03  ming_general + normalized 1甲/2甲 elite (2,841 records)

The grid-level Granger and GWR models are then re-estimated on both panels.
The 911 clustered layer is *not* used by these models; it only feeds the
cluster-level analysis and the point maps. This script quantifies how much the
grid results move when the encoding bug is fixed.

Usage:
    set MING_JINSHI_RAW=I:\\L\\Work_ming\\raw\\明进士.xlsx
    set MING_FAMINE_MERGED=I:\\L\\Work_ming\\old-version\\workload_明代\\database\\merged_data.csv
    set MING_FAMINE_EXT=I:\\L\\Work_ming\\old-version\\000work_ming\\000_load\\table_generals1521_1619.xlsx
    set MING_CITYS=I:\\L\\Work_ming\\old-version\\000work_ming\\000_load\\table_citys.xlsx
    set MING_JINSHI_ALL=I:\\L\\Work_ming\\old-version\\workload_明代\\database\\ming_general.csv
    python scripts/corrected_robustness.py
"""

from __future__ import annotations

import json
import os
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("MING_JINSHI_RAW", ROOT / "data" / "raw" / "明进士.xlsx"))
FAMINE_MERGED = Path(os.environ.get("MING_FAMINE_MERGED", ROOT / "data" / "raw" / "merged_data.csv"))
FAMINE_EXT = Path(os.environ.get("MING_FAMINE_EXT", ROOT / "data" / "raw" / "table_generals1521_1619.xlsx"))
CITYS = Path(os.environ.get("MING_CITYS", ROOT / "data" / "raw" / "table_citys.xlsx"))
JINSHI_ALL = Path(os.environ.get("MING_JINSHI_ALL", ROOT / "data" / "raw" / "ming_general.csv"))
OUT = Path(os.environ.get("MING_V03_OUT", ROOT / "output" / "v03"))
DOC = ROOT / "docs" / "corrected_robustness.md"

RANK_RE = re.compile(r"^\s*(?:第)?\s*([一二三123])\s*甲")
NUM = {"一": 1, "二": 2, "三": 3, "1": 1, "2": 2, "3": 3}
GRID = 1.0


def rank_class(value: object) -> int | None:
    if pd.isna(value):
        return None
    match = RANK_RE.match(str(value))
    return NUM[match.group(1)] if match else None


# --------------------------------------------------------------------- data
def load_famine() -> pd.DataFrame:
    merged = pd.read_csv(FAMINE_MERGED).rename(columns={"x": "X", "y": "Y"})
    city = pd.read_excel(CITYS)
    city = city[["code", "x", "y"]].drop_duplicates("code")
    ext = pd.read_excel(FAMINE_EXT).merge(city, on="code", how="inner")
    ext = ext.rename(columns={"x": "X", "y": "Y"})
    full = pd.concat(
        [merged[["year", "X", "Y", "level"]], ext[["year", "X", "Y", "level"]]],
        ignore_index=True,
    )
    full = full.drop_duplicates(subset=["year", "X", "Y"], keep="last")
    full["year"] = full["year"].astype(int)
    return full


def load_jinshi() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(RAW)
    raw["year"] = pd.to_numeric(raw.get("EntryYear"), errors="coerce")
    raw["cls"] = raw.get("EntryRank").map(rank_class)
    raw["arabic"] = raw.get("EntryRank").astype(str).str.contains(r"第[123]甲", na=False)

    old = raw[raw["arabic"] & raw["cls"].isin([1, 2]) & raw["year"].between(1521, 1619)]
    old = old.dropna(subset=["X", "Y"]).drop_duplicates("PersonID")
    new = raw[raw["cls"].isin([1, 2]) & raw["year"].between(1521, 1619)]
    new = new.dropna(subset=["X", "Y"]).drop_duplicates("PersonID")
    allj = raw[raw["year"].between(1521, 1619)].dropna(subset=["X", "Y"])
    allj = allj.drop_duplicates("PersonID")
    for df in (old, new, allj):
        df["EntryYear"] = df["year"].astype(int)
    return old, new, allj


def build_panel(famine: pd.DataFrame, jinshi: pd.DataFrame) -> pd.DataFrame:
    z = famine.copy()
    j = jinshi.copy()
    if "year" not in j.columns:
        j["year"] = j["EntryYear"]
    j = j.drop_duplicates(subset=["year", "X", "Y"])
    for frame in (z, j):
        frame["grid_x"] = np.floor(frame["X"] / GRID) * GRID + GRID / 2
        frame["grid_y"] = np.floor(frame["Y"] / GRID) * GRID + GRID / 2

    z_agg = (
        z.groupby(["year", "grid_x", "grid_y"])
        .agg(
            zaihuang_level=("level", "max"),
            zaihuang_count=("level", "count"),
            zaihuang_severity=("level", "sum"),
        )
        .reset_index()
    )
    j_agg = (
        j.groupby(["year", "grid_x", "grid_y"])
        .agg(jinshi_count=("year", "count"))
        .reset_index()
    )
    years = range(int(min(z_agg.year.min(), j_agg.year.min())),
                  int(max(z_agg.year.max(), j_agg.year.max())) + 1)
    grids = sorted(set(zip(z_agg.grid_x, z_agg.grid_y)) | set(zip(j_agg.grid_x, j_agg.grid_y)))
    full = pd.DataFrame([(y, gx, gy) for y in years for gx, gy in grids],
                        columns=["year", "grid_x", "grid_y"])
    full = full.merge(z_agg, on=["year", "grid_x", "grid_y"], how="left")
    full = full.merge(j_agg, on=["year", "grid_x", "grid_y"], how="left")
    for col in ("zaihuang_level", "zaihuang_count", "zaihuang_severity", "jinshi_count"):
        full[col] = full[col].fillna(0)
    return full


# ------------------------------------------------------------------ models
def run_granger(panel: pd.DataFrame) -> pd.DataFrame:
    import sys

    sys.path.insert(0, str(ROOT))
    from src.analysis.grid_analysis import GridGrangerCausality, fdr_correction

    analyzer = GridGrangerCausality(max_lag=20, significance=0.05, min_obs=30)
    result = analyzer.analyze_grid_causality(panel)
    if len(result):
        sig, qvals = fdr_correction(result["gc_z_to_j_pval"].values, alpha=0.05)
        result["gc_z_to_j_qval"] = qvals
        result["gc_z_to_j_fdr_sig"] = sig
    return result


def run_gwr(panel: pd.DataFrame) -> pd.DataFrame:
    from mgwr.gwr import GWR
    from mgwr.sel_bw import Sel_BW

    cell = (
        panel.groupby(["grid_x", "grid_y"])
        .agg(
            zaihuang_severity=("zaihuang_severity", "mean"),
            jinshi_count=("jinshi_count", "mean"),
        )
        .reset_index()
    )
    cell = cell[(cell.zaihuang_severity > 0) & (cell.jinshi_count > 0)].copy()
    if len(cell) < 20:
        return cell.assign(gwr_coef=np.nan, gwr_tval=np.nan, gwr_local_r2=np.nan,
                           gwr_sig=False)

    coords = cell[["grid_x", "grid_y"]].values
    y = cell["jinshi_count"].values.reshape(-1, 1)
    X = cell[["zaihuang_severity"]].values
    X = (X - X.mean()) / (X.std() + 1e-10)
    y = (y - y.mean()) / (y.std() + 1e-10)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bw = Sel_BW(coords, y, X, kernel="gaussian", fixed=False)
        bw_value = bw.search(bw_min=2, bw_max=max(50, len(coords) // 2))
        model = GWR(coords, y, X, bw_value, kernel="gaussian", fixed=False)
        res = model.fit()

    cell["gwr_coef"] = res.params[:, 1]
    cell["gwr_tval"] = res.tvalues[:, 1]
    cell["gwr_local_r2"] = res.localR2
    cell["gwr_sig"] = np.abs(cell["gwr_tval"]) > 1.96
    cell.attrs["bandwidth"] = float(bw_value)
    cell.attrs["global_r2"] = float(res.R2)
    return cell


# ------------------------------------------------------------------- report
def summarize(name: str, granger: pd.DataFrame, gwr: pd.DataFrame, n_jinshi: int) -> dict:
    return {
        "panel": name,
        "jinshi_records": int(n_jinshi),
        "granger_tested": int(len(granger)),
        "granger_causal_z_to_j": int(granger["gc_z_to_j_causal"].sum()) if len(granger) else 0,
        "granger_fdr_sig": int(granger["gc_z_to_j_fdr_sig"].sum()) if len(granger) else 0,
        "granger_median_lag": float(granger.loc[granger["gc_z_to_j_fdr_sig"], "gc_z_to_j_lag"].median())
        if len(granger) and granger["gc_z_to_j_fdr_sig"].any() else float("nan"),
        "gwr_cells": int(len(gwr)),
        "gwr_sig": int(gwr["gwr_sig"].sum()) if len(gwr) else 0,
        "gwr_median_coef": float(gwr["gwr_coef"].median()) if len(gwr) else float("nan"),
        "gwr_positive": int((gwr["gwr_coef"] > 0).sum()) if len(gwr) else 0,
        "gwr_negative": int((gwr["gwr_coef"] < 0).sum()) if len(gwr) else 0,
    }


def main() -> None:
    for path in (RAW, FAMINE_MERGED, FAMINE_EXT, CITYS, JINSHI_ALL):
        if not path.exists():
            raise SystemExit(f"missing input: {path}")

    OUT.mkdir(parents=True, exist_ok=True)
    famine = load_famine()
    old_j, new_j, all_j = load_jinshi()
    print(f"famine events: {len(famine)}")
    print(f"old Arabic 1/2: {len(old_j)} | corrected elite: {len(new_j)} | all Jinshi: {len(all_j)}")

    base = pd.read_csv(JINSHI_ALL).rename(columns={"EntryYear": "year"})
    base = base[["year", "X", "Y"]]

    def with_year(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "year" not in out.columns:
            out["year"] = out["EntryYear"]
        return out[["year", "X", "Y"]]

    panels = {
        "v02": build_panel(famine, pd.concat([base, with_year(old_j)], ignore_index=True)),
        "v03": build_panel(famine, pd.concat([base, with_year(new_j)], ignore_index=True)),
    }

    results = {}
    for name, panel in panels.items():
        panel.to_csv(OUT / f"panel_{name}.csv.gz", index=False, compression="gzip")
        granger = run_granger(panel)
        gwr = run_gwr(panel)
        granger.to_excel(OUT / f"granger_{name}.xlsx", index=False, engine="openpyxl")
        gwr.to_excel(OUT / f"gwr_{name}.xlsx", index=False, engine="openpyxl")
        results[name] = summarize(name, granger, gwr, int(panel["jinshi_count"].sum()))
        results[name]["gwr_bandwidth"] = gwr.attrs.get("bandwidth", np.nan)
        results[name]["gwr_global_r2"] = gwr.attrs.get("global_r2", np.nan)
        print(name, results[name])

    # common-grid comparison
    g2 = pd.read_excel(OUT / "gwr_v02.xlsx")
    g3 = pd.read_excel(OUT / "gwr_v03.xlsx")
    common = g2.merge(g3, on=["grid_x", "grid_y"], suffixes=("_v02", "_v03"))
    comparison = {
        "common_gwr_cells": int(len(common)),
        "coef_pearson": float(common["gwr_coef_v02"].corr(common["gwr_coef_v03"])),
        "coef_median_abs_diff": float((common["gwr_coef_v03"] - common["gwr_coef_v02"]).abs().median()),
        "sig_overlap": int((common["gwr_sig_v02"] & common["gwr_sig_v03"]).sum()),
        "sig_v02_only": int((common["gwr_sig_v02"] & ~common["gwr_sig_v03"]).sum()),
        "sig_v03_only": int((~common["gwr_sig_v02"] & common["gwr_sig_v03"]).sum()),
    }
    results["comparison"] = comparison
    print("comparison", comparison)

    (OUT / "summary.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # markdown
    rows = [results["v02"], results["v03"]]
    lines = [
        "# Corrected Jinshi layer: effect on the grid models",
        "",
        "Generated by `scripts/corrected_robustness.py`.",
        "",
        "The 911-record layer is used by the point maps and the cluster-level",
        "analysis. The grid-level Granger/GWR models use a broader series",
        "(`ming_general` + an elite extension), so they are not simply the 911",
        "subset. This check re-estimates both models with the old extension",
        "(v0.2) and the normalized elite extension (v0.3).",
        "",
        "| Metric | v0.2 (old extension) | v0.3 (normalized) |",
        "|---|---:|---:|",
        f"| Jinshi records in panel | {rows[0]['jinshi_records']:,} | {rows[1]['jinshi_records']:,} |",
        f"| Granger grids tested | {rows[0]['granger_tested']} | {rows[1]['granger_tested']} |",
        f"| Granger z→j causal (p<0.05) | {rows[0]['granger_causal_z_to_j']} | {rows[1]['granger_causal_z_to_j']} |",
        f"| **Granger FDR-significant** | **{rows[0]['granger_fdr_sig']}** | **{rows[1]['granger_fdr_sig']}** |",
        f"| Median FDR lag (years) | {rows[0]['granger_median_lag']:.1f} | {rows[1]['granger_median_lag']:.1f} |",
        f"| GWR cells | {rows[0]['gwr_cells']} | {rows[1]['gwr_cells']} |",
        f"| GWR significant (|t|>1.96) | {rows[0]['gwr_sig']} | {rows[1]['gwr_sig']} |",
        f"| GWR median coefficient | {rows[0]['gwr_median_coef']:.3f} | {rows[1]['gwr_median_coef']:.3f} |",
        f"| GWR positive / negative | {rows[0]['gwr_positive']} / {rows[0]['gwr_negative']} | {rows[1]['gwr_positive']} / {rows[1]['gwr_negative']} |",
        "",
        "## Common-grid agreement",
        "",
        f"- Common GWR cells: {comparison['common_gwr_cells']}",
        f"- Coefficient Pearson r: {comparison['coef_pearson']:.4f}",
        f"- Median |Δ coefficient|: {comparison['coef_median_abs_diff']:.4f}",
        f"- Significant in both: {comparison['sig_overlap']}; v0.2 only: {comparison['sig_v02_only']}; "
        f"v0.3 only: {comparison['sig_v03_only']}",
        "",
        "## Reading",
        "",
        "- If the FDR/GWR counts and coefficient correlation stay close, the",
        "  grid-level conclusions are robust to the encoding fix; the defect is",
        "  confined to the descriptive 911 layer.",
        "- If they move materially, the headline grid results must be revised.",
        "",
        "Raw inputs stay outside the repository.",
    ]
    DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
