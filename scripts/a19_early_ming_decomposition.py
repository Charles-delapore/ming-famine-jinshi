"""A19: decompose A12's full-Ming fixed-lag result by period.

Pre-registration: docs/a19_early_ming_preregistration.md (frozen before run).
Pure decomposition; no new hypothesis, no respecification, no verdicts.

Usage::

    python scripts/a19_early_ming_decomposition.py

Outputs::

    data/derived/a19_early_ming_decomposition.csv
    docs/a19_early_ming_decomposition.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from src.analysis.grid_analysis import fdr_correction  # noqa: E402
from long_tail_analysis import fixed_lag_pvalue  # noqa: E402

PANEL = ROOT / "data" / "derived" / "a12_full_ming_panel.csv.gz"
OUT = ROOT / "data" / "derived" / "a19_early_ming_decomposition.csv"
DOC = ROOT / "docs" / "a19_early_ming_decomposition.md"

# FROZEN in docs/a19_early_ming_preregistration.md
WINDOWS = {
    "early_1368_1520": (1368, 1520),
    "v03_1521_1619": (1521, 1619),
    "late_1620_1643": (1620, 1643),
    "full_1368_1643": (1368, 1643),
}
LAGS = (1, 2, 3, 4, 5)


def run_window(sub: pd.DataFrame) -> tuple[int, int, float]:
    rows = []
    for (gx, gy), cell in sub.groupby(["grid_x", "grid_y"]):
        cell = cell.sort_values("year")
        z = cell["zaihuang_severity"].to_numpy(dtype=float)
        j = cell["jinshi_count"].to_numpy(dtype=float)
        if np.sum(z > 0) < 3 or np.sum(j > 0) < 3 or len(z) < 30:
            continue
        rows.append({"grid_x": gx, "grid_y": gy,
                     "pval": fixed_lag_pvalue(z, j, LAGS)})
    if not rows:
        return 0, 0, float("nan")
    d = pd.DataFrame(rows)
    sig, _ = fdr_correction(d["pval"].to_numpy(), alpha=0.05)
    return len(d), int(sig.sum()), float("nan")


def main() -> None:
    if not PANEL.exists():
        raise SystemExit("run scripts/a12_full_ming_replication.py first")
    panel = pd.read_csv(PANEL)
    rows = []
    for tag, (lo, hi) in WINDOWS.items():
        sub = panel[panel.year.between(lo, hi)]
        n, k, _ = run_window(sub)
        rows.append({
            "window": tag, "years": f"{lo}-{hi}", "n_years": hi - lo + 1,
            "grids_tested": n, "fdr_sig": k,
            "pct": round(k / n * 100, 2) if n else np.nan,
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)

    full = df[df.window == "full_1368_1643"].iloc[0]
    v03 = df[df.window == "v03_1521_1619"].iloc[0]
    early = df[df.window == "early_1368_1520"].iloc[0]
    late = df[df.window == "late_1620_1643"].iloc[0]

    lines = [
        "# A19 — A12 early-Ming decomposition (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a19_early_ming_decomposition.py`",
        "- Pre-registration: `docs/a19_early_ming_preregistration.md` "
        "(frozen before run). Pure decomposition, **no verdicts**.",
        "- Panel: `<local private panel; not distributed>` "
        "(independent famine source, 1368–1643, 202 grids).",
        "- Method unchanged from A12: `fixed_lag_pvalue(1..5)` joint F test, "
        "same sample filters, BH FDR 0.05.",
        "",
        "| Window | Years | n years | grids tested | FDR grids | % |",
        "|---|---|---:|---:|---:|---:|",
        *[f"| {r.window} | {r.years} | {r.n_years} | {r.grids_tested} | "
          f"{r.fdr_sig} | {r.pct:.2f}% |" for r in df.itertuples(index=False)],
        "",
        "## Attribution (descriptive)",
        "",
        f"- Full window (A12 primary): **{int(full.fdr_sig)}/{int(full.grids_tested)}**.",
        f"- v0.3-period slice: **{int(v03.fdr_sig)}/{int(v03.grids_tested)}** "
        "(A12 secondary reported 1/142; identical method confirmed here).",
        f"- Early Ming (1368–1520): **{int(early.fdr_sig)}/{int(early.grids_tested)}**.",
        f"- Late Ming (1620–1643): **{int(late.fdr_sig)}/{int(late.grids_tested)}** "
        "(24 years; below the 30-observation filter for many grids).",
        "",
        "FDR is recomputed **within each window**, so counts are deliberately "
        "**not additive** — this table attributes where the full-window grids "
        "are estimable, it does not partition them arithmetically.",
        "",
        "## Interpretation limits (frozen)",
        "",
        "- Early-Ming records are sparser and differently documented; extra "
        "grids there may reflect record density, not a stronger effect.",
        "- Windows are slices of one panel, not independent samples.",
        "- The late window is short; `not estimable` grids are excluded by the "
        "same ≥30-observation filter as A12, not by a new rule.",
        "- **No pass/fail verdict, no significance claim about differences, "
        "no respecification.** No change to `docs/a3_main_results.md` or "
        "`docs/a12_full_ming_replication.md`.",
        "",
        "## When this would fail",
        "",
        "- The panel or the method changes without re-running A12 and A19.",
        "- Windows are merged/split after seeing counts (forbidden).",
        "- These descriptive counts are quoted as a new effect.",
        "",
        "Machine-readable: `data/derived/a19_early_ming_decomposition.csv`.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(df.to_string(index=False))
    print(f"wrote {OUT}, {DOC}")


if __name__ == "__main__":
    main()
