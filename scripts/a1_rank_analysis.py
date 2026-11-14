"""A1 (work package): rank-share model, executed exactly as pre-registered.

Pre-registration: docs/a1_rank_preregistration.md (frozen before this run).
Question: does famine exposure change the 1甲/2甲 *share* of Jinshi, not just
the count?

Usage::

    python scripts/a1_rank_analysis.py

Outputs::

    data/derived/a1_rank_coefficients.csv
    data/derived/a1_rank_units.csv
    figures/a1_rank_share.png / .pdf
    docs/a1_rank_results.md

Reads the private CBDB export and the real v0.3 panel; outputs are aggregate only.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import statsmodels.formula.api as smf  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_processing.jinshi_rank import rank_class  # noqa: E402

RAW = Path(os.environ.get("MING_JINSHI_RAW", r"data/private/明进士.xlsx"))
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
OUT_COEF = ROOT / "data" / "derived" / "a1_rank_coefficients.csv"
OUT_UNITS = ROOT / "data" / "derived" / "a1_rank_units.csv"
FIG_PNG = ROOT / "figures" / "a1_rank_share.png"
FIG_PDF = ROOT / "figures" / "a1_rank_share.pdf"
DOC = ROOT / "docs" / "a1_rank_results.md"

# FROZEN in docs/a1_rank_preregistration.md
SEED = 20261114
MIN_DENOM = 3
MIN_UNITS_PER_GRID = 5
N_PERM = 200
FORMULA = "share_top ~ famine_1_5 + log_total + C(grid_id) + C(exam_year)"


def build_units() -> pd.DataFrame:
    d = pd.read_excel(RAW)
    d["cls"] = d["EntryRank"].map(rank_class)
    d["year"] = pd.to_numeric(d["EntryYear"], errors="coerce")
    d = d[d["year"].between(1521, 1619) & d["X"].notna() & d["Y"].notna()].copy()
    d["grid_x"] = np.floor(d["X"]) + 0.5
    d["grid_y"] = np.floor(d["Y"]) + 0.5
    d = d[d["cls"].isin([1, 2, 3])].copy()  # unparsed excluded from both parts
    d["top"] = d["cls"].isin([1, 2]).astype(int)
    u = (
        d.groupby(["grid_x", "grid_y", "year"])
        .agg(total=("top", "size"), top=("top", "sum"))
        .reset_index()
    )
    u["share_top"] = u["top"] / u["total"]
    u = u[u["total"] >= MIN_DENOM].copy()
    per_grid = u.groupby(["grid_x", "grid_y"])["year"].transform("size")
    u = u[per_grid >= MIN_UNITS_PER_GRID].copy()
    u["grid_id"] = u["grid_x"].astype(str) + "_" + u["grid_y"].astype(str)
    u["exam_year"] = u["year"].astype(int)
    u["log_total"] = np.log(u["total"])
    return u


def build_exposure() -> pd.DataFrame:
    p = pd.read_csv(PANEL).sort_values(["grid_x", "grid_y", "year"])
    for k in range(1, 6):
        p[f"l{k}"] = p.groupby(["grid_x", "grid_y"])["zaihuang_severity"].shift(k)
    p["famine_1_5"] = p[[f"l{k}" for k in range(1, 6)]].mean(axis=1)
    return p[["grid_x", "grid_y", "year", "famine_1_5"]]


def main() -> None:
    if not RAW.exists() or not PANEL.exists():
        raise SystemExit("missing input")
    units = build_units()
    df = units.merge(build_exposure(), on=["grid_x", "grid_y", "year"], how="inner")
    df = df.dropna(subset=["famine_1_5"]).reset_index(drop=True)
    OUT_UNITS.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_UNITS, index=False)

    model = smf.wls(FORMULA, data=df, weights=df["total"]).fit(
        cov_type="cluster", cov_kwds={"groups": df["grid_id"]}
    )
    coef = float(model.params["famine_1_5"])
    se = float(model.bse["famine_1_5"])
    lo, hi = (float(v) for v in model.conf_int().loc["famine_1_5"])
    beta_std = coef * df["famine_1_5"].std() / df["share_top"].std()
    p_value = float(model.pvalues["famine_1_5"])

    # Pre-specified descriptive permutation (coefficient only, same spec).
    rng = np.random.default_rng(SEED)
    groups = df.groupby("grid_id")["famine_1_5"]
    perm = []
    for _ in range(N_PERM):
        shuffled = df.copy()
        shuffled["famine_1_5"] = groups.transform(
            lambda v: rng.permutation(v.to_numpy())
        )
        try:
            perm.append(float(smf.wls(FORMULA, data=shuffled,
                                      weights=shuffled["total"]).fit()
                              .params["famine_1_5"]))
        except Exception:
            continue
    perm = np.array(perm)
    p_perm = float((np.abs(perm) >= abs(coef)).mean()) if len(perm) else float("nan")

    null = (lo <= 0 <= hi) and abs(beta_std) < 0.05
    verdict = "NULL (zero result; stop expansion)" if null else "NON-NULL"

    coef_table = pd.DataFrame([{
        "term": "famine_1_5", "coef": coef, "std_err": se,
        "ci_low": lo, "ci_high": hi, "p_value": p_value,
        "standardized_beta": beta_std, "n_units": len(df),
        "n_grids": df["grid_id"].nunique(), "n_exam_years": df["exam_year"].nunique(),
        "r_squared": float(model.rsquared),
        "permutation_reps": len(perm), "permutation_p": p_perm,
        "verdict": verdict,
    }])
    coef_table.to_csv(OUT_COEF, index=False)

    # Figure: binned share_top vs exposure + fitted line.
    df["_bin"] = pd.qcut(df["famine_1_5"], 5, duplicates="drop")
    binned = df.groupby("_bin", observed=True).apply(
        lambda g: pd.Series({
            "x": g["famine_1_5"].mean(),
            "y": np.average(g["share_top"], weights=g["total"]),
            "n": len(g),
        }), include_groups=False
    )
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(binned["x"], binned["y"], "o-", color="#0072B2", lw=1.4,
            label="weighted mean by exposure quintile")
    xs = np.linspace(df["famine_1_5"].min(), df["famine_1_5"].max(), 50)
    ax.plot(xs, df["share_top"].mean() + coef * (xs - df["famine_1_5"].mean()),
            "--", color="#D55E00", lw=1.2, label=f"WLS slope ({coef:+.4f})")
    ax.axhline(df["share_top"].mean(), color="#999999", lw=0.8, alpha=0.7)
    ax.set_xlabel("mean famine severity, years t−1…t−5", fontsize=8)
    ax.set_ylabel("share of rank-1/2 Jinshi", fontsize=8)
    ax.set_title("A1: famine exposure vs rank composition", fontsize=9, loc="left")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.25, lw=0.5)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    FIG_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_PNG, dpi=300)
    fig.savefig(FIG_PDF)
    plt.close(fig)

    lines = [
        "# A1 — rank-share results (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a1_rank_analysis.py`",
        "- Pre-registration: `docs/a1_rank_preregistration.md` (frozen before run).",
        "- Input: CBDB `明进士.xlsx` (28,761 rows) + real `output/v03/panel_v03.csv.gz`.",
        "- Model: WLS `share_top ~ famine_1_5 + log(total) + C(grid) + C(exam_year)`, "
        "weights = denominator, SE clustered by grid.",
        "",
        f"**Verdict: {verdict}**",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| coefficient on famine_1_5 | {coef:+.6f} |",
        f"| cluster SE | {se:.6f} |",
        f"| 95% CI | [{lo:+.6f}, {hi:+.6f}] |",
        f"| standardized beta | {beta_std:+.4f} |",
        f"| p (cluster) | {p_value:.4f} |",
        f"| permutation p ({len(perm)} reps) | {p_perm:.4f} |",
        f"| units / grids / exam years | {len(df)} / {df['grid_id'].nunique()} / {df['exam_year'].nunique()} |",
        f"| R² | {model.rsquared:.4f} |",
        "",
        "## Interpretation (pre-registered rule)",
        "",
        f"- Null criterion: 95% CI includes 0 **and** |standardized beta| < 0.05 "
        f"→ {'met' if null else 'not met'}.",
    ]
    if null:
        lines += [
            "",
            "**Zero result.** Famine exposure in the preceding 1–5 years does not "
            "shift the 1甲/2甲 share of Jinshi in this specification. Per the "
            "pre-registration this is recorded as-is and **no expansion is "
            "undertaken**: no alternative windows, denominators, controls or "
            "subgroups.",
        ]
    else:
        lines += [
            "",
            "The coefficient does not meet the pre-registered null criterion; the "
            "direction and magnitude are reported above without post-hoc "
            "interpretation. No model respecification is performed.",
        ]
    lines += [
        "",
        "## When this result would fail",
        "",
        "- If the rank normalizer changes (unparsed ranks are currently excluded "
        "from both numerator and denominator).",
        "- If the 1–5 year exposure window or the ≥3 denominator / ≥5-units-per-grid "
        "restrictions are changed; all are frozen in the pre-registration.",
        "- If grid/exam-year fixed effects are dropped, the coefficient is not "
        "comparable.",
        "- Rank composition is measured on CBDB records with a parsed rank only; "
        "selection into parsed ranks is not modelled.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| coefficient table | `data/derived/a1_rank_coefficients.csv` |",
        "| unit-level data | `data/derived/a1_rank_units.csv` |",
        "| figure | `figures/a1_rank_share.{png,pdf}` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(coef_table.to_string(index=False))
    print(f"verdict: {verdict}, permutation p = {p_perm:.4f}")
    print(f"wrote {OUT_COEF}, {OUT_UNITS}, {FIG_PNG}, {DOC}")


if __name__ == "__main__":
    main()
