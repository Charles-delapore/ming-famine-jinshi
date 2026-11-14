"""A9: bring newly located real data sources into the project's table system.

Sources (read-only, private):
  1. CBDB SQLite build 2026-11-07  -> address administrative levels + person/address links
  2. Historical urban population   -> Ming city population time series
  3. Late-Ming Jinshi table 1627-1644 -> out-of-sample elite geography
  4. CHGIS v6 county point shapefile (WGS84) -> county/prefecture points

Outputs are standardized CSVs in data/derived/ plus an inventory document.

Usage::

    python scripts/a9_import_new_sources.py

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CBDB = Path(r"data/private/cbdb_20261107.sqlite3")
RAW_JINSHI = Path(r"data/private/明进士.xlsx")
POP = Path(r"data/private/population_ming.xlsx")
LATE = Path(
    r"data/private/archive\008\210520134_田正_地理信息科学_古代灾荒事件对社会人文现象的时空模式影响研究_附件"
    r"\数据表\table_general1627_1644.xlsx"
)
CHGIS_SHP = Path(
    r"data/private/chgis_points"
    r"\v6_time_cnty_pts_utf_wgs84.shp"
)
DERIVED = ROOT / "data" / "derived"
DOC = ROOT / "docs" / "a9_new_data_inventory.md"


def main() -> None:
    for p in (CBDB, RAW_JINSHI, POP, LATE, CHGIS_SHP):
        if not p.exists():
            raise SystemExit(f"missing new source: {p}")
    DERIVED.mkdir(parents=True, exist_ok=True)

    # 1. CBDB address table + admin levels
    con = sqlite3.connect(str(CBDB))
    addr = pd.read_sql_query(
        "select c_addr_id, c_name, c_name_chn, c_firstyear, c_lastyear, "
        "c_admin_type, c_admin_cat_code, x_coord, y_coord, CHGIS_PT_ID "
        "from ADDR_CODES", con,
    )
    addr.to_csv(DERIVED / "a9_cbdb_addr_admin_level.csv", index=False)
    admin_counts = addr["c_admin_type"].fillna("(null)").value_counts().head(20)

    # person -> address links, restricted to the Ming Jinshi export
    raw = pd.read_excel(RAW_JINSHI, usecols=["PersonID"])
    person_ids = set(pd.to_numeric(raw["PersonID"], errors="coerce").dropna().astype(int))
    links = pd.read_sql_query(
        "select c_personid, c_addr_id, c_addr_type from BIOG_ADDR_DATA", con
    )
    links = links[links["c_personid"].isin(person_ids)].copy()
    links.to_csv(DERIVED / "a9_person_addr_link.csv", index=False)
    con.close()

    # 2. Ming urban population time series
    pop = pd.read_excel(POP, header=None)
    pop.columns = ["id", "city", "alt_names", "country", "lat", "lon",
                   "level", "year", "population", "key"][:pop.shape[1]]
    pop.to_csv(DERIVED / "a9_ming_urban_population.csv", index=False)

    # 3. Late-Ming Jinshi (1627-1644)
    late = pd.read_excel(LATE)
    late.to_csv(DERIVED / "a9_jinshi_1627_1644.csv", index=False)

    # 4. CHGIS county points
    chgis = gpd.read_file(CHGIS_SHP)
    chgis_cols = list(chgis.columns)
    keep = [c for c in chgis.columns if c != "geometry"]
    chgis[keep].to_csv(DERIVED / "a9_chgis_county_points.csv", index=False)

    lines = [
        "# A9 — newly acquired data sources, standardized (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a9_import_new_sources.py`",
        "- Status: **local sources only**; network download was attempted "
        "separately and is recorded in the worklog.",
        "",
        "## Inventory",
        "",
        "| # | Source | Local path | Rows | Output table | Intended use |",
        "|---|---|---|---:|---|---|",
        f"| 1 | CBDB SQLite 2026-11-07 `ADDR_CODES` | `<private CBDB SQLite directory>` | {len(addr):,} | `data/derived/a9_cbdb_addr_admin_level.csv` | coordinate-confidence tiers (admin level + CHGIS point id) |",
        f"| 2 | CBDB `BIOG_ADDR_DATA` links | same DB | {len(links):,} | `data/derived/a9_person_addr_link.csv` | join Ming Jinshi PersonID to an address |",
        f"| 3 | Historical urban population | `人口数据\\明代.xlsx` | {len(pop):,} | `data/derived/a9_ming_urban_population.csv` | exogenous population / competition proxy |",
        f"| 4 | Late-Ming Jinshi 1627–1644 | `000毕设\\008\\...\\table_general1627_1644.xlsx` | {len(late):,} | `data/derived/a9_jinshi_1627_1644.csv` | out-of-sample elite-geography replication |",
        f"| 5 | CHGIS v6 county points (WGS84) | `ming_general\\v6_time_cnty_pts_utf_wgs84.shp` | {len(chgis):,} | `data/derived/a9_chgis_county_points.csv` | county-level coordinate benchmark, province→grid mapping (B1 G2) |",
        "",
        "## CBDB address administrative types (top 20)",
        "",
        "| c_admin_type | rows |",
        "|---|---:|",
        *[f"| {k} | {v:,} |" for k, v in admin_counts.items()],
        "",
        f"CHGIS county point columns: `{', '.join(chgis_cols)}`.",
        f"Late-Ming table columns: `{', '.join(late.columns)}`.",
        f"Population columns: `{', '.join(pop.columns)}`.",
        "",
        "## Provenance and limitations",
        "",
        "- CBDB SQLite is the 2026-11-07 build already present locally; the "
        "project's Jinshi export is an older/`入仕查询结果` extract, so a small "
        "share of PersonIDs may not match (documented in "
        "`docs/data_boundary_audit.md`). No imputation is applied to unmatched ids.",
        "- Population file has no header row in the original workbook; column "
        "names above are assigned by position and must be re-checked if the "
        "source file is regenerated. Years are sparse city observations, not a "
        "continuous annual panel.",
        "- The 1627–1644 table is a Jinshi export only; the famine series ends "
        "in 1619, so it supports **descriptive out-of-sample geography**, not a "
        "famine→Jinshi model.",
        "- CHGIS county points are a historical point layer; joins to modern "
        "1° grids are approximate and must report a coverage rate.",
        "- All sources are read-only. No raw historical table is redistributed "
        "by this script; only the standardized derived CSVs are written.",
        "",
        "## When this inventory would fail",
        "",
        "- Any source file is replaced with a different schema without "
        "re-running this importer.",
        "- CHGIS points are treated as exact county boundaries rather than "
        "point locations.",
        "- Unmatched CBDB PersonIDs are silently dropped from a rate "
        "denominator instead of reported.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print("CBDB addr rows", len(addr), "admin types", admin_counts.to_dict())
    print("person-addr links", len(links), "of", len(person_ids), "Jinshi persons")
    print("population rows", len(pop), "late Jinshi rows", len(late),
          "CHGIS points", len(chgis))
    print(f"wrote 5 derived tables + {DOC}")


if __name__ == "__main__":
    main()
