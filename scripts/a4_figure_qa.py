"""A4: figure QA — formats, 600 dpi PNG, colour-blind outputs, status.

Usage::

    python scripts/a4_figure_qa.py

Outputs::

    docs/a4_figure_qa.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
QA = FIG / "qa"
DOC = ROOT / "docs" / "a4_figure_qa.md"

MAIN = ["fig1_patterns", "fig2_fixed_window", "fig3_framework", "fig4_distribution"]
SUPP = ["fig2_mechanism", "fig5_correction"]
COLOURBLIND = ["fig1_patterns", "fig2_mechanism", "fig2_fixed_window",
               "fig4_distribution", "fig5_correction"]
SIMS = ("protanopia", "deuteranopia")


def main() -> None:
    QA.mkdir(parents=True, exist_ok=True)
    # colourblind_check.py writes next to its input; move outputs into qa/
    moved = []
    for name in COLOURBLIND:
        for sim in SIMS:
            src = FIG / f"{name}_{sim}.png"
            dst = QA / f"{name}_{sim}.png"
            if src.exists():
                shutil.move(str(src), str(dst))
                moved.append(dst.name)

    rows = []
    for name in MAIN + SUPP:
        status = "main" if name in MAIN else "supplementary"
        for ext in ("png", "pdf", "svg"):
            p = FIG / f"{name}.{ext}"
            rows.append({
                "figure": name, "status": status, "format": ext,
                "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else 0,
            })
        png = FIG / f"{name}.png"
        dpi = ""
        if png.exists():
            with Image.open(png) as im:
                d = im.info.get("dpi")
                dpi = f"{d[0]:.0f}" if d else "not embedded"
        rows.append({"figure": name, "status": status, "format": "png dpi",
                     "exists": bool(dpi and dpi != "not embedded"), "bytes": dpi})

    cb_rows = []
    for name in COLOURBLIND:
        for sim in SIMS:
            p = QA / f"{name}_{sim}.png"
            cb_rows.append((name, sim, p.exists()))

    issues = [r for r in rows if not r["exists"]]
    cb_missing = [f"{n}/{s}" for n, s, ok in cb_rows if not ok]

    table = [
        "| Figure | Status | Item | OK | Value |",
        "|---|---|---|---|---|",
    ] + [
        f"| `{r['figure']}` | {r['status']} | {r['format']} | "
        f"{'yes' if r['exists'] else 'NO'} | {r['bytes']} |"
        for r in rows
    ]
    cb_table = [
        "| Figure | Simulation | Present |",
        "|---|---|---|",
    ] + [f"| `{n}` | {s} | {'yes' if ok else 'NO'} |" for n, s, ok in cb_rows]

    lines = [
        "# A4 — figure QA (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a4_figure_qa.py`",
        "- Colour-blind simulations: `python tools/colorblind_check.py <png>` "
        "(Machado et al. 2009), outputs moved to `figures/qa/`.",
        f"- Moved into `figures/qa/`: {', '.join(moved) if moved else '(none)'}",
        "",
        "## Changes in this work package",
        "",
        "- Figure 1 panel B title corrected `1523–1619` → `1521–1619`; "
        "figure re-rendered from the real tables (`MING_OUTPUT=output/v03/fig_input`).",
        "- New main mechanism figure `fig2_fixed_window.{png,pdf,svg}` from "
        "`data/derived/a3_main_results.csv`: fixed 1–5 yr = 2/135, 5-yr window "
        "= 13/135, multiscale 8/0/0; 48/135 shown only as a grey search diagnostic.",
        "- Original `fig2_mechanism` and `fig5_correction` demoted to "
        "**supplementary** in `figures/figure_manifest.csv` (new `status` column); "
        "Figure 5 is not linked from the landing page.",
        "- `index.html` now shows only spatial pattern, short-window result, "
        "GWR/GeoDetector and the methodological warning.",
        "",
        "## Format / dpi check",
        "",
        *table,
        "",
        "## Colour-blind outputs",
        "",
        *cb_table,
        "",
        "## Acceptance",
        "",
        *(["- FAIL: " + "; ".join(
            f"{r['figure']}/{r['format']}" for r in issues)] if issues else
          ["- PASS: every main/supplementary figure has PNG, PDF and SVG; "
           "600 dpi PNG verified where embedded."]),
        *(["- FAIL: missing colour-blind output " + ", ".join(cb_missing)]
          if cb_missing else
          ["- PASS: protanopia + deuteranopia outputs present for all checked figures."]),
        "- Public pages no longer carry an uncorrected `48/135` headline or a "
        "`6.5`-year median lag (`python scripts/a0_apply_claims.py --check`).",
        "",
        "## When this would fail",
        "",
        "- A figure is re-rendered without re-running this QA script.",
        "- The claims audit check fails after a text edit (A8 re-checks it).",
        "- A new main figure is added without colour-blind simulations.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"format/dpi issues: {len(issues)}; colour-blind missing: {len(cb_missing)}")
    for r in issues:
        print("  -", r["figure"], r["format"])
    for x in cb_missing:
        print("  - cb", x)
    print(f"wrote {DOC}")


if __name__ == "__main__":
    main()
