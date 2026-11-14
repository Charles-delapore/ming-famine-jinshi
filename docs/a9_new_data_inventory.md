# A9 — newly acquired data sources, standardized (2026-11-14)

- Generated: 2026-11-14 17:22
- Command: `python scripts/a9_import_new_sources.py`
- Status: **local sources only**; network download was attempted separately and is recorded in the worklog.

## Inventory

| # | Source | Local path | Rows | Output table | Intended use |
|---|---|---|---:|---|---|
| 1 | CBDB SQLite 2026-11-07 `ADDR_CODES` | `<private raw-data directory>cbdb_sqlite\` | 30,160 | `data/derived/a9_cbdb_addr_admin_level.csv` | coordinate-confidence tiers (admin level + CHGIS point id) |
| 2 | CBDB `BIOG_ADDR_DATA` links | same DB | 41,043 | `data/derived/a9_person_addr_link.csv` | join Ming Jinshi PersonID to an address |
| 3 | Historical urban population | `人口数据\明代.xlsx` | 157 | `data/derived/a9_ming_urban_population.csv` | exogenous population / competition proxy |
| 4 | Late-Ming Jinshi 1627–1644 | `000毕设\008\...\table_general1627_1644.xlsx` | 1,950 | `data/derived/a9_jinshi_1627_1644.csv` | out-of-sample elite-geography replication |
| 5 | CHGIS v6 county points (WGS84) | `ming_general\v6_time_cnty_pts_utf_wgs84.shp` | 10,522 | `data/derived/a9_chgis_county_points.csv` | county-level coordinate benchmark, province→grid mapping (B1 G2) |

## CBDB address administrative types (top 20)

| c_admin_type | rows |
|---|---:|
| Xian | 13,689 |
| Zhou | 3,740 |
| xian | 1,727 |
| Pu | 933 |
| Jiedu | 651 |
| Du | 586 |
| Fu | 574 |
| Wei | 517 |
| Shi | 507 |
| County | 505 |
| Fengjun | 499 |
| Dao | 405 |
| Lu | 325 |
| Dudufu | 278 |
| Qi | 264 |
| Shouyu qianhusuo | 255 |
| State | 247 |
| Shixiaqu | 195 |
| Jun | 184 |
| Zhangguansi | 174 |

CHGIS county point columns: `NAME_PY, NAME_CH, NAME_FT, X_COOR, Y_COOR, PRES_LOC, TYPE_PY, TYPE_CH, LEV_RANK, BEG_YR, BEG_RULE, END_YR, END_RULE, NOTE_ID, OBJ_TYPE, SYS_ID, GEO_SRC, COMPILER, GECOMPLR, CHECKER, ENT_DATE, BEG_CHG_TY, END_CHG_TY, geometry`.
Late-Ming table columns: `Name, NameChn, PersonID, IndexYear, EntryDesc, EntryChn, EntryYear, EntryRank, KinType, KinName, KinChn, AddrName, AddrChn, X, Y, xy_count`.
Population columns: `id, city, alt_names, country, lat, lon, level, year, population, key`.

## Provenance and limitations

- CBDB SQLite is the 2026-11-07 build already present locally; the project's Jinshi export is an older/`入仕查询结果` extract, so a small share of PersonIDs may not match (documented in `docs/data_boundary_audit.md`). No imputation is applied to unmatched ids.
- Population file has no header row in the original workbook; column names above are assigned by position and must be re-checked if the source file is regenerated. Years are sparse city observations, not a continuous annual panel.
- The 1627–1644 table is a Jinshi export only; the famine series ends in 1619, so it supports **descriptive out-of-sample geography**, not a famine→Jinshi model.
- CHGIS county points are a historical point layer; joins to modern 1° grids are approximate and must report a coverage rate.
- All sources are read-only. No raw historical table is redistributed by this script; only the standardized derived CSVs are written.

## When this inventory would fail

- Any source file is replaced with a different schema without re-running this importer.
- CHGIS points are treated as exact county boundaries rather than point locations.
- Unmatched CBDB PersonIDs are silently dropped from a rate denominator instead of reported.

Private inputs; aggregate outputs only.
