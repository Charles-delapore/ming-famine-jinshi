"""A15: cross-check an independently downloaded famine-event chronology.

External source (MIT): Fengx06/Data-of-Famine-Cannibalism-in-Ancient-China,
result/明清时期灾荒食人年表_地点匹配明细.csv, downloaded via GitHub contents
API. This is a chronology of EXTREME famine events (cannibalism records) with
year, province/city/county and WGS84 coordinates — NOT a general hazard-type
table, so B2's G4 remains unmet.

Cross-check against the local full-Ming panel
(`<local private input; not distributed>`, from 灾荒数据.zip).

Usage::

    python scripts/a15_external_famine_crosscheck.py

Outputs::

    data/derived/a15_external_famine_crosscheck.csv
    docs/a15_external_famine_crosscheck.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CHRON = ROOT / "data" / "derived" / "a15_external_famine_chronology.csv"
SUMMARY = ROOT / "data" / "derived" / "a15_external_famine_summary.csv"
LEVEL = ROOT / "data" / "derived" / "a12_full_ming_famine.csv"
OUT = ROOT / "data" / "derived" / "a15_external_famine_crosscheck.csv"
DOC = ROOT / "docs" / "a15_external_famine_crosscheck.md"


def main() -> None:
    for p in (CHRON, LEVEL):
        if not p.exists():
            raise SystemExit(f"missing input: {p}")
    d = pd.read_csv(CHRON, encoding="utf-8-sig")
    cols = list(d.columns)
    lon_col = next((c for c in cols if "lng" in c.lower() or "lon" in c.lower()), None)
    lat_col = next((c for c in cols if "lat" in c.lower()), None)
    d["year_ce"] = pd.to_numeric(d.get("year_ce"), errors="coerce")
    n_raw = len(d)
    d = d[d["year_ce"].between(1368, 1643)].copy()
    d["year_ce"] = d["year_ce"].astype(int)
    if lon_col and lat_col:
        d[lon_col] = pd.to_numeric(d[lon_col], errors="coerce")
        d[lat_col] = pd.to_numeric(d[lat_col], errors="coerce")
        d = d.dropna(subset=[lon_col, lat_col]).copy()
        d["grid_x"] = np.floor(d[lon_col]) + 0.5
        d["grid_y"] = np.floor(d[lat_col]) + 0.5

    f = pd.read_csv(LEVEL)
    f["year"] = f["year"].astype(int)
    fam_year = f.groupby("year").agg(
        total_level=("level", "sum"),
        nz_cities=("level", lambda s: int((s > 0).sum())),
    ).reset_index()
    ext_year = d.groupby("year_ce").size().rename("extreme_events").reset_index()
    ext_year = ext_year.rename(columns={"year_ce": "year"})
    m = fam_year.merge(ext_year, on="year", how="left")
    m["extreme_events"] = m["extreme_events"].fillna(0).astype(int)

    r_level = float(stats.pearsonr(m.total_level, m.extreme_events)[0])
    rs_level = float(stats.spearmanr(m.total_level, m.extreme_events)[0])
    r_city = float(stats.pearsonr(m.nz_cities, m.extreme_events)[0])

    # Spatial check: event grid-years vs the local panel level in that grid-year.
    spatial = {}
    if "grid_x" in d.columns:
        fgrid = f.groupby(["year", "grid_x", "grid_y"])["level"].sum() \
            .rename("local_level").reset_index()
        ev = d.groupby(["year_ce", "grid_x", "grid_y"]).size() \
            .rename("events").reset_index().rename(columns={"year_ce": "year"})
        sm = ev.merge(fgrid, on=["year", "grid_x", "grid_y"], how="left")
        sm["local_level"] = sm["local_level"].fillna(0)
        spatial = {
            "event_grid_years": int(len(sm)),
            "mean_local_level_at_event_cells": float(sm.local_level.mean()),
            "share_events_with_local_level_gt0": float((sm.local_level > 0).mean()),
            "matched_grid_years": int((sm.local_level > 0).sum()),
        }

    rows = [
        {"metric": "external_rows_raw", "value": n_raw},
        {"metric": "external_rows_1368_1643_with_coords", "value": len(d)},
        {"metric": "external_years_covered", "value": int(d.year_ce.nunique())},
        {"metric": "external_event_years", "value": int((m.extreme_events > 0).sum())},
        {"metric": "local_panel_years", "value": int(len(m))},
        {"metric": "pearson_r_total_level_vs_events", "value": round(r_level, 4)},
        {"metric": "spearman_r_total_level_vs_events", "value": round(rs_level, 4)},
        {"metric": "pearson_r_nz_cities_vs_events", "value": round(r_city, 4)},
    ] + [{"metric": k, "value": (round(v, 4) if isinstance(v, float) else v)}
         for k, v in spatial.items()]
    res = pd.DataFrame(rows)
    res.to_csv(OUT, index=False)

    lines = [
        "# A15 — external famine-event cross-check (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a15_external_famine_crosscheck.py`",
        "- External: `Fengx06/Data-of-Famine-Cannibalism-in-Ancient-China` "
        "(MIT), `result/明清时期灾荒食人年表_地点匹配明细.csv`, obtained via "
        "GitHub contents API; local copies `a15_external_famine_*.csv`.",
        "- Local comparator: `<local private input; not distributed>` "
        "(灾荒数据.zip / `table_level.json`, 1368–1643, 251 cities).",
        "- **This is an extreme-event chronology, not a hazard-typed table.** "
        "B2 gate G4 (hazard field ≥80%) is still **not met**; this is a "
        "descriptive external-validity check only.",
        "",
        f"External columns: `{', '.join(cols[:18])}`.",
        "",
        "| Metric | Value |",
        "|---|---:|",
        *[f"| `{r['metric']}` | {r['value']} |" for r in rows],
        "",
        "## Interpretation",
        "",
        f"- Annual famine severity (sum of city levels) vs external extreme "
        f"events: Pearson r = **{r_level:.3f}**, Spearman = **{rs_level:.3f}**; "
        f"number of affected cities vs events: r = **{r_city:.3f}**.",
    ]
    if r_level > 0.3:
        lines += [
            "A positive correlation means the independent extreme-event "
            "chronology tracks the local famine panel's temporal pattern — "
            "supporting the external validity of the famine series.",
        ]
    elif r_level > 0:
        lines += [
            "The correlation is positive but weak; the two series measure "
            "different things (all recorded famine grades vs extreme events), "
            "so this is a plausibility check, not a validation of magnitudes.",
        ]
    else:
        lines += [
            "No positive association. This is recorded as-is: either the two "
            "sources cover different regions/definitions, or the extreme-event "
            "chronology is too sparse. No post-hoc reconciliation is attempted.",
        ]
    if spatial:
        lines += [
            f"- Event grid-years with a matching local famine level > 0: "
            f"**{spatial['share_events_with_local_level_gt0']*100:.1f}%** "
            f"({spatial['matched_grid_years']}/{spatial['event_grid_years']}); "
            "grid assignment is approximate (1°).",
        ]
    lines += [
        "",
        "## Limits",
        "",
        "- Cannibalism records are an extreme, possibly sensational subset of "
        "famine events; they are not a random sample of famines.",
        "- The external chronology covers Ming **and Qing**; only 1368–1643 "
        "rows are used here and the excluded count is implicit in the raw-vs-"
        "filtered rows above.",
        "- Ancient place names were matched by the external authors; residual "
        "geocoding error is not audited here.",
        "- Correlations are ecological (annual aggregates), not individual-level.",
        "- Licence: MIT per repository LICENSE; the files are used read-only "
        "for a cross-check.",
        "",
        "## When this would fail",
        "",
        "- External file replaced without re-running the download + this script.",
        "- The correlation is quoted as evidence about famine→Jinshi causality.",
        "- B2 G4 is claimed satisfied on the basis of this file (it is not).",
        "",
        "Machine-readable: `data/derived/a15_external_famine_crosscheck.csv`.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(res.to_string(index=False))
    print(f"wrote {OUT}, {DOC}")


if __name__ == "__main__":
    main()
