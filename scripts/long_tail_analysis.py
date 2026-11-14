"""Long-tail diagnostics for the Ming famine -> Jinshi Granger result (local).

Three questions:

1. Does the FDR discovery count depend on how many lags the max-F search is
   allowed to try? (selection-window sensitivity)
2. Does a fixed, pre-specified short lag window (1-5 years) still find grids?
   (no lag selection; closest to the Qing-China drought design)
3. Are long-lag grids (>=15 yr) ecologically distinct from short-lag grids?

Outputs:
    data/derived/long_tail_lag_window.csv
    data/derived/long_tail_fixed_lag.csv
    data/derived/long_tail_grid_groups.csv
    figures/long_tail_diagnostics.png / .pdf
    docs/long_tail_analysis.md   (numbers appended by hand afterwards)

Reads the private panel; outputs are aggregate only.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.analysis.grid_analysis import GridGrangerCausality, fdr_correction  # noqa: E402

PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
GRANGER = ROOT / "output" / "v03" / "granger_v03.xlsx"
OUT_LAG = ROOT / "data" / "derived" / "long_tail_lag_window.csv"
OUT_FIXED = ROOT / "data" / "derived" / "long_tail_fixed_lag.csv"
OUT_GROUPS = ROOT / "data" / "derived" / "long_tail_grid_groups.csv"


def fixed_lag_pvalue(x: np.ndarray, y: np.ndarray, lags: tuple[int, ...]) -> float:
    """Joint Granger F-test with a fixed lag set (restricted y-only vs +x)."""
    m = max(lags)
    n = len(y)
    if n < m + 10:
        return 1.0
    y_t = y[m:]
    X_r = np.column_stack([y[m - l:n - l] for l in lags])
    X_u = np.column_stack([X_r] + [x[m - l:n - l] for l in lags])
    n_obs = len(y_t)
    k = X_u.shape[1]

    def ssr(X):
        beta, *_ = np.linalg.lstsq(np.column_stack([np.ones(n_obs), X]), y_t, rcond=None)
        resid = y_t - np.column_stack([np.ones(n_obs), X]) @ beta
        return float(resid @ resid)

    ssr_r, ssr_u = ssr(X_r), ssr(X_u)
    if ssr_u <= 1e-12 or ssr_r <= ssr_u:
        return 1.0
    q = len(lags)
    f = ((ssr_r - ssr_u) / q) / (ssr_u / (n_obs - k - 1))
    if not np.isfinite(f):
        return 1.0
    return float(1 - stats.f.cdf(f, q, n_obs - k - 1))


def fixed_lag_panel(panel: pd.DataFrame, lags: tuple[int, ...]) -> pd.DataFrame:
    rows = []
    for (gx, gy), cell in panel.groupby(["grid_x", "grid_y"]):
        cell = cell.sort_values("year")
        z = cell["zaihuang_severity"].values.astype(float)
        j = cell["jinshi_count"].values.astype(float)
        if np.sum(z > 0) < 3 or np.sum(j > 0) < 3 or len(z) < 30:
            continue
        p = fixed_lag_pvalue(z, j, lags)
        rows.append({"grid_x": gx, "grid_y": gy, "pval": p})
    out = pd.DataFrame(rows)
    sig, q = fdr_correction(out["pval"].values, alpha=0.05)
    out["fdr_sig"] = sig
    out["qval"] = q
    return out


def lag_window_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for max_lag in (5, 10, 15, 20):
        analyzer = GridGrangerCausality(max_lag=max_lag, significance=0.05, min_obs=30)
        r = analyzer.analyze_grid_causality(panel)
        sig, _ = fdr_correction(r["gc_z_to_j_pval"].values, alpha=0.05)
        r["sig"] = sig
        # within-grid Bonferroni over the lag candidates actually tried
        p_adj = np.minimum(1.0, r["gc_z_to_j_pval"].values * max_lag)
        sig_b, _ = fdr_correction(p_adj, alpha=0.05)
        lags = r.loc[sig, "gc_z_to_j_lag"]
        rows.append({
            "max_lag": max_lag,
            "grids_tested": len(r),
            "fdr_sig": int(sig.sum()),
            "fdr_sig_bonferroni": int(sig_b.sum()),
            "median_lag": float(lags.median()) if len(lags) else np.nan,
            "short_share": float((lags <= 5).mean()) if len(lags) else np.nan,
            "long15_n": int((lags >= 15).sum()),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT_LAG, index=False)
    return df


def grid_groups(granger: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    agg = panel.groupby(["grid_x", "grid_y"]).agg(
        severity=("zaihuang_severity", "sum"),
        famine_records=("zaihuang_count", "sum"),
        jinshi_records=("jinshi_count", "sum"),
        famine_years=("zaihuang_count", lambda s: int((s > 0).sum())),
        n_years=("year", "size"),
    ).reset_index()
    m = granger.merge(agg, on=["grid_x", "grid_y"], how="left")
    sig = m[m["gc_z_to_j_fdr_sig"].astype(bool)].copy()
    sig["group"] = np.where(sig["gc_z_to_j_lag"] <= 5, "short(<=5)",
                            np.where(sig["gc_z_to_j_lag"] >= 15, "long(>=15)", "mid"))
    sig.to_csv(OUT_GROUPS, index=False)
    return sig


def main() -> None:
    panel = pd.read_csv(PANEL)
    granger = pd.read_excel(GRANGER)

    window = lag_window_sensitivity(panel)
    print(window.to_string(index=False))

    fixed_rows = []
    for lags in ((1, 2, 3, 4, 5), (1, 2, 3), (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)):
        r = fixed_lag_panel(panel, lags)
        fixed_rows.append({
            "lag_set": f"{lags[0]}-{lags[-1]}",
            "grids": len(r),
            "fdr_sig": int(r["fdr_sig"].sum()),
            "min_p": float(r["pval"].min()),
            "median_p_sig": float(r.loc[r["fdr_sig"], "pval"].median())
            if r["fdr_sig"].any() else np.nan,
        })
    fixed = pd.DataFrame(fixed_rows)
    fixed.to_csv(OUT_FIXED, index=False)
    print(fixed.to_string(index=False))

    groups = grid_groups(granger, panel)
    summary = (
        groups.groupby("group")
        .agg(n=("gc_z_to_j_lag", "size"),
             lag=("gc_z_to_j_lag", "median"),
             severity=("severity", "median"),
             famine_records=("famine_records", "median"),
             jinshi_records=("jinshi_records", "median"),
             famine_years=("famine_years", "median"),
             x=("grid_x", "median"), y=("grid_y", "median"))
        .round(1)
    )
    print(summary.to_string())

    s = groups[groups.group == "short(<=5)"]
    l = groups[groups.group == "long(>=15)"]
    for col in ("severity", "famine_records", "jinshi_records", "famine_years", "grid_x", "grid_y"):
        u = stats.mannwhitneyu(s[col], l[col])
        print(f"{col}: short {s[col].median():.1f} vs long {l[col].median():.1f}, p={u.pvalue:.3f}")


if __name__ == "__main__":
    main()
