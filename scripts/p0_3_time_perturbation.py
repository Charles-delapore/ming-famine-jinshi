"""P0-3 step 3 (pre-registered): time-perturbation sensitivity.

Reads the real v0.3 panel, shifts the famine series by a FIXED set of year
offsets, and re-estimates Granger + BH FDR with the unchanged pipeline in
scripts/corrected_robustness.py. Shifts and failure criteria are frozen in
docs/p0_3_preregistration.md BEFORE this script is run.

Usage::

    python scripts/p0_3_time_perturbation.py

Outputs::

    data/derived/p0_3_sensitivity_time.csv
    figures/p0_3_time_perturbation.png / .pdf
    docs/p0_3_sensitivity.md

Reads private real data; outputs are aggregate only.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corrected_robustness as cr  # noqa: E402

PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
OUT_CSV = ROOT / "data" / "derived" / "p0_3_sensitivity_time.csv"
OUT_PNG = ROOT / "figures" / "p0_3_time_perturbation.png"
OUT_PDF = ROOT / "figures" / "p0_3_time_perturbation.pdf"
OUT_DOC = ROOT / "docs" / "p0_3_sensitivity.md"

KEYS = ["year", "grid_x", "grid_y"]
Z_COLS = ["zaihuang_level", "zaihuang_count", "zaihuang_severity"]
J_COL = "jinshi_count"

# FROZEN in docs/p0_3_preregistration.md — do not change after seeing results.
SHIFTS = [0, 1, -1, 3, -3, 5, -5]
BASE_FDR = 48
BASE_LAG = 6.5
FDR_LOW, FDR_HIGH = 24, 72
LAG_TOL = 5.0


def perturb(panel: pd.DataFrame, k: int) -> pd.DataFrame:
    """Shift only the famine series by k years; Jinshi series stays fixed."""
    if k == 0:
        return panel[KEYS + Z_COLS + [J_COL]].copy()
    z = panel[KEYS + Z_COLS].copy()
    z["year"] = z["year"] + k
    out = panel[KEYS + [J_COL]].merge(z, on=KEYS, how="left")
    out[Z_COLS] = out[Z_COLS].fillna(0)
    return out[KEYS + Z_COLS + [J_COL]]


def metrics(g: pd.DataFrame) -> dict:
    fdr = g["gc_z_to_j_fdr_sig"]
    return {
        "grids_tested": int(len(g)),
        "causal_p05": int(g["gc_z_to_j_causal"].sum()),
        "fdr_sig": int(fdr.sum()),
        "median_lag": (
            float(g.loc[fdr, "gc_z_to_j_lag"].median())
            if fdr.any()
            else float("nan")
        ),
    }


def evaluate(rows: list[dict]) -> list[str]:
    """Apply the pre-registered failure criteria (no post-hoc tuning)."""
    failures: list[str] = []
    for r in rows:
        k = r["shift_years"]
        if abs(k) == 1 and not (FDR_LOW <= r["fdr_sig"] <= FDR_HIGH):
            failures.append(
                f"k={k:+d}: FDR-significant grids = {r['fdr_sig']}, outside "
                f"[{FDR_LOW}, {FDR_HIGH}] (baseline {BASE_FDR})"
            )
        lag = r["median_lag"]
        if not np.isnan(lag) and abs(lag - BASE_LAG) > LAG_TOL:
            failures.append(
                f"k={k:+d}: median FDR lag = {lag:.1f} yr, more than "
                f"{LAG_TOL} yr from baseline {BASE_LAG} yr"
            )
    for sign in (1, -1):
        seq = [
            next(r["median_lag"] for r in rows if r["shift_years"] == sign * m)
            for m in (1, 3, 5)
        ]
        if all(not np.isnan(v) for v in seq):
            diffs = np.diff(seq)
            if (np.all(diffs >= 0) or np.all(diffs <= 0)) and abs(seq[-1] - seq[0]) > LAG_TOL:
                failures.append(
                    f"k={sign:+d} side: monotone median-lag drift "
                    f"{seq[0]:.1f} -> {seq[-1]:.1f} yr (> {LAG_TOL} yr)"
                )
    return failures


def make_figure(df: pd.DataFrame) -> None:
    d = df.sort_values("shift_years")
    ks = d["shift_years"].values
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 4.8), sharex=True)

    ax1.plot(ks, d["fdr_sig"], "o-", color="#0072B2", lw=1.4, ms=4)
    ax1.axhline(BASE_FDR, color="#D55E00", ls="--", lw=1.0,
                label=f"baseline {BASE_FDR}")
    ax1.axhspan(FDR_LOW, FDR_HIGH, color="#0072B2", alpha=0.08)
    ax1.set_ylabel("FDR-significant grids (of 135)")
    ax1.legend(fontsize=7, loc="lower right")
    ax1.set_title("P0-3 time perturbation: famine series shifted, Jinshi fixed",
                  fontsize=9, loc="left")

    ax2.plot(ks, d["median_lag"], "s-", color="#009E73", lw=1.4, ms=4)
    ax2.axhline(BASE_LAG, color="#D55E00", ls="--", lw=1.0,
                label=f"baseline {BASE_LAG} yr")
    ax2.axhspan(BASE_LAG - LAG_TOL, BASE_LAG + LAG_TOL,
                color="#009E73", alpha=0.08)
    ax2.set_ylabel("Median FDR lag (yr)")
    ax2.set_xlabel("Famine-series shift k (years)")
    ax2.set_xticks(list(ks))
    ax2.legend(fontsize=7, loc="lower right")

    for ax in (ax1, ax2):
        ax.grid(alpha=0.25, lw=0.5)
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=300)
    fig.savefig(OUT_PDF)
    plt.close(fig)


def make_doc(df: pd.DataFrame, failures: list[str]) -> None:
    verdict = "FAIL" if failures else "PASS"
    rows = []
    for r in df.sort_values("shift_years").itertuples(index=False):
        lag = "n/a" if np.isnan(r.median_lag) else f"{r.median_lag:.1f}"
        rows.append(
            f"| {r.shift_years:+d} | {r.grids_tested} | {r.causal_p05} | "
            f"{r.fdr_sig} | {lag} |"
        )

    lines = [
        "# P0-3 sensitivity — time perturbation (step 3)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/p0_3_time_perturbation.py`",
        "- Pre-registered choices and failure criteria: "
        "`docs/p0_3_preregistration.md` (frozen before this run).",
        "- Input: real `output/v03/panel_v03.csv.gz`; method unchanged "
        "(`scripts/corrected_robustness.run_granger`).",
        "",
        f"**Verdict: {verdict}** "
        f"({'no failure criterion triggered' if not failures else str(len(failures)) + ' failure criterion/criteria triggered'}).",
        "",
        "| k (yr) | grids tested | causal p<0.05 | FDR-significant | median FDR lag (yr) |",
        "|---:|---:|---:|---:|---:|",
        *rows,
        "",
        "## Failure criteria (fixed before results)",
        "",
        f"- Discovery count: any `|k|=1` run outside "
        f"[{FDR_LOW}, {FDR_HIGH}] FDR grids (baseline {BASE_FDR}).",
        f"- Median lag: any run more than {LAG_TOL} yr from {BASE_LAG} yr, "
        "or a monotone drift > 5 yr on either side.",
        "- Record bias: the dual-proxy condition (§2 of the pre-registration) "
        "is evaluated in a later step, not here.",
        "",
        "## Under which perturbation the conclusion fails",
        "",
    ]
    if failures:
        lines += [f"- {f}" for f in failures]
        lines += [
            "",
            "The corresponding headline conclusion does **not** survive these "
            "perturbations within the pre-registered tolerances.",
        ]
    else:
        lines += [
            "None of the pre-registered perturbations broke the discovery-count "
            "or median-lag conclusions within the stated tolerances: every "
            "`|k|=1` run kept FDR-significant grids inside [24, 72], every run "
            "kept the median FDR lag within 5 yr of 6.5 yr, and neither side "
            "showed a >5 yr monotone drift.",
            "",
            "They would fail if a ±1-year shift moved the FDR count outside "
            "[24, 72] or pushed the median lag more than 5 yr from 6.5 yr — "
            "i.e. if the result depended on exact year alignment.",
        ]
    lines += [
        "",
        "## Limitations",
        "",
        "- Only the famine series is shifted; Jinshi years are held fixed. This "
        "tests time alignment, not independent dating error in both series.",
        "- Records shifted outside 1520–1619 are dropped; all `k` are treated "
        "identically, so the comparison is fair but boundary information is lost.",
        "- This is step 3 of P0-3 only. Record-intensity stratification (step 1) "
        "and coordinate-tier dropping (step 2) are separate, and no claim about "
        "reporting bias is made from this table alone.",
        "- Thresholds were fixed before the run; changing them requires a new "
        "dated pre-registration amendment.",
        "",
        "Machine-readable: `data/derived/p0_3_sensitivity_time.csv`. "
        "Figure: `figures/p0_3_time_perturbation.{png,pdf}`.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not PANEL.exists():
        raise SystemExit(f"missing real v0.3 panel: {PANEL}")
    panel = pd.read_csv(PANEL)
    rows: list[dict] = []
    for k in SHIFTS:
        g = cr.run_granger(perturb(panel, k))
        m = metrics(g)
        rows.append({"shift_years": k, **m})
        print(f"k={k:+d} -> {m}", flush=True)

    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    failures = evaluate(rows)
    make_figure(df)
    make_doc(df, failures)
    print(f"verdict: {'FAIL' if failures else 'PASS'} ({len(failures)} failures)")
    for f in failures:
        print("  -", f)
    print(f"wrote {OUT_CSV}, {OUT_PNG}, {OUT_DOC}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
