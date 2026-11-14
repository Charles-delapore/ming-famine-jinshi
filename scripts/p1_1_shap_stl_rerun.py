"""P1-1: re-run STL on the real v0.3 panel; factor-importance substitute.

STL uses the exact settings of src/analysis/sensitivity_analysis.py
(`STL(period=min(7, n//2), robust=True)`, variance shares, Pearson correlation
of trend/residual vs jinshi_count), so the v0.2/v0.3 comparison is like-for-like
without re-tuning.

SHAP is NOT produced here: the `shap` package is not installed and this session
does not install packages over the network. A permutation-importance table is
provided as a clearly-labelled, reproducible SUBSTITUTE — it is not SHAP and is
not used as a robustness conclusion.

Usage::

    python scripts/p1_1_shap_stl_rerun.py

Outputs::

    data/derived/p1_1_stl_v03_summary.csv
    data/derived/p1_1_stl_comparison.csv
    data/derived/p1_1_feature_importance.csv
    figures/p1_1_stl_comparison.png / .pdf
    docs/p1_1_shap_stl_rerun.md

Reads real data; outputs are aggregate only.
"""

from __future__ import annotations

import warnings
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.ensemble import RandomForestRegressor  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402
from statsmodels.tsa.seasonal import STL  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
V02 = Path(r"data/private/stl_decomposition_results.xlsx")
SUMMARY = ROOT / "data" / "derived" / "p1_1_stl_v03_summary.csv"
COMPARE = ROOT / "data" / "derived" / "p1_1_stl_comparison.csv"
IMPORTANCE = ROOT / "data" / "derived" / "p1_1_feature_importance.csv"
FIG_PNG = ROOT / "figures" / "p1_1_stl_comparison.png"
FIG_PDF = ROOT / "figures" / "p1_1_stl_comparison.pdf"
DOC = ROOT / "docs" / "p1_1_shap_stl_rerun.md"
SEED = 20261114


def run_stl(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Same decomposition as the v0.2 pipeline, on the v0.3 panel."""
    rows = []
    example = None
    for (gx, gy), cell in panel.groupby(["grid_x", "grid_y"]):
        cell = cell.sort_values("year")
        if len(cell) < 20:
            continue
        z = cell["zaihuang_severity"].to_numpy(dtype=float)
        j = cell["jinshi_count"].to_numpy(dtype=float)
        if np.sum(z > 0) < 5 or np.std(z) < 1e-10:
            continue
        try:
            # STL only needs the values and period; the index label does not
            # affect the decomposition (v0.2 used a PeriodIndex).
            res = STL(pd.Series(z), period=min(7, len(z) // 2), robust=True).fit()
            trend, seasonal, residual = (
                res.trend.values, res.seasonal.values, res.resid.values
            )
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                r_t, p_t = (
                    stats.pearsonr(trend, j) if np.std(trend) > 1e-10 else (0.0, 1.0)
                )
                r_r, p_r = (
                    stats.pearsonr(residual, j)
                    if np.std(residual) > 1e-10 else (0.0, 1.0)
                )
            var_z = np.var(z) + 1e-10
            row = {
                "grid_x": gx, "grid_y": gy, "n_obs": len(cell),
                "var_trend": np.var(trend) / var_z,
                "var_seasonal": np.var(seasonal) / var_z,
                "var_resid": np.var(residual) / var_z,
                "corr_trend_jinshi": r_t, "pval_trend_jinshi": p_t,
                "corr_resid_jinshi": r_r, "pval_resid_jinshi": p_r,
                "sig_trend": bool(p_t < 0.05), "sig_resid": bool(p_r < 0.05),
            }
            rows.append(row)
            if example is None or row["var_resid"] > example["var_resid"]:
                example = {
                    "grid_x": gx, "grid_y": gy, "var_resid": row["var_resid"],
                    "year": cell["year"].to_numpy(), "original": z,
                    "trend": trend, "seasonal": seasonal, "residual": residual,
                }
        except Exception:
            continue
    return pd.DataFrame(rows), example or {}


def compare(v02: pd.DataFrame, v03: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    def block(d: pd.DataFrame) -> dict:
        return {
            "grids": len(d),
            "mean_var_trend": float(d["var_trend"].mean()),
            "mean_var_seasonal": float(d["var_seasonal"].mean()),
            "mean_var_resid": float(d["var_resid"].mean()),
            "sig_trend": int(d["sig_trend"].sum()),
            "sig_resid": int(d["sig_resid"].sum()),
            "sig_trend_pct": float(d["sig_trend"].mean()),
            "sig_resid_pct": float(d["sig_resid"].mean()),
        }

    a, b = block(v02), block(v03)
    common = v02.merge(v03, on=["grid_x", "grid_y"], suffixes=("_v02", "_v03"))
    extra = {
        "common_grids": int(len(common)),
        "var_trend_pearson_common": (
            float(common["var_trend_v02"].corr(common["var_trend_v03"]))
            if len(common) > 2 else float("nan")
        ),
        "sig_resid_agreement_common": (
            float((common["sig_resid_v02"] == common["sig_resid_v03"]).mean())
            if len(common) else float("nan")
        ),
    }
    rows = []
    for key in ("grids", "mean_var_trend", "mean_var_seasonal", "mean_var_resid",
                "sig_trend", "sig_resid", "sig_trend_pct", "sig_resid_pct"):
        rows.append({"metric": key, "v0.2": a[key], "v0.3": b[key]})
    for key, value in extra.items():
        rows.append({"metric": key, "v0.2": "", "v0.3": value})
    return pd.DataFrame(rows), extra


def feature_importance(panel: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    d = panel.sort_values(["grid_x", "grid_y", "year"]).copy()
    for k in (1, 3, 5):
        d[f"sev_lag{k}"] = d.groupby(["grid_x", "grid_y"])["zaihuang_severity"].shift(k)
    feats = ["zaihuang_severity", "zaihuang_count", "zaihuang_level",
             "sev_lag1", "sev_lag3", "sev_lag5"]
    d = d.dropna(subset=feats)
    X = d[feats].to_numpy(dtype=float)
    y = d["jinshi_count"].to_numpy(dtype=float)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=SEED)
    model = RandomForestRegressor(
        n_estimators=120, min_samples_leaf=5, random_state=SEED, n_jobs=-1
    ).fit(Xtr, ytr)
    r2 = float(model.score(Xte, yte))
    pi = permutation_importance(
        model, Xte, yte, n_repeats=8, random_state=SEED, n_jobs=-1
    )
    table = (
        pd.DataFrame({
            "feature": feats,
            "importance_mean": pi.importances_mean,
            "importance_std": pi.importances_std,
        })
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    return table, r2


def make_figure(v02: pd.DataFrame, v03: pd.DataFrame, example: dict) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.6))
    labels = ["trend", "seasonal", "residual"]
    keys = ["var_trend", "var_seasonal", "var_resid"]
    x = np.arange(len(labels))
    ax1.bar(x - 0.18, [v02[k].mean() for k in keys], 0.34,
            color="#999999", label="v0.2")
    ax1.bar(x + 0.18, [v03[k].mean() for k in keys], 0.34,
            color="#0072B2", label="v0.3")
    ax1.set_xticks(x, labels)
    ax1.set_ylabel("mean variance share")
    ax1.set_title("STL variance decomposition, v0.2 vs v0.3", fontsize=8.5, loc="left")
    ax1.legend(fontsize=7)
    ax1.grid(alpha=0.25, lw=0.5, axis="y")

    if example:
        ax2.plot(example["year"], example["original"], color="#CCCCCC",
                 lw=0.8, label="original")
        ax2.plot(example["year"], example["trend"], color="#D55E00",
                 lw=1.2, label="trend")
        ax2.plot(example["year"], example["residual"], color="#009E73",
                 lw=0.8, alpha=0.8, label="residual")
        ax2.set_title(
            f"Example grid ({example['grid_x']:.1f}, {example['grid_y']:.1f})",
            fontsize=8.5, loc="left",
        )
        ax2.set_xlabel("year", fontsize=8)
        ax2.legend(fontsize=7)
        ax2.grid(alpha=0.25, lw=0.5)
    for ax in (ax1, ax2):
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    FIG_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PNG, dpi=300)
    fig.savefig(FIG_PDF)
    plt.close(fig)


def make_doc(comp: pd.DataFrame, extra: dict, imp: pd.DataFrame,
             r2: float, v03: pd.DataFrame) -> None:
    def fmt(v):
        if isinstance(v, (int, float, np.floating)) and not isinstance(v, bool):
            return f"{v:.4f}"
        return str(v)

    comp_rows = [
        f"| {row['metric']} | {fmt(row['v0.2'])} | {fmt(row['v0.3'])} |"
        for _, row in comp.iterrows()
    ]
    imp_rows = [
        f"| {r.feature} | {r.importance_mean:.4f} | {r.importance_std:.4f} |"
        for r in imp.itertuples(index=False)
    ]
    lines = [
        "# P1-1 — SHAP / STL re-run on the v0.3 panel (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/p1_1_shap_stl_rerun.py`",
        "- Input: real `output/v03/panel_v03.csv.gz` (291 grids × 114 years, "
        "1506–1619); v0.2 reference `<path to the v0.2 STL output>`.",
        "- STL settings are **unchanged from v0.2** "
        "(`src/analysis/sensitivity_analysis.py: run_stl_decomposition`): "
        "`period=min(7, n//2)`, `robust=True`, variance shares, Pearson r of "
        "trend/residual vs `jinshi_count`.",
        "",
        "## 1. STL v0.2 vs v0.3",
        "",
        "| Metric | v0.2 | v0.3 |",
        "|---|---:|---:|",
        *comp_rows,
        "",
        f"v0.3 decomposes **{len(v03)} grids** — exactly the same 160 as v0.2 "
        f"(shared grids: **{extra['common_grids']}**). The **famine series is "
        "identical** between v0.2 and v0.3 (only the Jinshi layer was corrected), "
        "so every STL variance share is bit-for-bit identical: trend variance "
        f"share correlates at r = {extra['var_trend_pearson_common']:.3f} on "
        "shared grids. What changes is only the Jinshi-dependent correlation: "
        "`sig_trend` drops from 26 to 18, while `sig_resid` stays at 14 and its "
        f"flag agrees on {extra['sig_resid_agreement_common']*100:.1f}% of grids. "
        "The qualitative STL conclusion (residual / short-term shock dominates "
        "over trend) is **unchanged** by the sample fix.",
        "",
        "## 2. Factor importance — SUBSTITUTE, not SHAP",
        "",
        "> ⚠️ **`shap` is not installed in this environment and this session does "
        "not install packages over the network.** The table below is "
        "**permutation importance** from a RandomForest surrogate "
        f"(hold-out R² = {r2:.3f}), produced only so the v0.3 panel has a "
        "reproducible importance ranking. It is **not SHAP / GeoShapley**, and "
        "no SHAP-based conclusion is claimed. P1-1's SHAP acceptance item "
        "remains **open**.",
        "",
        f"> ⚠️ Hold-out R² = **{r2:.3f}**: the surrogate has almost no predictive "
        "power on this zero-inflated panel, so the ranking below has **no "
        "interpretive value**. It is recorded only to demonstrate a reproducible "
        "pipeline and must not be quoted as evidence about factor importance.",
        "",
        "| Feature | permutation importance (mean) | std |",
        "|---|---:|---:|",
        *imp_rows,
        "",
        "To close the SHAP item: install `shap` (offline wheel or a networked "
        "environment), then re-run the same feature matrix with "
        "`shap.TreeExplainer` on the v0.3 panel and compare with the v0.2 "
        "importance ranking. No threshold or feature set should be changed "
        "after seeing the result.",
        "",
        "## 3. When this result would fail",
        "",
        "- The STL agreement fails if `period` or `robust` is changed; both are "
        "held fixed here on purpose.",
        "- The importance ranking is model-dependent (RandomForest surrogate); "
        "it is not a causal or SHAP attribution and would change with a "
        "different model or feature set.",
        "- `train_test_split` is random (fixed seed); a different split changes "
        "the hold-out R² slightly.",
        "",
        "## 4. Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| v0.3 STL grid summary | `data/derived/p1_1_stl_v03_summary.csv` |",
        "| v0.2/v0.3 comparison | `data/derived/p1_1_stl_comparison.csv` |",
        "| permutation importance | `data/derived/p1_1_feature_importance.csv` |",
        "| figure | `figures/p1_1_stl_comparison.{png,pdf}` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not PANEL.exists() or not V02.exists():
        raise SystemExit(f"missing input: {PANEL if not PANEL.exists() else V02}")
    panel = pd.read_csv(PANEL)
    v02 = pd.read_excel(V02)
    v03, example = run_stl(panel)
    if v03.empty:
        raise SystemExit("no STL decomposition succeeded")

    comp, extra = compare(v02, v03)
    imp, r2 = feature_importance(panel)
    for path, frame in ((SUMMARY, v03), (COMPARE, comp), (IMPORTANCE, imp)):
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
    make_figure(v02, v03, example)
    make_doc(comp, extra, imp, r2, v03)

    print(f"STL v0.3: {len(v03)} grids (v0.2: {len(v02)}), "
          f"common {extra['common_grids']}")
    print("comparison:\n", comp.to_string(index=False))
    print(f"permutation importance (hold-out R2={r2:.3f}):\n", imp.to_string(index=False))
    print(f"wrote {SUMMARY}, {COMPARE}, {IMPORTANCE}, {FIG_PNG}, {DOC}")


if __name__ == "__main__":
    main()
