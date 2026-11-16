# Amendment 3 — coordinate-confidence sensitivity (2026-11-14)

- Generated: 2026-11-14 17:28
- Command: `python scripts/a10_coordinate_confidence.py`
- Pre-registration: `docs/p0_3_preregistration_amendment_3.md` (frozen before this run).
- Data: CBDB 2026-11-07 `ADDR_CODES.c_admin_type` joined via `BIOG_ADDR_DATA` to the 2,841 normalized elite records.

| Quantity | Value |
|---|---:|
| elite records | 2,841 |
| CBDB address-link match rate | 99.2% |
| tier 1 (county) | 2,556 |
| tier 2 (prefecture) | 258 |
| tier 3 (coarse / unknown) | 27 |
| tier 3 share | 1.0% |
| persons with >1 address link | 64.1% |

## Sensitivity run (tiers 1+2 kept, tier 3 dropped)

| Quantity | Restricted | Frozen v0.3 baseline (20-lag diagnostic) |
|---|---:|---:|
| elite rows | 2,814 | 2,841 |
| grids tested | 135 | 135 |
| FDR-significant grids | 48 | 48 |
| median selected lag | 6.5 | 6.5 |

FDR change: **+0** grids (+0.0% of the 20-lag diagnostic).

The FDR count stays within the frozen ±50% band, so the descriptive spatial conclusions are not driven by coarse / unresolvable address records. This is a robustness addition; `docs/a3_main_results.md` headline numbers are unchanged.

## Interpretation limits

- `c_admin_type` is an **administrative-level proxy** for coordinate precision, not a measured geocoding error.
- Persons with several address links take the finest tier; the multi-address share is reported above.
- CHGIS v6 county points (`data/derived/a9_chgis_county_points.csv`) were used only as an independent cross-check in `docs/a10_new_data_replication.md`, not to redefine tiers.

## When this would fail

- CBDB build replaced without re-running `a9_import_new_sources.py`.
- Tier map changed after seeing the coefficient (forbidden).
- Baseline re-used from a different window; both rows above use the same 20-lag pipeline.

## Outputs

| Output | Path |
|---|---|
| tier assignment | `data/derived/a10_coordinate_tiers_summary.csv` (aggregate; person-level assignment kept private) |
| sensitivity summary | `data/derived/a10_coordinate_sensitivity.csv` |

Private inputs; aggregate outputs only. The person-level tier assignment is not
distributed because it joins CBDB `PersonID` to coordinates.
