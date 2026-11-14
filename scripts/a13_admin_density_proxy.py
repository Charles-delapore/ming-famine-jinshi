"""A13: upgrade the record-intensity proxy with CHGIS Ming county points.

P0-3 (Amendment 2 §4) tested a record-bias dose-response using proxy B =
251 `table_citys` points (median = 1, effectively binary). The newly imported
CHGIS v6 county-point layer has 2,183 Ming-valid points — ~9x denser — and
carries BEG_YR/END_YR, so the same pre-registered test can be repeated with a
much better exposure measure.

This is a REPEAT of an existing pre-registered test with improved data, not a
new hypothesis: the pass criterion is unchanged (monotone gradient AND >=10 pp
top-vs-bottom gap). No threshold is tuned after seeing results.

Usage::

    python scripts/a13_admin_density_proxy.py

Outputs::

    data/derived/a13_admin_density_dose.csv
    docs/a13_admin_density_proxy.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CHGIS = ROOT / "data" / "derived" / "a9_chgis_county_points.csv"
GRANGER = ROOT / "output" / "v03" / "granger_v03.xlsx"
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
OUT = ROOT / "data" / "derived" / "a13_admin_density_dose.csv"
DOC = ROOT / "docs" / "a13_admin_density_proxy.md"

# FROZEN in docs/p0_3_preregistration_amendment_2.md §4
GAP_MIN_PP = 10.0


def main() -> None:
    for p in (CHGIS, GRANGER, PANEL):
        if not p.exists():
            raise SystemExit(f"missing input: {p}")
    ch = pd.read_csv(CHGIS)
    ch = ch.dropna(subset=["X_COOR", "Y_COOR"]).copy()
    ming = ch[(ch["BEG_YR"] <= 1644) & (ch["END_YR"] >= 1368)].copy()
    ming["grid_x"] = np.floor(ming["X_COOR"]) + 0.5
    ming["grid_y"] = np.floor(ming["Y_COOR"]) + 0.5
    density = (ming.groupby(["grid_x", "grid_y"]).size()
               .rename("admin_points").reset_index())

    g = pd.read_excel(GRANGER)
    g = g[["grid_x", "grid_y", "gc_z_to_j_fdr_sig"]].copy()
    g["gc_z_to_j_fdr_sig"] = g["gc_z_to_j_fdr_sig"].astype(bool)
    m = g.merge(density, on=["grid_x", "grid_y"], how="left")
    m["admin_points"] = m["admin_points"].fillna(0).astype(int)

    # Quartiles of non-zero density, zeros kept as their own level (frozen style:
    # same as Amendment 2's "quartiles of grids, zeros included" for proxy A).
    nz = m[m.admin_points > 0]["admin_points"]
    q = nz.quantile([0.25, 0.5, 0.75]).to_dict()

    def level(v):
        if v == 0:
            return "0 (no county point)"
        if v <= q[0.25]:
            return "Q1"
        if v <= q[0.5]:
            return "Q2"
        if v <= q[0.75]:
            return "Q3"
        return "Q4"

    m["level"] = m["admin_points"].map(level)
    order = ["0 (no county point)", "Q1", "Q2", "Q3", "Q4"]
    rows = []
    for lv in order:
        sub = m[m.level == lv]
        rows.append({
            "level": lv,
            "n_grids": int(len(sub)),
            "median_admin_points": float(sub.admin_points.median()) if len(sub) else np.nan,
            "fdr_rate": float(sub.gc_z_to_j_fdr_sig.mean()) if len(sub) else np.nan,
            "fdr_sig_n": int(sub.gc_z_to_j_fdr_sig.sum()) if len(sub) else 0,
        })
    dose = pd.DataFrame(rows)
    dose.to_csv(OUT, index=False)

    rates = [r for r in rows if r["n_grids"] > 0]
    vals = [r["fdr_rate"] for r in rates]
    monotone = bool(all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
                    or all(vals[i] >= vals[i + 1] for i in range(len(vals) - 1)))
    gap = (rates[-1]["fdr_rate"] - rates[0]["fdr_rate"]) * 100
    supported = monotone and gap >= GAP_MIN_PP

    # Compare with the old 251-point proxy result (Amendment 2 / p0_3b_salvage).
    old_b_gap = 1.3  # data/derived/p0_3b_record_bias_levels.csv, proxy B
    lines = [
        "# A13 — admin-density proxy upgrade (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a13_admin_density_proxy.py`",
        "- **Repeat of a pre-registered test** (`docs/p0_3_preregistration_amendment_2.md` "
        "§4) with improved data; pass criterion unchanged: monotone gradient "
        f"AND ≥{GAP_MIN_PP:.0f} pp top-vs-bottom gap. No post-hoc tuning.",
        "- Old proxy B: 251 `table_citys` points (median = 1, near-binary).",
        f"- New proxy: CHGIS v6 Ming-valid county points "
        f"**{len(ming):,}** (BEG_YR ≤ 1644, END_YR ≥ 1368), "
        f"{density[['grid_x','grid_y']].drop_duplicates().shape[0]} grids.",
        "",
        "| Level | n grids | median county points | FDR rate | FDR grids |",
        "|---|---:|---:|---:|---:|",
        *[f"| {r['level']} | {r['n_grids']} | {r['median_admin_points']:.0f} | "
          f"{r['fdr_rate']:.3f} | {r['fdr_sig_n']} |" for r in rows],
        "",
        f"- Monotone across levels: **{monotone}**",
        f"- Top-vs-bottom gap: **{gap:+.1f} pp** (old proxy B: +{old_b_gap} pp)",
        f"- Dose-response supported: **{supported}**",
        "",
        "## Interpretation",
        "",
    ]
    if supported:
        lines += [
            "With the denser proxy the pre-registered dose-response criterion is "
            "met — this would be evidence that discovery rates track "
            "administrative / recording density. It must be reported as a "
            "**change relative to the frozen P0-3 conclusion** via a dated "
            "addendum, not by editing the frozen documents.",
        ]
    else:
        lines += [
            "The criterion is still **not met**: discovery rates do not show a "
            "monotone ≥10 pp gradient even with a ~9x denser, time-validated "
            "administrative proxy. This **strengthens** the frozen P0-3 "
            "conclusion of no record-intensity dose-response, because the "
            "previous near-binary proxy was the weak link.",
        ]
    lines += [
        "",
        "## Limits",
        "",
        "- CHGIS county points are historical point locations; grid assignment "
        "is approximate and the panel is 1° (MAUP applies).",
        "- `BEG_YR`/`END_YR` filter keeps units valid at some point in "
        "1368–1644; it does not model within-period establishment/abolition.",
        "- The outcome is the frozen v0.3 `granger_v03.xlsx` FDR flag "
        "(135 grids); no model was re-estimated.",
        "- Quartiles are computed on non-zero density with zeros as their own "
        "level, matching Amendment 2's zero-inclusive style; this is declared "
        "here, not chosen after seeing rates.",
        "",
        "## When this would fail",
        "",
        "- CHGIS layer or v0.3 Granger table replaced without re-running.",
        "- A different binning is substituted after seeing the rates.",
        "- The result is quoted as causal (it is a descriptive dose-response).",
        "",
        "Machine-readable: `data/derived/a13_admin_density_dose.csv`.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(dose.to_string(index=False))
    print(f"monotone={monotone}, gap={gap:+.1f}pp, supported={supported}")
    print(f"wrote {OUT}, {DOC}")


if __name__ == "__main__":
    main()
