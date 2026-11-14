"""Amendment 3: coordinate-confidence sensitivity using CBDB admin levels.

Pre-registration: docs/p0_3_preregistration_amendment_3.md (frozen BEFORE run).
This replaces the "not decidable" step-2 declaration with a real test, using
newly standardized CBDB address-level data.

Usage::

    python scripts/a10_coordinate_confidence.py

Outputs::

    data/derived/a10_coordinate_tiers.csv
    data/derived/a10_coordinate_sensitivity.csv
    docs/a10_coordinate_confidence_results.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corrected_robustness as cr  # noqa: E402

RAW = Path(os.environ.get("MING_JINSHI_RAW", r"data/private/明进士.xlsx"))
PRIVATE = {
    "RAW": RAW,
    "FAMINE_MERGED": Path(r"data/private/merged_data.csv"),
    "FAMINE_EXT": Path(r"data/private/table_generals1521_1619.xlsx"),
    "CITYS": Path(r"data/private/table_citys.xlsx"),
    "JINSHI_ALL": Path(r"data/private/ming_general.csv"),
}
for attr, path in PRIVATE.items():
    setattr(cr, attr, path)

DERIVED = ROOT / "data" / "derived"
TIERS = DERIVED / "a10_coordinate_tiers.csv"
SENS = DERIVED / "a10_coordinate_sensitivity.csv"
DOC = ROOT / "docs" / "a10_coordinate_confidence_results.md"

# FROZEN in Amendment 3 §2
TIER1 = {"xian", "county", "shixiaqu"}
TIER2 = {"zhou", "fu", "jun", "dudufu", "wei", "pu", "shi", "fengjun",
         "qi", "zhangguansi", "shouyu qianhusuo"}
MATCH_MIN = 0.60
TIER3_MAX = 0.50
BASELINE_FDR = 48
BASELINE_LAG = 6.5


def tier_of(value) -> int:
    s = str(value).strip().lower()
    if s in TIER1:
        return 1
    if s in TIER2:
        return 2
    return 3


def build_tiers() -> tuple[pd.DataFrame, dict]:
    addr = pd.read_csv(DERIVED / "a9_cbdb_addr_admin_level.csv")
    links = pd.read_csv(DERIVED / "a9_person_addr_link.csv")
    merged = links.merge(addr[["c_addr_id", "c_admin_type"]],
                         on="c_addr_id", how="left")
    merged["tier"] = merged["c_admin_type"].map(tier_of)
    finest = merged.groupby("c_personid")["tier"].min()
    n_links = merged.groupby("c_personid").size()

    _, elite, _ = cr.load_jinshi()
    elite = elite.copy()
    elite["tier"] = elite["PersonID"].map(finest).fillna(3).astype(int)
    elite["n_addr_links"] = elite["PersonID"].map(n_links).fillna(0).astype(int)
    out = elite[["PersonID", "EntryYear", "X", "Y", "tier", "n_addr_links"]].copy()
    out.to_csv(TIERS, index=False)

    stats = {
        "n_elite": int(len(elite)),
        "match_rate": float(elite["PersonID"].isin(finest.index).mean()),
        "tier1": int((elite.tier == 1).sum()),
        "tier2": int((elite.tier == 2).sum()),
        "tier3": int((elite.tier == 3).sum()),
        "tier3_share": float((elite.tier == 3).mean()),
        "multi_addr_share": float((elite.n_addr_links > 1).mean()),
    }
    return elite, stats


def main() -> None:
    for p in PRIVATE.values():
        if not p.exists():
            raise SystemExit(f"missing private input: {p}")
    elite, stats = build_tiers()

    head = [
        "# Amendment 3 — coordinate-confidence sensitivity (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a10_coordinate_confidence.py`",
        "- Pre-registration: `docs/p0_3_preregistration_amendment_3.md` "
        "(frozen before this run).",
        "- Data: CBDB 2026-11-07 `ADDR_CODES.c_admin_type` joined via "
        "`BIOG_ADDR_DATA` to the 2,841 normalized elite records.",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| elite records | {stats['n_elite']:,} |",
        f"| CBDB address-link match rate | {stats['match_rate']*100:.1f}% |",
        f"| tier 1 (county) | {stats['tier1']:,} |",
        f"| tier 2 (prefecture) | {stats['tier2']:,} |",
        f"| tier 3 (coarse / unknown) | {stats['tier3']:,} |",
        f"| tier 3 share | {stats['tier3_share']*100:.1f}% |",
        f"| persons with >1 address link | {stats['multi_addr_share']*100:.1f}% |",
        "",
    ]

    if stats["match_rate"] < MATCH_MIN or stats["tier3_share"] > TIER3_MAX:
        lines = head + [
            "## Verdict: COVERAGE INSUFFICIENT",
            "",
            f"Match rate {stats['match_rate']*100:.1f}% (min {MATCH_MIN*100:.0f}%) "
            f"or tier-3 share {stats['tier3_share']*100:.1f}% (max "
            f"{TIER3_MAX*100:.0f}%) exceeds the frozen limit. Per Amendment 3 "
            "§4 no sensitivity coefficient is reported; this is a method note.",
            "",
            "Private inputs; aggregate outputs only.",
            "",
        ]
        DOC.write_text("\n".join(lines), encoding="utf-8")
        print("COVERAGE INSUFFICIENT", stats)
        return

    keep = elite[elite.tier.isin([1, 2])][["year", "X", "Y"]]
    base = pd.read_csv(cr.JINSHI_ALL).rename(columns={"EntryYear": "year"})[
        ["year", "X", "Y"]
    ]
    panel = cr.build_panel(cr.load_famine(),
                           pd.concat([base, keep], ignore_index=True))
    g = cr.run_granger(panel)
    fdr = g["gc_z_to_j_fdr_sig"]
    result = {
        "grids_tested": int(len(g)),
        "fdr_sig": int(fdr.sum()),
        "median_lag": (float(g.loc[fdr, "gc_z_to_j_lag"].median())
                       if fdr.any() else float("nan")),
        "elite_rows_kept": int(len(keep)),
        "elite_rows_dropped": int(stats["n_elite"] - len(keep)),
    }
    delta = result["fdr_sig"] - BASELINE_FDR
    big_move = abs(delta) > 0.5 * BASELINE_FDR
    pd.DataFrame([{**stats, **result, "baseline_fdr": BASELINE_FDR,
                   "fdr_delta": delta, "large_move": big_move}]).to_csv(SENS, index=False)

    lines = head + [
        "## Sensitivity run (tiers 1+2 kept, tier 3 dropped)",
        "",
        "| Quantity | Restricted | Frozen v0.3 baseline (20-lag diagnostic) |",
        "|---|---:|---:|",
        f"| elite rows | {result['elite_rows_kept']:,} | {stats['n_elite']:,} |",
        f"| grids tested | {result['grids_tested']} | 135 |",
        f"| FDR-significant grids | {result['fdr_sig']} | {BASELINE_FDR} |",
        f"| median selected lag | {result['median_lag']:.1f} | {BASELINE_LAG} |",
        "",
        f"FDR change: **{delta:+d}** grids ({delta/BASELINE_FDR*100:+.1f}% of "
        f"the 20-lag diagnostic).",
        "",
    ]
    if big_move:
        lines += [
            "⚠️ The frozen ±50% criterion is breached. Per Amendment 3 §4 this is "
            "reported as a **sensitivity limitation**, not a corrected headline; "
            "no re-specification is performed.",
        ]
    else:
        lines += [
            "The FDR count stays within the frozen ±50% band, so the descriptive "
            "spatial conclusions are not driven by coarse / unresolvable address "
            "records. This is a robustness addition; `docs/a3_main_results.md` "
            "headline numbers are unchanged.",
        ]
    lines += [
        "",
        "## Interpretation limits",
        "",
        "- `c_admin_type` is an **administrative-level proxy** for coordinate "
        "precision, not a measured geocoding error.",
        "- Persons with several address links take the finest tier; the "
        "multi-address share is reported above.",
        "- CHGIS v6 county points (`data/derived/a9_chgis_county_points.csv`) "
        "were used only as an independent cross-check in "
        "`docs/a10_new_data_replication.md`, not to redefine tiers.",
        "",
        "## When this would fail",
        "",
        "- CBDB build replaced without re-running `a9_import_new_sources.py`.",
        "- Tier map changed after seeing the coefficient (forbidden).",
        "- Baseline re-used from a different window; both rows above use the "
        "same 20-lag pipeline.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| tier assignment | `data/derived/a10_coordinate_tiers.csv` |",
        "| sensitivity summary | `data/derived/a10_coordinate_sensitivity.csv` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(result, "delta", delta, "large_move", big_move)
    print(f"wrote {TIERS}, {SENS}, {DOC}")


if __name__ == "__main__":
    main()
