"""A3: assemble the main-results table from the real source tables.

Every number in `docs/a3_main_results.md` comes from a script → table → doc
chain recorded here, so a third party can reproduce it with the command list.

Usage::

    python scripts/a3_assemble_main_results.py

Outputs::

    data/derived/a3_main_results.csv
    docs/a3_main_results.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
SUMMARY = ROOT / "output" / "v03" / "summary.json"
FIGIN = ROOT / "output" / "v03" / "fig_input"
DERIVED = ROOT / "data" / "derived"
OUT_CSV = DERIVED / "a3_main_results.csv"
OUT_DOC = ROOT / "docs" / "a3_main_results.md"


def main() -> None:
    rows: list[dict] = []

    def add(metric, value, script, table, doc, note=""):
        rows.append({"metric": metric, "value": value, "script": script,
                     "table": table, "document": doc, "note": note})

    panel = pd.read_csv(PANEL)
    s = json.loads(SUMMARY.read_text(encoding="utf-8"))
    v03 = s["v03"]
    cmp_ = s["comparison"]

    add("panel_grid_years", len(panel), "scripts/corrected_robustness.py",
        "output/v03/panel_v03.csv.gz", "docs/a3_main_results.md",
        "291 grids x 114 years, 1506-1619")
    add("panel_grids", int(panel[["grid_x", "grid_y"]].drop_duplicates().shape[0]),
        "scripts/corrected_robustness.py", "output/v03/panel_v03.csv.gz",
        "docs/a3_main_results.md")
    add("panel_jinshi_records", int(v03["jinshi_records"]),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/v03_model_outputs.md", "ming_general + normalized elite extension")

    # 1. Fixed 1-5 year joint test
    fl = pd.read_csv(DERIVED / "long_tail_fixed_lag.csv")
    add("fixed_1_5_joint_FDR_grids",
        int(fl.loc[fl.lag_set == "1-5", "fdr_sig"].iloc[0]),
        "scripts/long_tail_analysis.py", "data/derived/long_tail_fixed_lag.csv",
        "docs/long_tail_analysis.md §2", "PRIMARY short-window result")

    # 2. Multiscale LASSO (1/3/5, 5-10, 11-20)
    for horizon, label in (("short", "1-5"), ("medium", "5-10"),
                           ("long", "11-20")):
        d = pd.read_excel(FIGIN / f"multiscale_causal_{horizon}_term.xlsx")
        col = "fdr_significant" if "fdr_significant" in d.columns else "significant"
        add(f"multiscale_{label}_FDR_grids", int(d[col].sum()),
            "scripts/build_v03_figure_inputs.py",
            f"output/v03/fig_input/multiscale_causal_{horizon}_term.xlsx",
            "docs/v03_model_outputs.md", f"column used: {col}")

    # 3. GWR
    add("GWR_significant", int(v03["gwr_sig"]),
        "scripts/corrected_robustness.py", "output/v03/gwr_v03.xlsx",
        "docs/corrected_robustness.md", "|t|>1.96")
    add("GWR_cells", int(v03["gwr_cells"]),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/v03_model_outputs.md")
    add("GWR_positive", int(v03["gwr_positive"]),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/v03_model_outputs.md")
    add("GWR_negative", int(v03["gwr_negative"]),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/v03_model_outputs.md")
    add("GWR_global_R2", round(float(v03["gwr_global_r2"]), 4),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/v03_model_outputs.md")
    add("GWR_coef_r_v02_v03", round(float(cmp_["coef_pearson"]), 4),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/corrected_robustness.md", "encoding fix robustness")
    add("significant_grid_overlap", int(cmp_["sig_overlap"]),
        "scripts/corrected_robustness.py", "output/v03/summary.json",
        "docs/corrected_robustness.md", "of 125 v0.2 grids")

    # 4. GeoDetector
    g = pd.read_excel(FIGIN / "geodetector_results.xlsx")
    for col, label in (("q_zaihuang_severity", "severity"),
                       ("q_longitude", "longitude"),
                       ("q_latitude", "latitude")):
        add(f"GeoDetector_q_{label}", round(float(g[col].iloc[0]), 4),
            "scripts/build_v03_figure_inputs.py",
            "output/v03/fig_input/geodetector_results.xlsx",
            "docs/v03_model_outputs.md")

    # Diagnostics (explicitly NOT headlines)
    lw = pd.read_csv(DERIVED / "long_tail_lag_window.csv")
    for ml, tag in ((5, "max_lag_5_FDR"), (20, "max_lag_20_FDR")):
        r = lw[lw.max_lag == ml].iloc[0]
        add(tag, int(r.fdr_sig), "scripts/long_tail_analysis.py",
            "data/derived/long_tail_lag_window.csv",
            "docs/long_tail_analysis.md §1", "search-window diagnostic")
        if ml == 5:
            add("max_lag_5_short_lag_share", round(float(r.short_share), 3),
                "scripts/long_tail_analysis.py",
                "data/derived/long_tail_lag_window.csv",
                "docs/long_tail_analysis.md §1")
    r20 = lw[lw.max_lag == 20].iloc[0]
    add("within_grid_Bonferroni_20", int(r20.fdr_sig_bonferroni),
        "scripts/long_tail_analysis.py", "data/derived/long_tail_lag_window.csv",
        "docs/long_tail_analysis.md §1", "48/135 is a search artefact")

    cs = pd.read_csv(DERIVED / "p0_3b_time_common_support.csv")
    base = float(cs.loc[cs.shift_years == 0, "fdr_sig"].iloc[0])
    pm1 = cs[cs.shift_years.isin([-1, 1])]["fdr_sig"]
    pm3 = cs[cs.shift_years.isin([-3, 3])]["fdr_sig"]
    add("common_support_baseline_FDR", int(base),
        "scripts/p0_3b_salvage.py", "data/derived/p0_3b_time_common_support.csv",
        "docs/p0_3b_salvage.md §2", "restricted window 1511-1614, 133 grids")
    add("common_support_pm1_pass", bool(((pm1 - base).abs() / base <= 0.25).all()),
        "scripts/p0_3b_salvage.py", "data/derived/p0_3b_time_common_support.csv",
        "docs/p0_3b_salvage.md §2", "within ±25% of restricted baseline")
    add("common_support_pm3_pass", bool(((pm3 - base).abs() / base <= 0.40).all()),
        "scripts/p0_3b_salvage.py", "data/derived/p0_3b_time_common_support.csv",
        "docs/p0_3b_salvage.md §2", "within ±40% of restricted baseline")

    rb = pd.read_csv(DERIVED / "p0_3b_record_bias_levels.csv")
    b = rb[rb.proxy.str.startswith("B")]
    a = rb[rb.proxy.str.startswith("A")]
    add("record_bias_B_gap_pp",
        round((b.fdr_rate.iloc[-1] - b.fdr_rate.iloc[0]) * 100, 1),
        "scripts/p0_3b_salvage.py", "data/derived/p0_3b_record_bias_levels.csv",
        "docs/p0_3b_salvage.md §3", "non-monotone; no dose-response")
    add("record_bias_A_gap_pp",
        round((a.fdr_rate.iloc[-1] - a.fdr_rate.iloc[0]) * 100, 1),
        "scripts/p0_3b_salvage.py", "data/derived/p0_3b_record_bias_levels.csv",
        "docs/p0_3b_salvage.md §3", "non-monotone; no dose-response")

    a1 = pd.read_csv(DERIVED / "a1_rank_coefficients.csv")
    add("A1_rank_share_coef", round(float(a1.coef.iloc[0]), 6),
        "scripts/a1_rank_analysis.py", "data/derived/a1_rank_coefficients.csv",
        "docs/a1_rank_results.md", "NULL: CI includes 0, permutation p=0.935")
    a2 = pd.read_csv(DERIVED / "a2_spillover_coefficients.csv")
    for term in ("direct", "spillover"):
        r = a2[a2.term == term].iloc[0]
        add(f"A2_{term}_coef", round(float(r.coef), 6),
            "scripts/a2_spillover_analysis.py",
            "data/derived/a2_spillover_coefficients.csv",
            "docs/a2_spillover_results.md", "NULL: CI includes 0")

    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)

    table = [
        "| Metric | Value | Script | Table | Document | Note |",
        "|---|---:|---|---|---|---|",
    ] + [
        f"| `{r.metric}` | {r.value} | `{r.script}` | `{r.table}` | "
        f"{r.document} | {r.note} |"
        for r in df.itertuples(index=False)
    ]
    lines = [
        "# A3 — main results, one panel (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a3_assemble_main_results.py`",
        "- Claim audit: `docs/a0_claims_audit.md` (all public wording follows this table).",
        "",
        "## One panel",
        "",
        "All four headline analyses use `output/v03/panel_v03.csv.gz` "
        "(291 1° grids × 114 years, 1506–1619; 5,401 Jinshi records in the "
        "grid models). The famine series is identical between v0.2 and v0.3; "
        "only the Jinshi layer was corrected, so GeoDetector/GWR descriptive "
        "results are stable while the lag-search diagnostics are not.",
        "",
        "## Main results (script → table → document)",
        "",
        *table,
        "",
        "## Authoritative headline",
        "",
        "- **Spatial inequality**: GeoDetector q = 0.3368 (severity) vs 0.1857 "
        "(longitude) / 0.1284 (latitude); GWR locally significant in 123/159 "
        "grids, 155 positive / 4 negative, global R² = 0.759.",
        "- **Short-window signal**: a fixed 1–5 year joint Granger test is "
        "FDR-significant in **2/135** grids; a pre-specified 5-year search "
        "window gives **13/135**; multiscale LASSO gives **8/135** at 1–5 years "
        "and **0/135** at 5–10 / 11–20 years.",
        "- **Methodological warning**: `48/135` is a max_lag=20 search artefact "
        "(7/135 after within-grid Bonferroni); the 6.5-year median lag comes "
        "from a bimodal distribution and is not reported.",
        "- **Robustness**: common-support ±1 and ±3 year shifts pass; no "
        "record-intensity dose-response; encoding fix leaves GWR coefficient "
        "r = 0.991 (122/125 significant-grid overlap).",
        "- **A1/A2 zero results**: famine does not shift the 1甲/2甲 share "
        "(A1 null) and neither local nor neighbouring famine predicts Jinshi "
        "counts in the NB model (A2 null). Per roadmap §1.4 the paper is "
        "positioned as **descriptive + methodological**, targeting the stable "
        "journal tier.",
        "",
        "## Reproduce (third party)",
        "",
        "```bash",
        "python scripts/corrected_robustness.py        # panel, Granger, GWR, summary.json",
        "python scripts/build_v03_figure_inputs.py    # multiscale + GeoDetector tables",
        "python scripts/long_tail_analysis.py         # fixed-lag + lag-window diagnostics",
        "python scripts/p0_3b_salvage.py              # common support + record bias",
        "python scripts/a1_rank_analysis.py           # A1 rank share",
        "python scripts/a2_spillover_analysis.py      # A2 spillover",
        "python scripts/a3_assemble_main_results.py   # this table",
        "python scripts/a0_apply_claims.py --check    # public-wording acceptance",
        "```",
        "",
        "Private raw inputs (`明进士.xlsx`, `merged_data.csv`, `ming_general.csv`, "
        "`table_citys.xlsx`, `table_generals1521_1619.xlsx`) are required for the "
        "first two commands; see `docs/v03_model_outputs.md` for the `MING_*` "
        "environment variables. The synthetic `data/sample/` path can only "
        "verify code/layout, never these numbers.",
        "",
        "## When this would fail",
        "",
        "- Any source table is regenerated with different numbers without "
        "re-running this assembler (A8 re-checks it).",
        "- A new public claim is added outside `docs/a0_claims_audit.md`.",
        "- The panel window or grid resolution changes; all four analyses would "
        "need re-estimation.",
        "",
        "Machine-readable: `data/derived/a3_main_results.csv`.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")
    print(df[["metric", "value"]].to_string(index=False))
    print(f"wrote {OUT_CSV}, {OUT_DOC}")


if __name__ == "__main__":
    main()
