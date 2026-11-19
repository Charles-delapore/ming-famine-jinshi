"""A10: out-of-sample replication and external-data cross-checks.

Three descriptive analyses on newly acquired data (no new causal model):

1. Late-Ming Jinshi 1627-1644: is the elite geography stable out of sample?
2. External CHGIS Ming city points: cross-check against local CHGIS v6 county
   points and the historical urban-population file.
3. Population-file coverage: how many 1° grids does it touch?

Usage::

    python scripts/a10_new_data_replication.py

Outputs::

    data/derived/a10_late_ming_geography.csv
    data/derived/a10_external_city_crosscheck.csv
    docs/a10_new_data_replication.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_processing.jinshi_rank import rank_class  # noqa: E402

DERIVED = ROOT / "data" / "derived"
PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
LATE = DERIVED / "a9_jinshi_1627_1644.csv"
CITY = DERIVED / "a9_external_ming_city.json"
CHGIS = DERIVED / "a9_chgis_county_points.csv"
POP = DERIVED / "a9_ming_urban_population.csv"
OUT_LATE = DERIVED / "a10_late_ming_geography.csv"
OUT_CITY = DERIVED / "a10_external_city_crosscheck.csv"
DOC = ROOT / "docs" / "a10_new_data_replication.md"


def grid(df: pd.DataFrame, x="X", y="Y") -> pd.DataFrame:
    df = df.copy()
    df["grid_x"] = np.floor(df[x]) + 0.5
    df["grid_y"] = np.floor(df[y]) + 0.5
    return df


def late_ming() -> dict:
    late = pd.read_csv(LATE)
    n_raw = len(late)
    late = late[late["EntryYear"].between(1627, 1644)].copy()
    late["cls"] = late["EntryRank"].map(rank_class)
    late = late[late["cls"].notna() & late["X"].notna() & late["Y"].notna()].copy()
    late = grid(late)
    late_grid = (late.groupby(["grid_x", "grid_y"]).size()
                 .rename("late_jinshi").reset_index())

    panel = pd.read_csv(PANEL)
    v03_grid = (panel.groupby(["grid_x", "grid_y"])["jinshi_count"].sum()
                .rename("v03_jinshi").reset_index())
    m = v03_grid.merge(late_grid, on=["grid_x", "grid_y"], how="outer").fillna(0)
    m.to_csv(OUT_LATE, index=False)

    pear = float(stats.pearsonr(m.v03_jinshi, m.late_jinshi)[0])
    spear = float(stats.spearmanr(m.v03_jinshi, m.late_jinshi)[0])
    top_n = 20
    a = set(m.nlargest(top_n, "v03_jinshi")[["grid_x", "grid_y"]]
            .itertuples(index=False, name=None))
    b = set(m.nlargest(top_n, "late_jinshi")[["grid_x", "grid_y"]]
            .itertuples(index=False, name=None))
    overlap = len(a & b)
    return {
        "late_rows_raw": n_raw,
        "late_rows_1627_1644_parsed": int(len(late)),
        "late_grids": int(len(late_grid)),
        "v03_grids": int(len(v03_grid)),
        "union_grids": int(len(m)),
        "pearson_r": pear, "spearman_r": spear,
        "top20_overlap": overlap,
        "top20_jaccard": overlap / (2 * top_n - overlap) if (2 * top_n - overlap) else 0.0,
    }


def external_crosscheck() -> tuple[pd.DataFrame, dict]:
    j = json.loads(CITY.read_text(encoding="utf-8"))
    feats = j["features"]
    city = pd.DataFrame([
        {
            "name": f["properties"].get("NAME", ""),
            "lon": float(f["geometry"]["coordinates"][0]),
            "lat": float(f["geometry"]["coordinates"][1]),
        }
        for f in feats
    ])
    chgis = pd.read_csv(CHGIS).dropna(subset=["X_COOR", "Y_COOR"]).reset_index(drop=True)
    tree = cKDTree(chgis[["X_COOR", "Y_COOR"]].to_numpy())
    dist, idx = tree.query(city[["lon", "lat"]].to_numpy())
    city["nearest_chgis_name"] = chgis["NAME_CH"].iloc[idx].to_numpy()
    city["nearest_chgis_type"] = chgis["TYPE_CH"].iloc[idx].to_numpy()
    city["dist_deg"] = dist

    pop = pd.read_csv(POP)
    pop_pts = pop[["lon", "lat"]].dropna()
    tree2 = cKDTree(pop_pts.to_numpy())
    d2, _ = tree2.query(city[["lon", "lat"]].to_numpy())
    city["dist_to_pop_city_deg"] = d2

    city.to_csv(OUT_CITY, index=False)
    info = {
        "external_points": int(len(city)),
        "lon_range": (float(city.lon.min()), float(city.lon.max())),
        "lat_range": (float(city.lat.min()), float(city.lat.max())),
        "median_dist_chgis": float(np.median(dist)),
        "share_within_0_25deg": float((dist < 0.25).mean()),
        "share_within_0_5deg": float((dist < 0.5).mean()),
        "share_within_1deg": float((dist < 1.0).mean()),
        "median_dist_pop": float(np.median(d2)),
        "chgis_county_points": int(len(chgis)),
        "pop_rows": int(len(pop_pts)),
    }
    return city, info


def population_coverage() -> dict:
    pop = pd.read_csv(POP)
    pop = pop[pop["year"].between(1400, 1620)].copy()
    pop = grid(pop, x="lon", y="lat")
    grids = pop[["grid_x", "grid_y"]].drop_duplicates()
    panel = pd.read_csv(PANEL)
    pgrids = set(panel[["grid_x", "grid_y"]].drop_duplicates()
                 .itertuples(index=False, name=None))
    overlap = sum(1 for g in grids.itertuples(index=False, name=None) if g in pgrids)
    return {
        "pop_rows_1400_1620": int(len(pop)),
        "pop_unique_cities": int(pop["city"].nunique()),
        "pop_grids": int(len(grids)),
        "panel_grids": len(pgrids),
        "overlap_grids": overlap,
        "overlap_pct": overlap / len(pgrids) * 100 if pgrids else 0.0,
    }


def main() -> None:
    for p in (LATE, CITY, CHGIS, POP, PANEL):
        if not p.exists():
            raise SystemExit(f"missing input: {p}")
    lm = late_ming()
    city, ex = external_crosscheck()
    pc = population_coverage()

    city_table = [
        "| External city | lon | lat | nearest CHGIS point | type | dist (°) |",
        "|---|---:|---:|---|---|---:|",
    ] + [
        f"| {r.name} | {r.lon:.2f} | {r.lat:.2f} | {r.nearest_chgis_name} | "
        f"{r.nearest_chgis_type} | {r.dist_deg:.3f} |"
        for r in city.itertuples(index=False)
    ]
    lines = [
        "# A10 — new-data replication and external cross-checks (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a10_new_data_replication.py`",
        "- Sources: `docs/a9_new_data_inventory.md` + externally downloaded "
        "`a9_external_ming_city.json` (GitHub `ChenSK23/GIS`, contents API).",
        "- **Descriptive only**: no new causal model, no new control variable, "
        "no headline change.",
        "",
        "## 1. Late-Ming out-of-sample elite geography (1627–1644)",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| rows in late table | {lm['late_rows_raw']:,} |",
        f"| rows 1627–1644 with parsed rank + coordinates | {lm['late_rows_1627_1644_parsed']:,} |",
        f"| late grids | {lm['late_grids']} |",
        f"| v0.3 panel grids | {lm['v03_grids']} |",
        f"| union grids | {lm['union_grids']} |",
        f"| Pearson r (grid Jinshi counts) | {lm['pearson_r']:.3f} |",
        f"| Spearman r | {lm['spearman_r']:.3f} |",
        f"| top-20 grid overlap | {lm['top20_overlap']}/20 |",
        f"| top-20 Jaccard | {lm['top20_jaccard']:.3f} |",
        "",
        "The famine series ends in 1619, so this is **not** a famine→Jinshi "
        "test. It checks whether the *spatial inequality* finding (Jiangnan "
        "core, partial overlap with famine belts) persists after the study "
        "window. Raw `EntryYear` extends to 1871, so the 1627–1644 filter is "
        "applied explicitly.",
        "",
        "## 2. External CHGIS Ming city points — cross-check",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| external points | {ex['external_points']} |",
        f"| longitude range | {ex['lon_range'][0]:.2f} – {ex['lon_range'][1]:.2f} |",
        f"| latitude range | {ex['lat_range'][0]:.2f} – {ex['lat_range'][1]:.2f} |",
        f"| local CHGIS v6 county points | {ex['chgis_county_points']:,} |",
        f"| median distance to nearest CHGIS point | {ex['median_dist_chgis']:.3f}° |",
        f"| share within 0.25° / 0.5° / 1° | "
        f"{ex['share_within_0_25deg']*100:.0f}% / {ex['share_within_0_5deg']*100:.0f}% / {ex['share_within_1deg']*100:.0f}% |",
        f"| median distance to nearest population city | {ex['median_dist_pop']:.3f}° |",
        "",
        *city_table,
        "",
        "Caveat: only 27 points, concentrated in the far north-east; this is a "
        "**small external reference set**, not a national city sample. It is "
        "used to verify coordinate plausibility, not to estimate coverage.",
        "",
        "## 3. Population-file coverage (descriptive only)",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| rows 1400–1620 | {pc['pop_rows_1400_1620']} |",
        f"| unique cities | {pc['pop_unique_cities']} |",
        f"| 1° grids touched | {pc['pop_grids']} |",
        f"| panel grids | {pc['panel_grids']} |",
        f"| overlap grids | {pc['overlap_grids']} ({pc['overlap_pct']:.1f}%) |",
        "",
        "The population file is a sparse city time series, not a continuous "
        "annual panel. No dose-response or competition model is fitted here "
        "(roadmap §4: no new control variable without pre-registration); it is "
        "recorded as a candidate exogenous proxy for a future dated Go decision.",
        "",
        "## When this would fail",
        "",
        "- Late-Ming table re-exported with different year coverage or rank codes.",
        "- External GeoJSON replaced without re-running this script.",
        "- CHGIS point layer swapped to a different CRS; distances are in "
        "degrees and assume WGS84.",
        "- Any of these descriptive numbers is quoted as a causal result.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| late-Ming grid table | `data/derived/a10_late_ming_geography.csv` |",
        "| external city cross-check | `data/derived/a10_external_city_crosscheck.csv` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print("late Ming:", lm)
    print("external:", ex)
    print("population:", pc)
    print(f"wrote {OUT_LATE}, {OUT_CITY}, {DOC}")


if __name__ == "__main__":
    main()
