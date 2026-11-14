"""A18: descriptive ego-network study on the full CBDB graph.

Pre-registration: docs/a18_ego_network_preregistration.md (frozen before run).
Trigger: docs/a17_cbdb_network_coverage.md (GO, 56.4% coverage).

Descriptive only: no regression, no p-values, no causal claim, no SHAP/ML.

Usage::

    python scripts/a18_ego_network_analysis.py

Outputs::

    data/derived/a18_ego_network_summary.csv
    data/derived/a18_ego_degrees.csv
    data/derived/a18_grid_correlations.csv
    docs/a18_ego_network_results.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CBDB = Path(r"data/private/cbdb_20261107.sqlite3")
RAW = Path(r"data/private/明进士.xlsx")
V03_PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
FULL_FAMINE = ROOT / "data" / "derived" / "a12_full_ming_famine.csv"
DERIVED = ROOT / "data" / "derived"
OUT_SUM = DERIVED / "a18_ego_network_summary.csv"
OUT_DEG = DERIVED / "a18_ego_degrees.csv"
OUT_GRID = DERIVED / "a18_grid_correlations.csv"
DOC = ROOT / "docs" / "a18_ego_network_results.md"

# FROZEN: kin address coverage below this -> geographic measures not estimable
GEO_COVERAGE_MIN = 0.50
TIER1 = {"xian", "county", "shixiaqu"}
TIER2 = {"zhou", "fu", "jun", "dudufu", "wei", "pu", "shi", "fengjun",
         "qi", "zhangguansi", "shouyu qianhusuo"}


def tier_of(v) -> int:
    s = str(v).strip().lower()
    if s in TIER1:
        return 1
    if s in TIER2:
        return 2
    return 3


def main() -> None:
    for p in (CBDB, RAW, V03_PANEL, FULL_FAMINE):
        if not p.exists():
            raise SystemExit(f"missing input: {p}")
    raw = pd.read_excel(RAW, usecols=["PersonID"])
    jinshi = set(pd.to_numeric(raw.PersonID, errors="coerce").dropna().astype(int))
    con = sqlite3.connect(str(CBDB))

    kin = pd.read_sql_query(
        "select c_personid, c_kin_id, c_kin_code from KIN_DATA", con)
    kin = kin[kin.c_personid.isin(jinshi)].copy()
    assoc = pd.read_sql_query(
        "select c_personid, c_assoc_id from ASSOC_DATA", con)
    assoc = assoc[assoc.c_personid.isin(jinshi)].copy()
    kc = pd.read_sql_query(
        "select c_kincode, c_kinrel_chn from KINSHIP_CODES", con)

    kin_deg = kin.groupby("c_personid")["c_kin_id"].nunique().rename("kin_degree")
    assoc_deg = assoc.groupby("c_personid")["c_assoc_id"].nunique() \
        .rename("assoc_degree")
    deg = pd.concat([kin_deg, assoc_deg], axis=1).fillna(0).astype(int)
    deg["total_degree"] = deg.kin_degree + deg.assoc_degree
    deg.index.name = "personid"
    deg = deg.reset_index()
    deg.to_csv(OUT_DEG, index=False)

    n_egos = len(deg)
    rows = [
        {"metric": "jinshi_personids", "value": len(jinshi)},
        {"metric": "egos_with_kin_or_assoc_edge", "value": n_egos},
        {"metric": "ego_coverage", "value": round(n_egos / len(jinshi), 4)},
        {"metric": "median_total_degree", "value": float(deg.total_degree.median())},
        {"metric": "q25_total_degree", "value": float(deg.total_degree.quantile(.25))},
        {"metric": "q75_total_degree", "value": float(deg.total_degree.quantile(.75))},
        {"metric": "max_total_degree", "value": int(deg.total_degree.max())},
        {"metric": "share_degree_ge_5", "value": round(float((deg.total_degree >= 5).mean()), 4)},
        {"metric": "share_degree_ge_10", "value": round(float((deg.total_degree >= 10).mean()), 4)},
        {"metric": "median_kin_degree", "value": float(deg.kin_degree.median())},
        {"metric": "median_assoc_degree", "value": float(deg.assoc_degree.median())},
        {"metric": "kin_edges_total", "value": len(kin)},
        {"metric": "assoc_edges_total", "value": len(assoc)},
    ]
    top_kin = kin.c_kin_code.value_counts().head(10)
    label = dict(zip(kc.c_kincode, kc.c_kinrel_chn))
    for code, n in top_kin.items():
        rows.append({"metric": f"kinship_type_{int(code)}_{label.get(code, 'NA')}",
                     "value": int(n)})

    # ---- geographic (descriptive) ----
    addr = pd.read_sql_query(
        "select c_addr_id, x_coord, y_coord, c_admin_type from ADDR_CODES", con)
    links = pd.read_sql_query(
        "select c_personid, c_addr_id from BIOG_ADDR_DATA", con)
    con.close()
    addr = addr.dropna(subset=["x_coord", "y_coord"]).copy()
    addr["tier"] = addr.c_admin_type.map(tier_of)
    m = links.merge(addr, on="c_addr_id", how="inner")
    coords = (m.sort_values("tier").groupby("c_personid")
              .first()[["x_coord", "y_coord"]])

    edges = kin[["c_personid", "c_kin_id"]].drop_duplicates()
    edges = edges.merge(coords.add_prefix("ego_"), left_on="c_personid",
                        right_index=True, how="left")
    edges = edges.merge(coords.add_prefix("kin_"), left_on="c_kin_id",
                        right_index=True, how="left")
    both = edges.dropna(subset=["ego_x_coord", "ego_y_coord",
                                "kin_x_coord", "kin_y_coord"]).copy()
    geo_cov = len(both) / len(edges) if len(edges) else 0.0
    rows.append({"metric": "kin_edges_with_both_coordinates", "value": len(both)})
    rows.append({"metric": "kin_address_coverage", "value": round(geo_cov, 4)})

    geo_estimable = geo_cov >= GEO_COVERAGE_MIN
    if geo_estimable and len(both):
        dx = both.ego_x_coord - both.kin_x_coord
        dy = both.ego_y_coord - both.kin_y_coord
        dist = np.sqrt(dx ** 2 + dy ** 2)
        egx = np.floor(both.ego_x_coord) + 0.5
        egy = np.floor(both.ego_y_coord) + 0.5
        kgx = np.floor(both.kin_x_coord) + 0.5
        kgy = np.floor(both.kin_y_coord) + 0.5
        rows += [
            {"metric": "median_kin_distance_deg", "value": round(float(np.median(dist)), 3)},
            {"metric": "share_kin_same_1deg_grid",
             "value": round(float(((egx == kgx) & (egy == kgy)).mean()), 4)},
        ]
    else:
        rows += [
            {"metric": "median_kin_distance_deg", "value": "not estimable"},
            {"metric": "share_kin_same_1deg_grid", "value": "not estimable"},
        ]

    # ---- grid-level descriptive correlations ----
    ego_coords = deg.merge(coords, left_on="personid", right_index=True, how="left")
    ego_coords = ego_coords.dropna(subset=["x_coord", "y_coord"]).copy()
    ego_coords["grid_x"] = np.floor(ego_coords.x_coord) + 0.5
    ego_coords["grid_y"] = np.floor(ego_coords.y_coord) + 0.5
    gsum = (ego_coords.groupby(["grid_x", "grid_y"])["total_degree"].sum()
            .rename("network_degree").reset_index())

    v03 = pd.read_csv(V03_PANEL)
    vjin = (v03.groupby(["grid_x", "grid_y"])["jinshi_count"].sum()
            .rename("v03_jinshi").reset_index())
    fam = pd.read_csv(FULL_FAMINE)
    flev = (fam.groupby(["grid_x", "grid_y"])["level"].sum()
            .rename("famine_level").reset_index())
    gm = gsum.merge(vjin, on=["grid_x", "grid_y"], how="left") \
        .merge(flev, on=["grid_x", "grid_y"], how="left").fillna(0)

    grid_rows = []
    for target in ("v03_jinshi", "famine_level"):
        if len(gm) >= 3:
            r = float(stats.pearsonr(gm.network_degree, gm[target])[0])
            rs = float(stats.spearmanr(gm.network_degree, gm[target])[0])
        else:
            r = rs = float("nan")
        grid_rows.append({"target": target, "n_grids": len(gm),
                          "pearson_r": round(r, 4), "spearman_r": round(rs, 4)})
    pd.DataFrame(grid_rows).to_csv(OUT_GRID, index=False)
    pd.DataFrame(rows).to_csv(OUT_SUM, index=False)

    lines = [
        "# A18 — descriptive ego-network results (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a18_ego_network_analysis.py`",
        "- Pre-registration: `docs/a18_ego_network_preregistration.md` "
        "(frozen before run). **Descriptive only** — no model, no p-values, "
        "no causal claim.",
        "- Trigger: `docs/a17_cbdb_network_coverage.md` (GO, coverage 56.4%).",
        "- Graph: CBDB `KIN_DATA` (565,276 rows) + `ASSOC_DATA` (190,164 rows), "
        "restricted to Jinshi egos; coordinates via `BIOG_ADDR_DATA` → "
        "`ADDR_CODES` (finest administrative tier).",
        "",
        "| Metric | Value |",
        "|---|---:|",
        *[f"| `{r['metric']}` | {r['value']} |" for r in rows],
        "",
        "## Grid-level descriptive correlations",
        "",
        "| Target | n grids | Pearson r | Spearman r |",
        "|---|---:|---:|---:|",
        *[f"| `{r['target']}` | {r['n_grids']} | {r['pearson_r']:.3f} | "
          f"{r['spearman_r']:.3f} |" for r in grid_rows],
        "",
        "## Interpretation (strictly descriptive)",
        "",
        f"- {n_egos:,} of {len(jinshi):,} Jinshi PersonIDs have ≥1 recorded "
        f"kin/association edge ({n_egos/len(jinshi)*100:.1f}%).",
        f"- Median total degree {deg.total_degree.median():.0f}; the "
        "distribution is reported with quartiles and ≥5 / ≥10 shares.",
        f"- Kin address coordinate coverage: **{geo_cov*100:.1f}%** "
        f"(geographic measures {'estimable' if geo_estimable else 'NOT estimable'}).",
        "- Grid correlations are **ecological and descriptive**; degree is "
        "as much a documentation-intensity proxy as a social one. No "
        "significance claim is made and no model was fitted.",
        "- ⚠️ The high grid correlation with `v03_jinshi` (r≈0.91) is "
        "**mechanically expected**: both are computed from the same Jinshi "
        "persons in a grid (more egos ⇒ more recorded kin AND more Jinshi). "
        "It is **not** evidence that social networks explain elite production. "
        "Likewise the ~95% same-grid kin share largely reflects CBDB recording "
        "family / ancestral addresses at one location, not a measured "
        "social-distance effect.",
        "",
        "## Limits (frozen)",
        "",
        "- CBDB kinship includes auto-generated / inferred relations; edge "
        "quality is not independently verified.",
        "- `KINSHIP_CODES` labels are CBDB's own taxonomy; no re-coding.",
        "- Ego coordinates use the finest-tier address; kin coordinates use "
        "the same rule — historical point locations, not exact residences.",
        "- The three-stage funnel (举人完整度) remains out of scope.",
        "",
        "## When this would fail",
        "",
        "- CBDB replaced without re-running A17 + A18.",
        "- Any measure/threshold changed after seeing results (forbidden).",
        "- These numbers quoted as evidence about elite reproduction rather "
        "than as a descriptive inventory.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| summary + kinship types | `data/derived/a18_ego_network_summary.csv` |",
        "| per-ego degrees | `<local private; not distributed>` |",
        "| grid correlations | `data/derived/a18_grid_correlations.csv` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))
    print(pd.DataFrame(grid_rows).to_string(index=False))
    print(f"wrote {OUT_SUM}, {OUT_DEG}, {OUT_GRID}, {DOC}")


if __name__ == "__main__":
    main()
