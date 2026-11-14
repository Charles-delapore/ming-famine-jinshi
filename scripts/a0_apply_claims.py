"""A0: apply the claims audit rewrites reproducibly.

The audit table is `docs/a0_claims_audit.md`. This script applies every
"rewrite" row to the public text and then checks that no uncorrected `48/135`
headline or `6.5`-lag headline survives in public pages.

Usage::

    python scripts/a0_apply_claims.py            # apply rewrites
    python scripts/a0_apply_claims.py --check    # verify only, no writes

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "a0_apply_report.md"

# (relative path, exact old text, replacement text)
RULES: list[tuple[str, str, str]] = [
    ("README.md",
     "- Famine→Jinshi Granger survives FDR in **48/135** grids; multiscale models find\n"
     "  **8** short-horizon grids and **0** at 6–10 and 11–20 years.\n"
     "- GWR is locally significant in **123/159** grids; famine severity is the\n"
     "  strongest GeoDetector factor (**q = 0.337**).",
     "- A **fixed 1–5 year** joint Granger test is FDR-significant in **2/135** grids;\n"
     "  a pre-specified 5-year search window gives **13/135**, and multiscale LASSO\n"
     "  gives **8/135** at 1–5 years with **0** at 6–10 and 11–20 years. The earlier\n"
     "  `48/135` was a 20-lag search artefact (7/135 after within-grid correction).\n"
     "- GWR is locally significant in **123/159** grids; famine severity is the\n"
     "  strongest GeoDetector factor (**q = 0.337**).\n"
     "- Under common-support ±1/±3-year shifts the discovery count is stable, and\n"
     "  there is no dose-response of discoveries to record intensity."),
    ("README.zh.md",
     "- 灾荒→进士的 Granger 因果在 **48/135** 个格网通过 FDR；多尺度模型在 1–5 年找到 **8** 个显著格网，6–10 年与 11–20 年均为 **0**。\n"
     "- GWR 在 **123/159** 个格网局部显著；灾荒强度是最强因子（**q = 0.337**）。",
     "- **固定 1–5 年**联合 Granger 检验在 **2/135** 个格网通过 FDR；预设 5 年搜索窗为 **13/135**，多尺度 LASSO 在 1–5 年找到 **8** 个、6–10 与 11–20 年均为 **0**。此前的 `48/135` 是 20 阶滞后搜索产物（组内校正后 7/135）。\n"
     "- GWR 在 **123/159** 个格网局部显著；灾荒强度是最强因子（**q = 0.337**）。\n"
     "- 共同支撑窗下 ±1/±3 年的发现数稳定；发现数对记录强度无剂量反应。"),
    ("index.html",
     '<div class="stat"><b>48/135</b><span>FDR-significant Granger grids</span></div>',
     '<div class="stat"><b>2/135</b><span>fixed 1–5 yr joint Granger (FDR)</span></div>'),
    ("index.html",
     "    <li><strong>Spatially selective signal.</strong> Famine→Jinshi Granger causality survives\n"
     "    FDR in <strong>48 of 135</strong> estimable grid cells.</li>",
     "    <li><strong>Spatially selective signal.</strong> A fixed 1–5 year joint Granger test\n"
     "    survives FDR in <strong>2 of 135</strong> grids (13/135 with a pre-specified 5-year\n"
     "    window). The earlier <strong>48/135</strong> was a 20-lag search artefact, reported\n"
     "    only as a diagnostic.</li>"),
    ("index.html",
     "famine→Jinshi grids (48/135); (C) discovery across horizons (8/0/0); (D) GeoDetector q.",
     "famine→Jinshi grids (2/135 fixed 1–5 yr; 48/135 only as a 20-lag search diagnostic); "
     "(C) discovery across horizons (8/0/0); (D) GeoDetector q."),
    ("docs/figure_plan.md",
     "in 48/135 grid cells and is concentrated in short horizons; famine severity is",
     "in 2/135 grids under a fixed 1–5 year joint test (13/135 with a 5-year search\n"
     "window); famine severity is"),
    ("docs/figure_plan.md",
     "**On figure**: 48/135 FDR-significant grids; 8 short-horizon FDR grids vs 0",
     "**On figure**: 2/135 fixed-window FDR grids (48/135 is only the 20-lag search\n"
     "diagnostic); 8 multiscale short-horizon FDR grids vs 0"),
    ("docs/figure_plan.md",
     "(A) GWR local R²; (B) 48/135 grids with FDR-significant famine→Jinshi Granger",
     "(A) GWR local R²; (B) 2/135 grids with fixed 1–5 yr FDR-significant\n"
     "famine→Jinshi Granger"),
    ("docs/figure_plan.md",
     "median significant lag 11.0 → 6.5 years. The v0.2 values here are **baseline",
     "selected lag 11.0 → 6.5 years (bimodal distribution; reported as a share, not\n"
     "a headline). The v0.2 values here are **baseline"),
    ("docs/figure_plan.md",
     "a headline). The v0.2 values here are **baseline\n"
     "comparison values**, not current headline figures. Current headline values are\n"
     "48/135, 123/159, 8/0/0 and q = 0.337/0.186/0.128 (Figures 1–2 and",
     "a headline). The v0.2 values here are **baseline comparison values**, not\n"
     "current headline figures. Current headline values are 2/135 (fixed 1–5 yr\n"
     "joint), 13/135 (5-yr window), 123/159, 8/0/0 and q = 0.337/0.186/0.128;\n"
     "`48/135` is only the 20-lag search diagnostic (Figures 1–2 and"),
    ("docs/figure_plan.md",
     "significant lag shifts from 11 to 6.5 years, so lag claims are the least robust",
     "selected lag shifts from 11 to 6.5 years in a bimodal distribution, so lag\n"
     "claims are the least robust"),
    ("docs/figure_plan.md",
     "moves FDR discovery from 56 to 48 of 135 grids, while GWR coefficients remain",
     "moves FDR discovery from 56 to 48 of 135 grids under the 20-lag search\n"
     "(2/135 in a fixed 1–5 yr test), while GWR coefficients remain"),
    ("docs/figure_plan.md",
     "| B | Jinshi 1523–1619 (normalized 1甲/2甲 elite) | position; single blue; fixed size | Jinshi table |",
     "| B | Jinshi 1521–1619 (normalized 1甲/2甲 elite) | position; single blue; fixed size | Jinshi table |"),
    ("docs/figure_qa.md",
     "- Figure 5 is an audit figure: it quotes v0.2 baseline numbers (56 vs 48 FDR\n"
     "  grids, 11.0 vs 6.5 yr median lag) solely to show what the rank fix changes.\n"
     "  Current headline numbers are 48/135, 123/159, 8/0/0 and q = 0.337/0.186/0.128.",
     "- Figure 5 is an audit figure: it quotes v0.2 baseline numbers (56 vs 48 FDR\n"
     "  grids under a 20-lag search, 11.0 vs 6.5 yr selected lag) solely to show what\n"
     "  the rank fix changes. Current headline: 2/135 (fixed 1–5 yr joint), 13/135\n"
     "  (5-yr window), 8/0/0, 123/159 and q = 0.337/0.186/0.128. `48/135` is kept\n"
     "  only as a 20-lag search diagnostic (`docs/long_tail_analysis.md`)."),
    ("docs/corrected_robustness.md",
     "- The corrected figures (v0.3) use 48/135, 123/159, 8/0/0 and GeoDetector\n"
     "  q = 0.337/0.186/0.128. See `figures/fig5_correction.png`.",
     "- The corrected figures (v0.3) use 123/159, 8/0/0 and GeoDetector\n"
     "  q = 0.337/0.186/0.128. Grid counts are reported as 2/135 (fixed 1–5 yr\n"
     "  joint) or 13/135 (5-yr window); `48/135` belongs to the 20-lag search and is\n"
     "  a diagnostic, not a headline (`docs/long_tail_analysis.md`).\n"
     "  See `figures/fig5_correction.png`."),
    ("docs/v03_model_outputs.md",
     "- Discovery count and lag are not fully robust (56→48; 11→6.5 years).",
     "- Discovery count and selected lag are not fully robust (56→48 under a 20-lag\n"
     "  search; 11→6.5 years for a bimodal lag distribution). The 48 count is a\n"
     "  diagnostic, not the headline."),
    ("docs/jinshi_provenance.md",
     "   from 56 to 48 of 135 estimable grids, GWR coefficients agree at r = 0.991, and the median\n"
     "   significant lag shifts from 11 to 6.5 years.",
     "   from 56 to 48 of 135 estimable grids under a 20-lag search (2/135 under a\n"
     "   fixed 1–5 year joint test), GWR coefficients agree at r = 0.991, and the\n"
     "   selected-lag distribution is bimodal with a 6.5-year median."),
]

PUBLIC = ["README.md", "README.zh.md", "index.html",
          "docs/figure_plan.md", "docs/figure_qa.md",
          "docs/corrected_robustness.md", "docs/v03_model_outputs.md",
          "docs/jinshi_provenance.md"]
QUALIFIERS = ("diagnostic", "artefact", "20-lag", "search", "supplement",
              "within-grid", "max_lag", "not a headline", "only",
              "搜索产物", "诊断", "20 阶", "仅")


def apply() -> list[str]:
    log = []
    for rel, old, new in RULES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            log.append(f"applied   {rel}: {old.splitlines()[0][:70]}")
        elif new in text:
            log.append(f"already   {rel}: {old.splitlines()[0][:70]}")
        else:
            log.append(f"NOT FOUND {rel}: {old.splitlines()[0][:70]}")
    return log


def check() -> list[str]:
    issues = []
    for rel in PUBLIC:
        lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            if "48/135" in line or "48 of 135" in line:
                context = (line + " " + (lines[i] if i < len(lines) else "")).lower()
                if not any(q in context for q in QUALIFIERS):
                    issues.append(
                        f"uncorrected 48/135 headline: {rel}:{i}: {line.strip()[:100]}"
                    )
    for rel in ("README.md", "README.zh.md", "index.html"):
        lines = (ROOT / rel).read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            if "6.5" in line:
                issues.append(f"6.5 headline in public page: {rel}:{i}: {line.strip()[:100]}")
    return issues


def main() -> int:
    check_only = "--check" in sys.argv
    log = [] if check_only else apply()
    issues = check()
    lines = [
        "# A0 apply report",
        "",
        f"- Mode: {'check only' if check_only else 'apply + check'}",
        f"- Rewrite rules: {len(RULES)}",
        "",
        "## Applied",
        "",
        *[f"- {entry}" for entry in (log or ["(check only)"])],
        "",
        "## Acceptance check",
        "",
        *(["- PASS: no uncorrected `48/135` headline, no `6.5` in public pages."]
          if not issues else [f"- {x}" for x in issues]),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    for entry in log:
        print(entry)
    print(f"\n{'FAIL' if issues else 'PASS'}: {len(issues)} issue(s)")
    for x in issues:
        print("  -", x)
    print(f"report: {REPORT}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
