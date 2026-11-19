"""A12: independent full-Ming replication of the fixed 1-5 yr short-window test.

Pre-registration: docs/a12_full_ming_preregistration.md (frozen before run).
Reuses scripts/long_tail_analysis.py:fixed_lag_pvalue and the project's BH FDR.

Usage::

    python scripts/a12_full_ming_replication.py

Outputs::

    data/derived/a12_full_ming_panel.csv.gz
    data/derived/a12_full_ming_fixed_lag.csv
    data/derived/a12_full_ming_lag_window.csv
    docs/a12_full_ming_replication.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from long_tail_analysis import fixed_lag_pvalue  # noqa: E402

from src.analysis.grid_analysis import GridGrangerCausality, fdr_correction  # noqa: E402
from src.data_processing.jinshi_rank import rank_class  # noqa: E402

FAMINE = ROOT / "data" / "derived" / "a12_full_ming_famine.csv"
RAW = Path(os.environ.get("MING_JINSHI_RAW", r"data/private/明进士.xlsx"))
DERIVED = ROOT / "data" / "derived"
OUT_PANEL = DERIVED / "a12_full_ming_panel.csv.gz"
OUT_FIXED = DERIVED / "a12_full_ming_fixed_lag.csv"
OUT_LAG = DERIVED / "a12_full_ming_lag_window.csv"
DOC = ROOT / "docs" / "a12_full_ming_replication.md"

# FROZEN in docs/a12_full_ming_preregistration.md
LAGS = (1, 2, 3, 4, 5)
YEAR_MIN, YEAR_MAX = 1368, 1643
WINDOWS = {"full_1368_1643": (1368, 1643), "v03_window_1521_1619": (1521, 1619)}
V03_FIXED = 2
V03_GRIDS = 135


def build_panel() -> tuple[pd.DataFrame, int]:
    f = pd.read_csv(FAMINE)
    z = (f.groupby(["year", "grid_x", "grid_y"])["level"].sum()
         .rename("zaihuang_severity").reset_index())

    d = pd.read_excel(RAW)
    d["cls"] = d["EntryRank"].map(rank_class)
    y = pd.to_numeric(d["EntryYear"], errors="coerce")
    in_window = y.between(YEAR_MIN, YEAR_MAX)
    excluded = int((~in_window & y.notna()).sum())
    d = d[in_window & d["cls"].notna() & d["X"].notna() & d["Y"].notna()].copy()
    d["year"] = y[d.index].astype(int)
    d["grid_x"] = np.floor(d["X"]) + 0.5
    d["grid_y"] = np.floor(d["Y"]) + 0.5
    j = (d.groupby(["year", "grid_x", "grid_y"]).size()
         .rename("jinshi_count").reset_index())

    grids = pd.concat([z[["grid_x", "grid_y"]], j[["grid_x", "grid_y"]]]) \
        .drop_duplicates().sort_values(["grid_x", "grid_y"])
    years = np.arange(YEAR_MIN, YEAR_MAX + 1)
    full = grids.assign(_k=1).merge(pd.DataFrame({"year": years, "_k": 1}),
                                   on="_k").drop(columns="_k")
    full = full.merge(z, on=["year", "grid_x", "grid_y"], how="left")
    full = full.merge(j, on=["year", "grid_x", "grid_y"], how="left")
    full[["zaihuang_severity", "jinshi_count"]] = \
        full[["zaihuang_severity", "jinshi_count"]].fillna(0)
    full["zaihuang_level"] = full["zaihuang_severity"]
    full["zaihuang_count"] = (full["zaihuang_severity"] > 0).astype(int)
    full = full.sort_values(["grid_x", "grid_y", "year"]).reset_index(drop=True)
    return full, excluded


def fixed_window(sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (gx, gy), cell in sub.groupby(["grid_x", "grid_y"]):
        cell = cell.sort_values("year")
        z = cell["zaihuang_severity"].to_numpy(dtype=float)
        j = cell["jinshi_count"].to_numpy(dtype=float)
        if np.sum(z > 0) < 3 or np.sum(j > 0) < 3 or len(z) < 30:
            continue
        rows.append({"grid_x": gx, "grid_y": gy,
                     "pval": fixed_lag_pvalue(z, j, LAGS)})
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    sig, q = fdr_correction(out["pval"].to_numpy(), alpha=0.05)
    out["fdr_sig"] = sig
    out["qval"] = q
    return out


def lag_window(sub: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for max_lag in (5, 20):
        analyzer = GridGrangerCausality(max_lag=max_lag, significance=0.05,
                                        min_obs=30)
        r = analyzer.analyze_grid_causality(sub)
        sig, _ = fdr_correction(r["gc_z_to_j_pval"].to_numpy(), alpha=0.05)
        lags = r.loc[sig, "gc_z_to_j_lag"]
        rows.append({
            "max_lag": max_lag,
            "grids_tested": len(r),
            "fdr_sig": int(sig.sum()),
            "median_lag": float(lags.median()) if len(lags) else np.nan,
            "short_share": float((lags <= 5).mean()) if len(lags) else np.nan,
        })
    return pd.DataFrame(rows)


def verdict_of(k: int, n: int) -> str:
    if n == 0:
        return "NOT ESTIMABLE"
    if k == 0:
        return "NOT REPLICATED (zero result)"
    if k <= 0.10 * n:
        return "PARTIALLY REPLICATED (minority of grids)"
    return "INCONSISTENT (too many grids)"


def main() -> None:
    if not FAMINE.exists() or not RAW.exists():
        raise SystemExit("missing input")
    panel, excluded = build_panel()
    panel.to_csv(OUT_PANEL, index=False, compression="gzip")

    fixed_rows, lag_rows, summary = [], [], []
    for tag, (lo, hi) in WINDOWS.items():
        sub = panel[panel.year.between(lo, hi)].copy()
        fx = fixed_window(sub)
        fx["window"] = tag
        fixed_rows.append(fx)
        n, k = len(fx), int(fx["fdr_sig"].sum()) if len(fx) else 0
        verdict = verdict_of(k, n)
        summary.append({
            "window": tag, "years": f"{lo}-{hi}", "grids_tested": n,
            "fixed_1_5_fdr_sig": k, "pct": k / n * 100 if n else np.nan,
            "verdict": verdict,
        })
        lw = lag_window(sub)
        lw["window"] = tag
        lag_rows.append(lw)

    fixed = pd.concat(fixed_rows, ignore_index=True)
    lag = pd.concat(lag_rows, ignore_index=True)
    fixed.to_csv(OUT_FIXED, index=False)
    lag.to_csv(OUT_LAG, index=False)

    s = pd.DataFrame(summary)
    full_n = int(s.loc[s.window == "full_1368_1643", "grids_tested"].iloc[0])
    full_k = int(s.loc[s.window == "full_1368_1643", "fixed_1_5_fdr_sig"].iloc[0])
    primary = s.loc[s.window == "full_1368_1643", "verdict"].iloc[0]

    lines = [
        "# A12 — full-Ming independent replication (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a12_full_ming_replication.py`",
        "- Pre-registration: `docs/a12_full_ming_preregistration.md` "
        "(frozen before run).",
        "- Famine source: `灾荒数据.zip/table_level.json` (69,276 city-year "
        "rows, 1368–1643, 251 cities, 202 1° grids) — **independent** of the "
        "v0.3 `merged_data.csv`.",
        "- Jinshi source: full `明进士.xlsx`, 1368–1643, parsed ranks only.",
        f"- Records outside 1368–1643 excluded: **{excluded:,}**.",
        "- Method: identical `fixed_lag_pvalue(z, j, (1,2,3,4,5))` joint F "
        "test + BH FDR as `docs/long_tail_analysis.md` §2.",
        "",
        f"## Primary verdict (full 1368–1643): **{primary}**",
        "",
        "| Window | Years | grids tested | fixed 1–5 FDR grids | % | verdict |",
        "|---|---|---:|---:|---:|---|",
        *[f"| {r.window} | {r.years} | {r.grids_tested} | "
          f"{r.fixed_1_5_fdr_sig} | {r.pct:.1f}% | {r.verdict} |"
          for r in s.itertuples(index=False)],
        "",
        f"v0.3 reference (different source, 1506–1619 panel): **2/{V03_GRIDS}** "
        "grids in the same fixed 1–5 year joint test. Comparison is on "
        "existence and order of magnitude only; the number of estimable grids "
        "differs, so exact equality is not a pass criterion (pre-registration §5).",
        "",
        "## Lag-window diagnostic (same source)",
        "",
        "| Window | max_lag | grids tested | FDR grids | median lag | short-lag share |",
        "|---|---:|---:|---:|---:|---:|",
        *[f"| {r.window} | {r.max_lag} | {r.grids_tested} | {r.fdr_sig} | "
          f"{r.median_lag:.1f} | {r.short_share:.2f} |"
          for r in lag.itertuples(index=False)],
        "",
        "The 20-lag search is shown only to document search-window inflation "
        "on the independent source; it is not a headline.",
        "",
        "## Interpretation",
        "",
    ]
    if primary.startswith("PARTIALLY"):
        lines += [
            f"The fixed short-window signal reappears in **{full_k}/{full_n}** "
            "grids of the full-Ming independent panel — again a small minority. "
            "This supports the route-A framing: a *short-horizon predictive "
            "association in a minority of grids*, not a general causal effect.",
        ]
    elif primary.startswith("NOT REPLICATED"):
        lines += [
            "No grid survives the fixed 1–5 year joint test on the independent "
            "full-Ming panel. Per the pre-registration this is recorded as a "
            "**zero result with no respecification**. It weakens (but does not "
            "silently rewrite) the v0.3 short-window claim; a dated addendum "
            "must state the discrepancy.",
        ]
    else:
        lines += [
            f"The result is **{primary}**. Both the coefficient count and the "
            "v0.3 reference are reported; no tuning is performed to reconcile "
            "them.",
        ]
    lines += [
        "",
        "## When this would fail",
        "",
        "- `level` is a 0–5 grade, not the v0.3 severity sum; absolute effect "
        "sizes are not comparable.",
        "- Only 251 city points → 202 grids (v0.3 had 291); coverage is lower.",
        "- Early-Ming (1368–1520) record density is lower; the 1521–1619 "
        "secondary window is the cleaner like-for-like check.",
        "- Stray `EntryYear` up to 1871 were excluded explicitly; a different "
        "filter changes the panel.",
        "- Any post-hoc change to lags, FDR alpha, grid size or window is "
        "forbidden by the pre-registration.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| rectangular panel | `<local private panel; not distributed>` |",
        "| fixed-lag grid results | `data/derived/a12_full_ming_fixed_lag.csv` |",
        "| lag-window diagnostics | `data/derived/a12_full_ming_lag_window.csv` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(s.to_string(index=False))
    print(lag.to_string(index=False))
    print(f"primary: {primary} ({full_k}/{full_n})")
    print(f"wrote {OUT_PANEL}, {OUT_FIXED}, {OUT_LAG}, {DOC}")


if __name__ == "__main__":
    main()
