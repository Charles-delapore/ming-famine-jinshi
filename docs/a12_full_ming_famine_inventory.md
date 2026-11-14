# A12 — full-Ming famine panel, standardized (2026-11-14)

- Generated: 2026-11-14 17:49
- Command: `python scripts/a12_import_full_ming_famine.py`
- Source: `灾荒数据.zip` in the 000毕设/008 attachment
- **This is an independent famine source** from `merged_data.csv` / `table_generals1521_1619.xlsx` used for v0.3.

| Item | Value |
|---|---:|
| city-year rows | 69,276 |
| years | 1368–1643 (276) |
| cities | 251 |
| cities matched to coordinates | 69,276 / 69,276 (100.0%) |
| 1° grids | 202 |
| non-zero famine level rows | 10,766 |
| calendar entries | 276 |
| level distribution | {0: 58510, 1: 132, 2: 3817, 3: 2905, 4: 3205, 5: 707} |
| rows 1521–1619 (v0.3 window) | 24,849 |
| rows 1620–1643 (out of v0.3 window) | 6,024 |
| rows 1368–1520 (earlier than v0.3) | 38,403 |

## Provenance and limits

- `level` is a **severity grade 0–5** (0 = no recorded famine), not a hazard type. B2's G4 (hazard-typed field) is still not met.
- The panel is balanced (every city × every year); zeros are real 'no recorded event', not missing data.
- City coordinates are point locations; the 1° grid assignment is approximate and its coverage is reported above.
- The calendar table maps 公历/干支/年号 and covers the same 276 years.
- No raw archive file is redistributed; only the two derived CSVs.

Private inputs; aggregate outputs only.
