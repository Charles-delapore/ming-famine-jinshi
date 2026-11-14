"""P0-3 salvage (Amendment 2): common-support time perturbation, paired lag
stability and a record-bias dose-response.

Everything here is fixed in docs/p0_3_preregistration_amendment_2.md BEFORE the
run. The original step-3 result is not overwritten; this script adds a second,
separately motivated robustness round.

Usage::

    python scripts/p0_3b_salvage.py

Outputs::

    data/derived/p0_3b_time_common_support.csv
    data/derived/p0_3b_lag_distribution.csv
    data/derived/p0_3b_paired_lag.csv
    data/derived/p0_3b_record_bias_levels.csv
    data/derived/p0_3b_record_bias_logit.csv
    figures/p0_3b_time_robustness.png / .pdf
    docs/p0_3b_salvage.md

Reads private real data; outputs are aggregate only.
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
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corrected_robustness as cr  # noqa: E402

PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
GRANGER = ROOT / "output" / "v03" / "granger_v03.xlsx"
CITY = Path(os.environ.get(
    "MING_CITYS",
    r"data/private/table_citys.xlsx",
))

OUT_TIME = ROOT / "data" / "derived" / "p0_3b_time_common_support.csv"
OUT_DIST = ROOT / "data" / "derived" / "p0_3b_lag_distribution.csv"
OUT_PAIRED = ROOT / "data" / "derived" / "p0_3b_paired_lag.csv"
OUT_LEVELS = ROOT / "data" / "derived" / "p0_3b_record_bias_levels.csv"
OUT_LOGIT = ROOT / "data" / "derived" / "p0_3b_record_bias_logit.csv"
OUT_PNG = ROOT / "figures" / "p0_3b_time_robustness.png"
OUT_PDF = ROOT / "figures" / "p0_3b_time_robustness.pdf"
OUT_DOC = ROOT / "docs" / "p0_3b_salvage.md"

# FROZEN in Amendment 2.
WINDOW = (1511, 1614)
SHIFTS = [-5, -3, -1, 0, 1, 3, 5]
FDR_TOL_1 = 0.25
FDR_TOL_3 = 0.40
SHORT_TOL_PP = 10.0
PAIRED_MED_1 = 2.0
PAIRED_SHARE_3 = 0.60
PROXY_GAP_PP = 10.0
SHORT_LAG = 5

KEYS = ["year", "grid_x", "grid_y"]
Z_COLS = ["zaihuang_level", "zaihuang_count", "zaihuang_severity"]
J_COL = "jinshi_count"


def perturb_common(panel: pd.DataFrame, k: int) -> pd.DataFrame:
    """Shift famine on the full panel, then clip every panel to WINDOW."""
    z = panel[KEYS + Z_COLS].copy()
    z["year"] = z["year"] + k
    out = panel[KEYS + [J_COL]].merge(z, on=KEYS, how="left")
    out[Z_COLS] = out[Z_COLS].fillna(0)
    lo, hi = WINDOW
    return out[out["year"].between(lo, hi)][KEYS + Z_COLS + [J_COL]]


def metrics(g: pd.DataFrame) -> dict:
    fdr = g["gc_z_to_j_fdr_sig"].astype(bool)
    lags = g.loc[fdr, "gc_z_to_j_lag"]
    return {
        "grids_tested": int(len(g)),
        "fdr_sig": int(fdr.sum()),
        "median_lag": float(lags.median()) if len(lags) else float("nan"),
        "short_lag_share": float((lags <= SHORT_LAG).mean()) if len(lags) else float("nan"),
        "long_lag_n": int((lags > 10).sum()) if len(lags) else 0,
    }


def run_time(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    dist_rows = []
    grids = {}
    for k in SHIFTS:
        g = cr.run_granger(perturb_common(panel, k))
        m = metrics(g)
        m["shift_years"] = k
        rows.append(m)
        grids[k] = g
        sig = g[g["gc_z_to_j_fdr_sig"].astype(bool)]
        bins = pd.cut(sig["gc_z_to_j_lag"], bins=[0, 5, 10, 14, 20],
                      labels=["1-5", "6-10", "11-14", "15-20"])
        vc = bins.value_counts().reindex(["1-5", "6-10", "11-14", "15-20"], fill_value=0)
        for label, n in vc.items():
            dist_rows.append({"shift_years": k, "lag_bin": label, "n": int(n)})

    time_df = pd.DataFrame(rows).sort_values("shift_years").reset_index(drop=True)
    dist_df = pd.DataFrame(dist_rows)

    base = grids[0]
    base_sig = base[base["gc_z_to_j_fdr_sig"].astype(bool)][["grid_x", "grid_y", "gc_z_to_j_lag"]]
    base_sig = base_sig.rename(columns={"gc_z_to_j_lag": "lag_base"})
    paired_rows = []
    for k in SHIFTS:
        m = base_sig.merge(
            grids[k][["grid_x", "grid_y", "gc_z_to_j_lag", "gc_z_to_j_fdr_sig"]],
            on=["grid_x", "grid_y"], how="inner",
        )
        d = (m["gc_z_to_j_lag"] - m["lag_base"]).abs()
        paired_rows.append({
            "shift_years": k,
            "n_paired": int(len(d)),
            "median_abs_change": float(d.median()) if len(d) else float("nan"),
            "share_within_3": float((d <= 3).mean()) if len(d) else float("nan"),
            "still_fdr_sig": int(m["gc_z_to_j_fdr_sig"].astype(bool).sum()),
        })
    paired_df = pd.DataFrame(paired_rows).sort_values("shift_years").reset_index(drop=True)

    OUT_TIME.parent.mkdir(parents=True, exist_ok=True)
    time_df.to_csv(OUT_TIME, index=False)
    dist_df.to_csv(OUT_DIST, index=False)
    paired_df.to_csv(OUT_PAIRED, index=False)
    return time_df, dist_df, paired_df


def evaluate_time(time_df: pd.DataFrame, paired_df: pd.DataFrame) -> tuple[list[str], dict]:
    base = time_df.loc[time_df.shift_years == 0].iloc[0]
    failures = []
    checks = {"fdr1": True, "short1": True, "fdr3": True, "paired1": True, "paired3": True}
    for k in (-1, 1):
        r = time_df.loc[time_df.shift_years == k].iloc[0]
        if abs(r.fdr_sig - base.fdr_sig) > FDR_TOL_1 * base.fdr_sig:
            failures.append(f"k={k:+d}: FDR grids {r.fdr_sig} outside ±25% of {base.fdr_sig}")
            checks["fdr1"] = False
        if abs(r.short_lag_share - base.short_lag_share) * 100 > SHORT_TOL_PP:
            failures.append(
                f"k={k:+d}: short-lag share {r.short_lag_share:.2f} vs {base.short_lag_share:.2f}"
            )
            checks["short1"] = False
    for k in (-3, 3):
        r = time_df.loc[time_df.shift_years == k].iloc[0]
        if abs(r.fdr_sig - base.fdr_sig) > FDR_TOL_3 * base.fdr_sig:
            failures.append(f"k={k:+d}: FDR grids {r.fdr_sig} outside ±40% of {base.fdr_sig}")
            checks["fdr3"] = False
    p1 = paired_df.loc[paired_df.shift_years.isin([-1, 1])]
    for _, r in p1.iterrows():
        if r.median_abs_change > PAIRED_MED_1:
            failures.append(
                f"k={r.shift_years:+d}: paired median |Δlag| {r.median_abs_change:.1f} yr"
            )
            checks["paired1"] = False
    p3 = paired_df.loc[paired_df.shift_years.isin([-3, 3])]
    for _, r in p3.iterrows():
        if r.share_within_3 < PAIRED_SHARE_3:
            failures.append(
                f"k={r.shift_years:+d}: only {r.share_within_3:.0%} paired within ±3 yr"
            )
            checks["paired3"] = False
    return failures, checks


def level_table(values: pd.Series, outcome: pd.Series,
                levels: list[tuple[int, str]]) -> pd.DataFrame:
    rows = []
    for code, label in levels:
        mask = values == code
        n = int(mask.sum())
        rate = float(outcome[mask].mean()) if n else float("nan")
        rows.append({"level": label, "n": n, "fdr_rate": rate})
    return pd.DataFrame(rows)


def record_bias() -> tuple[pd.DataFrame, pd.DataFrame]:
    granger = pd.read_excel(GRANGER)
    panel = pd.read_csv(PANEL)
    outcome = granger.set_index(["grid_x", "grid_y"])["gc_z_to_j_fdr_sig"].astype(float)

    a = panel.groupby(["grid_x", "grid_y"])["zaihuang_count"].sum()
    city = pd.read_excel(CITY)
    city["grid_x"] = np.floor(city["x"] / 1.0) + 0.5
    city["grid_y"] = np.floor(city["y"] / 1.0) + 0.5
    b = city.groupby(["grid_x", "grid_y"]).size()

    idx = outcome.index
    a = a.reindex(idx).fillna(0)
    b = b.reindex(idx).fillna(0)

    b_level = pd.cut(b, bins=[0.5, 1.5, 2.5, np.inf], labels=[1, 2, 3]).astype(int)
    a_rank = pd.qcut(a.rank(method="first"), 4, labels=[0, 1, 2, 3]).astype(int)

    b_tab = level_table(b_level, outcome, [(1, "1"), (2, "2"), (3, "3+")])
    b_tab.insert(0, "proxy", "B administrative density")
    a_tab = level_table(a_rank, outcome, [(0, "Q1"), (1, "Q2"), (2, "Q3"), (3, "Q4")])
    a_tab.insert(0, "proxy", "A famine count")
    levels = pd.concat([b_tab, a_tab], ignore_index=True)

    def monotone(rates: pd.Series) -> bool:
        d = np.diff(rates.dropna().values)
        return bool(len(d) == 0 or np.all(d > 0) or np.all(d < 0))

    b_valid = b_tab.dropna(subset=["fdr_rate"])
    a_valid = a_tab.dropna(subset=["fdr_rate"])
    b_gap = (b_valid.fdr_rate.iloc[-1] - b_valid.fdr_rate.iloc[0]) * 100
    a_gap = (a_valid.fdr_rate.iloc[-1] - a_valid.fdr_rate.iloc[0]) * 100
    levels.attrs["B_gap_pp"] = b_gap
    levels.attrs["A_gap_pp"] = a_gap
    levels.attrs["B_monotone"] = monotone(b_tab.fdr_rate)
    levels.attrs["A_monotone"] = monotone(a_tab.fdr_rate)
    levels.attrs["B_spearman"] = float(stats.spearmanr(b_level, outcome).statistic)
    levels.attrs["A_spearman"] = float(stats.spearmanr(a_rank, outcome).statistic)

    df = pd.DataFrame({
        "fdr": outcome.values,
        "b_level": b_level.values,
        "a_rank": a_rank.values,
        "a_count": a.values,
        "b_count": b.values,
    })

    import statsmodels.formula.api as smf

    try:
        model = smf.logit("fdr ~ C(b_level) + a_rank", data=df).fit(disp=0)
        params = model.params
        conf = model.conf_int()
        rows = []
        for term in params.index:
            if term == "Intercept":
                continue
            rows.append({
                "term": term,
                "odds_ratio": float(np.exp(params[term])),
                "ci_low": float(np.exp(conf.loc[term, 0])),
                "ci_high": float(np.exp(conf.loc[term, 1])),
                "p_value": float(model.pvalues[term]),
            })
        logit = pd.DataFrame(rows)
    except Exception as exc:  # noqa: BLE001
        logit = pd.DataFrame([{"term": "fit_failed", "odds_ratio": np.nan,
                               "ci_low": np.nan, "ci_high": np.nan,
                               "p_value": np.nan, "note": str(exc)}])

    levels.to_csv(OUT_LEVELS, index=False)
    logit.to_csv(OUT_LOGIT, index=False)
    return levels, logit


def make_figure(time_df: pd.DataFrame) -> None:
    d = time_df.sort_values("shift_years")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.0, 4.6), sharex=True)
    base = d.loc[d.shift_years == 0].iloc[0]

    ax1.plot(d.shift_years, d.fdr_sig, "o-", color="#0072B2", lw=1.4, ms=4)
    ax1.axhline(base.fdr_sig, color="#D55E00", ls="--", lw=1.0,
                label=f"restricted baseline {int(base.fdr_sig)}")
    ax1.axhspan(base.fdr_sig * (1 - FDR_TOL_1), base.fdr_sig * (1 + FDR_TOL_1),
                color="#0072B2", alpha=0.10, label="±25% at |k|≤1")
    ax1.set_ylabel("FDR-significant grids")
    ax1.set_title("Common-support time perturbation (window 1511–1614)",
                  fontsize=9, loc="left")
    ax1.legend(fontsize=6.5, loc="lower left")

    ax2.plot(d.shift_years, d.short_lag_share * 100, "s-", color="#009E73", lw=1.4, ms=4)
    ax2.axhline(base.short_lag_share * 100, color="#D55E00", ls="--", lw=1.0,
                label=f"baseline {base.short_lag_share:.0%}")
    ax2.set_ylabel("Share of FDR grids with lag ≤ 5 yr (%)")
    ax2.set_xlabel("Famine-series shift k (years)")
    ax2.set_xticks(list(d.shift_years))
    ax2.legend(fontsize=6.5, loc="lower left")

    for ax in (ax1, ax2):
        ax.grid(alpha=0.25, lw=0.5)
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=300)
    fig.savefig(OUT_PDF)
    plt.close(fig)


def write_doc(time_df, dist_df, paired_df, failures, checks, levels, logit) -> None:
    base = time_df.loc[time_df.shift_years == 0].iloc[0]
    passes_1 = bool(checks["fdr1"] and checks["short1"] and checks["paired1"])
    passes_3 = bool(checks["fdr3"] and checks["paired3"])

    lines = [
        "# P0-3 salvage — common-support perturbation and lag stability (2026-11-14)",
        "",
        f"- Generated: {datetime.now():%Y-%m-%d %H:%M}",
        "- Command: `python scripts/p0_3b_salvage.py`",
        "- Pre-registered choices: `docs/p0_3_preregistration_amendment_2.md` (frozen before this run).",
        f"- Input: real `output/v03/panel_v03.csv.gz`, restricted to {WINDOW[0]}–{WINDOW[1]}.",
        "",
        "## 1. Why this exists",
        "",
        "The first ±k test changed the observation window as well as the alignment, and",
        "the lag distribution is bimodal (1–3 yr or 15–20 yr), so the median is fragile.",
        "This round fixes the window to the maximal common support of all shifts.",
        "",
        "## 2. Common-support time perturbation",
        "",
        "| k (yr) | grids | FDR grids | median lag | short-lag share (≤5 yr) | long lags (>10) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in time_df.iterrows():
        lines.append(
            f"| {int(r.shift_years):+d} | {int(r.grids_tested)} | {int(r.fdr_sig)} | "
            f"{r.median_lag:.1f} | {r.short_lag_share:.0%} | {int(r.long_lag_n)} |"
        )

    lines += [
        "",
        f"Restricted baseline: **{int(base.fdr_sig)} grids**, short-lag share "
        f"**{base.short_lag_share:.0%}**, median lag {base.median_lag:.1f} yr.",
        "",
        "### Pass criteria",
        "",
        f"- ±1 yr: FDR count within ±25% and short-lag share within ±10 pp → "
        f"**{'PASS' if passes_1 else 'FAIL'}**",
        f"- ±3 yr: FDR count within ±40% → **{'PASS' if passes_3 else 'FAIL'}**",
        f"- Paired lag stability at ±1 yr (median |Δlag| ≤ 2 yr) and ±3 yr "
        f"(≥60% within ±3 yr)",
        "",
        "### Failures recorded",
        "",
    ]
    lines += [f"- {f}" for f in failures] if failures else ["- none"]
    lines += [
        "",
        "### Lag distribution by shift",
        "",
        "| k | 1–5 | 6–10 | 11–14 | 15–20 |",
        "|---:|---:|---:|---:|---:|",
    ]
    pivot = dist_df.pivot(index="shift_years", columns="lag_bin", values="n").fillna(0)
    for k in sorted(pivot.index):
        row = pivot.loc[k]
        lines.append(
            f"| {k:+d} | {int(row.get('1-5', 0))} | {int(row.get('6-10', 0))} | "
            f"{int(row.get('11-14', 0))} | {int(row.get('15-20', 0))} |"
        )

    lines += [
        "",
        "### Paired lag change on baseline-significant grids",
        "",
        "| k | paired grids | median |Δlag| | share within ±3 yr | still FDR-significant |",
        "|---:|---:|---:|---:|---:|",
    ]
    for _, r in paired_df.iterrows():
        lines.append(
            f"| {int(r.shift_years):+d} | {int(r.n_paired)} | {r.median_abs_change:.1f} | "
            f"{r.share_within_3:.0%} | {int(r.still_fdr_sig)} |"
        )

    b = levels[levels.proxy.str.startswith("B")]
    a = levels[levels.proxy.str.startswith("A")]
    lines += [
        "",
        "## 3. Record-bias dose-response",
        "",
        "| proxy | level | n | FDR rate |",
        "|---|---|---:|---:|",
    ]
    for _, r in levels.iterrows():
        lines.append(f"| {r.proxy} | {r.level} | {r.n} | {r.fdr_rate:.3f} |")

    b_gap = levels.attrs["B_gap_pp"]
    a_gap = levels.attrs["A_gap_pp"]
    b_mono = levels.attrs["B_monotone"]
    a_mono = levels.attrs["A_monotone"]
    rb_pass = bool(b_mono and a_mono and b_gap >= PROXY_GAP_PP and a_gap >= PROXY_GAP_PP)
    lines += [
        "",
        f"- Proxy B: monotone = **{b_mono}**, top-vs-bottom = **{b_gap:+.1f} pp**, "
        f"Spearman ρ = {levels.attrs['B_spearman']:.2f}",
        f"- Proxy A: monotone = **{a_mono}**, top-vs-bottom = **{a_gap:+.1f} pp**, "
        f"Spearman ρ = {levels.attrs['A_spearman']:.2f}",
        f"- Dose-response criterion (both proxies monotone and ≥10 pp): "
        f"**{'PASS' if rb_pass else 'FAIL'}**",
        "",
        "Logistic model `FDR ~ C(B level) + A quartile`:",
        "",
        "| term | OR | 95% CI | p |",
        "|---|---:|---|---:|",
    ]
    for _, r in logit.iterrows():
        lines.append(
            f"| {r.term} | {r.odds_ratio:.2f} | {r.ci_low:.2f}–{r.ci_high:.2f} | {r.p_value:.3f} |"
        )

    lines += [
        "",
        "## 4. Coordinate precision",
        "",
        "Not testable with the available fields (Amendment 2 §5). Step 2 remains void;",
        "no substitute test is invented.",
        "",
        "## 5. What the headline can claim",
        "",
    ]
    if passes_1 and passes_3:
        lines.append(
            "- The FDR discovery count is stable under common-support shifts of ±1 and ±3 "
            "years; ±5 is an extreme stress test."
        )
        lines.append(
            "- The horizon should be reported as a **distribution** (short-lag share), "
            "not as a single 6.5-year median."
        )
        lines.append(
            f"- Record-bias dose-response: proxy B monotone={b_mono}, gap {b_gap:+.1f} pp; "
            f"proxy A monotone={a_mono}, gap {a_gap:+.1f} pp → "
            f"**{'SUPPORTED' if rb_pass else 'NOT SUPPORTED'}**."
        )
    elif passes_1:
        lines.append(
            "- The FDR discovery count is stable at ±1 year but not at ±3; the headline "
            "must say 'robust to ±1-year dating error', not 'robust'."
        )
    else:
        lines.append("- The discovery count is not stable even at ±1 year; rewrite the claim.")
    lines += [
        "",
        "## 6. When this would fail",
        "",
        "- If the analysis window is changed again after seeing results.",
        "- If the lag distribution is summarised by a mean or median alone.",
        "- If the record-bias proxies are redefined post hoc.",
        "",
        "Machine-readable: `data/derived/p0_3b_*.csv`.",
    ]

    OUT_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    for path in (PANEL, GRANGER, CITY):
        if not path.exists():
            raise SystemExit(f"missing input: {path}")

    panel = pd.read_csv(PANEL)
    time_df, dist_df, paired_df = run_time(panel)
    failures, checks = evaluate_time(time_df, paired_df)
    levels, logit = record_bias()
    make_figure(time_df)
    write_doc(time_df, dist_df, paired_df, failures, checks, levels, logit)
    print(time_df.to_string(index=False))
    print(paired_df.to_string(index=False))
    print("failures:", failures or "none")


if __name__ == "__main__":
    main()
