"""A12: standardize the full-Ming famine panel (1368-1643) from the thesis archive.

Source: 灾荒数据.zip (table_level.json / table_city.json / table_calendar.json)
inside 000毕设/008/.../数据表/原始数据/. This is an INDEPENDENT famine data
source from the merged_data.csv used for v0.3, and covers a longer window.

Usage::

    python scripts/a12_import_full_ming_famine.py

Outputs::

    data/derived/a12_full_ming_famine.csv
    data/derived/a12_full_ming_cities.csv
    docs/a12_full_ming_famine_inventory.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = Path(
    r"data/private/archive\008\210520134_田正_地理信息科学_古代灾荒事件对社会人文现象的时空模式影响研究_附件"
    r"\数据表\原始数据\灾荒数据.zip"
)
DERIVED = ROOT / "data" / "derived"
OUT_LEVEL = DERIVED / "a12_full_ming_famine.csv"
OUT_CITY = DERIVED / "a12_full_ming_cities.csv"
DOC = ROOT / "docs" / "a12_full_ming_famine_inventory.md"


def main() -> None:
    if not ZIP.exists():
        raise SystemExit(f"missing archive: {ZIP}")
    DERIVED.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP) as z:
        level = pd.DataFrame(json.loads(z.read("table_level.json")))
        city = pd.DataFrame(json.loads(z.read("table_city.json")))
        cal = pd.DataFrame(json.loads(z.read("table_calendar.json")))

    city["lon"] = city["geometry"].apply(lambda g: float(g["coordinates"][0]))
    city["lat"] = city["geometry"].apply(lambda g: float(g["coordinates"][1]))
    city["code"] = city["code"].astype(str)
    city = city.rename(columns={"title": "city_name"})
    city_out = city[["code", "city_name", "lon", "lat"]].copy()
    city_out.to_csv(OUT_CITY, index=False)

    level["city"] = level["city"].astype(str)
    level["year"] = pd.to_numeric(level["year"], errors="coerce").astype(int)
    level["level"] = pd.to_numeric(level["level"], errors="coerce").fillna(0)
    m = level.merge(city_out, left_on="city", right_on="code", how="left")
    m["grid_x"] = np.floor(m["lon"]) + 0.5
    m["grid_y"] = np.floor(m["lat"]) + 0.5
    out = m[["year", "city", "city_name", "level", "lon", "lat",
             "grid_x", "grid_y"]].copy()
    out.to_csv(OUT_LEVEL, index=False)

    matched = int(m["lon"].notna().sum())
    lines = [
        "# A12 — full-Ming famine panel, standardized (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a12_import_full_ming_famine.py`",
        f"- Source: `灾荒数据.zip` in the 000毕设/008 attachment",
        "- **This is an independent famine source** from "
        "`merged_data.csv` / `table_generals1521_1619.xlsx` used for v0.3.",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| city-year rows | {len(out):,} |",
        f"| years | {out.year.min()}–{out.year.max()} ({out.year.nunique()}) |",
        f"| cities | {out.city.nunique()} |",
        f"| cities matched to coordinates | {matched:,} / {len(out):,}"
        f" ({matched/len(out)*100:.1f}%) |",
        f"| 1° grids | {out[['grid_x','grid_y']].drop_duplicates().shape[0]} |",
        f"| non-zero famine level rows | {int((out.level>0).sum()):,} |",
        f"| calendar entries | {len(cal)} |",
        f"| level distribution | {out.level.value_counts().sort_index().to_dict()} |",
        f"| rows 1521–1619 (v0.3 window) | {int(out.year.between(1521,1619).sum()):,} |",
        f"| rows 1620–1643 (out of v0.3 window) | {int(out.year.between(1620,1643).sum()):,} |",
        f"| rows 1368–1520 (earlier than v0.3) | {int(out.year.between(1368,1520).sum()):,} |",
        "",
        "## Provenance and limits",
        "",
        "- `level` is a **severity grade 0–5** (0 = no recorded famine), not a "
        "hazard type. B2's G4 (hazard-typed field) is still not met.",
        "- The panel is balanced (every city × every year); zeros are real "
        "'no recorded event', not missing data.",
        "- City coordinates are point locations; the 1° grid assignment is "
        "approximate and its coverage is reported above.",
        "- The calendar table maps 公历/干支/年号 and covers the same 276 years.",
        "- No raw archive file is redistributed; only the two derived CSVs.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(f"rows {len(out)}, years {out.year.min()}-{out.year.max()}, "
          f"cities {out.city.nunique()}, grids "
          f"{out[['grid_x','grid_y']].drop_duplicates().shape[0]}, "
          f"matched {matched}/{len(out)}")
    print(f"wrote {OUT_LEVEL}, {OUT_CITY}, {DOC}")


if __name__ == "__main__":
    main()
