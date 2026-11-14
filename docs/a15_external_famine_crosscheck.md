# A15 — external famine-event cross-check (2026-11-14)

- Generated: 2026-11-14 17:58
- Command: `python scripts/a15_external_famine_crosscheck.py`
- External: `Fengx06/Data-of-Famine-Cannibalism-in-Ancient-China` (MIT), `result/明清时期灾荒食人年表_地点匹配明细.csv`, obtained via GitHub contents API; local copies `a15_external_famine_*.csv`.
- Local comparator: `<local private input; not distributed>` (灾荒数据.zip / `table_level.json`, 1368–1643, 251 cities).
- **This is an extreme-event chronology, not a hazard-typed table.** B2 gate G4 (hazard field ≥80%) is still **not met**; this is a descriptive external-validity check only.

External columns: `seq, year_ce, year_era, province, city, county, ancient_name, source, record, matched_level, matched_province, matched_province_code, matched_prefecture, matched_prefecture_code, matched_county, matched_county_code, lng_wgs84, lat_wgs84`.

| Metric | Value |
|---|---:|
| `external_rows_raw` | 1856 |
| `external_rows_1368_1643_with_coords` | 1361 |
| `external_years_covered` | 133 |
| `external_event_years` | 133 |
| `local_panel_years` | 276 |
| `pearson_r_total_level_vs_events` | 0.5826 |
| `spearman_r_total_level_vs_events` | 0.6639 |
| `pearson_r_nz_cities_vs_events` | 0.4606 |
| `event_grid_years` | 772 |
| `mean_local_level_at_event_cells` | 3.4741 |
| `share_events_with_local_level_gt0` | 0.6179 |
| `matched_grid_years` | 477 |

## Interpretation

- Annual famine severity (sum of city levels) vs external extreme events: Pearson r = **0.583**, Spearman = **0.664**; number of affected cities vs events: r = **0.461**.
A positive correlation means the independent extreme-event chronology tracks the local famine panel's temporal pattern — supporting the external validity of the famine series.
- Event grid-years with a matching local famine level > 0: **61.8%** (477/772); grid assignment is approximate (1°).

## Limits

- Cannibalism records are an extreme, possibly sensational subset of famine events; they are not a random sample of famines.
- The external chronology covers Ming **and Qing**; only 1368–1643 rows are used here and the excluded count is implicit in the raw-vs-filtered rows above.
- Ancient place names were matched by the external authors; residual geocoding error is not audited here.
- Correlations are ecological (annual aggregates), not individual-level.
- Licence: MIT per repository LICENSE; the files are used read-only for a cross-check.

## When this would fail

- External file replaced without re-running the download + this script.
- The correlation is quoted as evidence about famine→Jinshi causality.
- B2 G4 is claimed satisfied on the basis of this file (it is not).

Machine-readable: `data/derived/a15_external_famine_crosscheck.csv`.

Private inputs; aggregate outputs only.
