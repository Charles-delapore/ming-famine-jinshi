"""A2 (work package): spatial spillover, executed exactly as pre-registered.

Pre-registration: docs/a2_spillover_preregistration.md (frozen before this run).
Question: does neighbouring-grid famine predict local Jinshi output beyond local
famine?

Usage::

    python scripts/a2_spillover_analysis.py

Outputs::

    data/derived/a2_spillover_coefficients.csv
    data/derived/a2_spillover_units.csv
    docs/a2_spillover_results.md

Reads the private CBDB export and the real v0.3 panel; outputs are aggregate only.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_processing.jinshi_rank import rank_class  # noqa: E402

RAW = Path(os.environ.get("MING_JINSHI_RAW", r"data/private/明进士.xlsx"))
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
OUT_COEF = ROOT / "data" / "derived" / "a2_spillover_coefficients.csv"
OUT_UNITS = ROOT / "data" / "derived" / "a2_spillover_units.csv"
DOC = ROOT / "docs" / "a2_spillover_results.md"

# FROZEN in docs/a2_spillover_preregistration.md
QUEEN = [(dx, dy) for dx in (-1.0, 0.0, 1.0) for dy in (-1.0, 0.0, 1.0)
         if not (dx == 0 and dy == 0)]
FORMULA = "jinshi_count ~ direct + spillover + C(exam_year) + C(grid_id)"
MIN_NEIGHBOUR_COVERAGE = 0.60


def build_units() -> pd.DataFrame:
    d = pd.read_excel(RAW)
    d["cls"] = d["EntryRank"].map(rank_class)
    d["year"] = pd.to_numeric(d["EntryYear"], errors="coerce")
    d = d[d["year"].between(1521, 1619) & d["X"].notna() & d["Y"].notna()
          & d["cls"].notna()].copy()
    d["grid_x"] = np.floor(d["X"]) + 0.5
    d["grid_y"] = np.floor(d["Y"]) + 0.5
    counts = (
        d.groupby(["grid_x", "grid_y", "year"]).size()
        .rename("jinshi_count").reset_index()
    )
    grids = counts[["grid_x", "grid_y"]].drop_duplicates()
    years = sorted(int(y) for y in counts["year"].unique())
    rows = [(gx, gy, y) for gx, gy in grids.itertuples(index=False, name=None)
            for y in years]
    full = pd.DataFrame(rows, columns=["grid_x", "grid_y", "year"])
    full = full.merge(counts, on=["grid_x", "grid_y", "year"], how="left")
    full["jinshi_count"] = full["jinshi_count"].fillna(0).astype(int)
    full["grid_id"] = (full["grid_x"].astype(str) + "_" +
                       full["grid_y"].astype(str))
    full["exam_year"] = full["year"].astype(int)
    return full


def build_exposure() -> pd.DataFrame:
    p = pd.read_csv(PANEL).sort_values(["grid_x", "grid_y", "year"])
    for k in range(1, 6):
        p[f"l{k}"] = p.groupby(["grid_x", "grid_y"])["zaihuang_severity"].shift(k)
    p["direct"] = p[[f"l{k}" for k in range(1, 6)]].mean(axis=1)
    e = p[["grid_x", "grid_y", "year", "direct"]].dropna().copy()
    lookup = e.set_index(["grid_x", "grid_y", "year"])["direct"].to_dict()
    spill, has = [], []
    for row in e.itertuples(index=False):
        vals = [lookup.get((row.grid_x + dx, row.grid_y + dy, row.year), np.nan)
                for dx, dy in QUEEN]
        vals = [v for v in vals if np.isfinite(v)]
        spill.append(float(np.mean(vals)) if vals else 0.0)
        has.append(bool(vals))
    e["spillover"] = spill
    e["has_neighbour"] = has
    return e[["grid_x", "grid_y", "year", "direct", "spillover",
              "has_neighbour"]]


def main() -> None:
    if not RAW.exists() or not PANEL.exists():
        raise SystemExit("missing input")
    units = build_units()
    df = units.merge(build_exposure(), on=["grid_x", "grid_y", "year"], how="inner")
    OUT_UNITS.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_UNITS, index=False)

    coverage = float(df["has_neighbour"].mean())
    n_grids = df["grid_id"].nunique()
    n_years = df["exam_year"].nunique()

    # alpha: intercept-only NB estimate, else fixed 1.0 (both reported).
    try:
        nb0 = sm.NegativeBinomial(df["jinshi_count"].to_numpy(),
                                  np.ones((len(df), 1))).fit(disp=0)
        alpha = float(nb0.params[-1])
        alpha_src = "estimated (intercept-only NB)"
        if not np.isfinite(alpha) or alpha <= 0:
            alpha, alpha_src = 1.0, "fixed 1.0 (invalid estimate)"
    except Exception as exc:
        alpha, alpha_src = 1.0, f"fixed 1.0 (estimation failed: {type(exc).__name__})"

    lines_head = [
        "# A2 — spatial spillover results (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a2_spillover_analysis.py`",
        "- Pre-registration: `docs/a2_spillover_preregistration.md` (frozen before run).",
        "- Model: negative-binomial GLM (log link), `jinshi_count ~ direct + "
        "spillover + C(exam_year) + C(grid)`, SE clustered by grid.",
        f"- NB alpha: {alpha:.4f} ({alpha_src}).",
        f"- Units: {len(df)}; grids: {n_grids}; exam years: {n_years}.",
        f"- Queen-neighbour coverage: **{coverage*100:.1f}%** "
        f"(pre-registered minimum {MIN_NEIGHBOUR_COVERAGE*100:.0f}%).",
        "",
    ]

    if coverage < MIN_NEIGHBOUR_COVERAGE:
        doc_lines = lines_head + [
            "## Verdict: NOT IDENTIFIABLE",
            "",
            "Fewer than 60% of units have a queen neighbour in the panel. Per the "
            "pre-registration the spillover is declared not identifiable and no "
            "coefficient is reported.",
            "",
            "Private inputs; aggregate outputs only.",
            "",
        ]
        DOC.write_text("\n".join(doc_lines), encoding="utf-8")
        print("NOT IDENTIFIABLE: neighbour coverage", coverage)
        return

    try:
        model = smf.glm(
            FORMULA, data=df,
            family=sm.families.NegativeBinomial(alpha=alpha),
        ).fit(cov_type="cluster", cov_kwds={"groups": df["grid_id"]})
    except Exception as exc:
        DOC.write_text("\n".join(lines_head + [
            "## Verdict: MODEL FAILED",
            "",
            f"GLM fit raised `{type(exc).__name__}: {exc}`. Per the "
            "pre-registration the estimator is **not** silently switched; the "
            "failure is reported instead.",
        ]) + "\n", encoding="utf-8")
        print("MODEL FAILED:", type(exc).__name__, exc)
        return

    rows = []
    for term in ("direct", "spillover"):
        lo, hi = (float(v) for v in model.conf_int().loc[term])
        rows.append({
            "term": term,
            "coef": float(model.params[term]),
            "std_err": float(model.bse[term]),
            "ci_low": lo, "ci_high": hi,
            "p_value": float(model.pvalues[term]),
            "significant": bool(not (lo <= 0 <= hi)),
        })
    coef_df = pd.DataFrame(rows)
    coef_df.to_csv(OUT_COEF, index=False)

    d_sig = bool(coef_df.loc[coef_df.term == "direct", "significant"].iloc[0])
    s_sig = bool(coef_df.loc[coef_df.term == "spillover", "significant"].iloc[0])
    d_coef = float(coef_df.loc[coef_df.term == "direct", "coef"].iloc[0])
    s_coef = float(coef_df.loc[coef_df.term == "spillover", "coef"].iloc[0])
    if s_sig and abs(s_coef) > abs(d_coef):
        verdict = "REGIONAL (spillover dominates; A3 local wording must be rewritten)"
    elif d_sig and not s_sig:
        verdict = "LOCAL (direct effect; spillover null)"
    elif not d_sig and not s_sig:
        verdict = "NULL (both CIs include 0; stop, no respecification)"
    else:
        verdict = "MIXED (report both coefficients; no post-hoc reinterpretation)"

    table = [
        "| term | coef | cluster SE | 95% CI | p | significant |",
        "|---|---:|---:|---|---:|---|",
    ] + [
        f"| {r.term} | {r.coef:+.5f} | {r.std_err:.5f} | "
        f"[{r.ci_low:+.5f}, {r.ci_high:+.5f}] | {r.p_value:.4f} | "
        f"{'yes' if r.significant else 'no'} |"
        for r in coef_df.itertuples(index=False)
    ]
    doc_lines = lines_head + [
        f"## Verdict: {verdict}",
        "",
        *table,
        "",
        "Pre-registered interpretation rule (§5) applied mechanically; no "
        "window, adjacency, control or fixed-effect changes were made after "
        "seeing the coefficients.",
        "",
        "## When this result would fail",
        "",
        "- If a different adjacency (rook / distance band) or lag window is used, "
        "the coefficients are not comparable; both are frozen.",
        "- If the NB alpha is re-estimated on the full model, standard errors move.",
        "- Counts include only CBDB records with a parsed rank; rank-missing "
        "records are not modelled (selection into parsing is a limitation).",
        "- Zero-inflated counts are handled by NB, not by a hurdle model; "
        "over-dispersion is absorbed by alpha.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| coefficient table | `data/derived/a2_spillover_coefficients.csv` |",
        "| unit-level data | `data/derived/a2_spillover_units.csv` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(doc_lines), encoding="utf-8")
    print(coef_df.to_string(index=False))
    print("verdict:", verdict)
    print(f"wrote {OUT_COEF}, {OUT_UNITS}, {DOC}")


if __name__ == "__main__":
    main()
