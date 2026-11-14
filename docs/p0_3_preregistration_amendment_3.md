# P0-3 pre-registration — Amendment 3 (2026-11-14)

**Dated amendment, written BEFORE any analysis using the newly acquired CBDB
SQLite data.** It supersedes the "not decidable" declaration in Amendment 1 §2
for P0-3 step 2 only. §2 (dual proxy), §4 (time perturbation), §5 (failure
criteria) and all route-A results are unchanged.

## 1. What changed

Amendment 1 withdrew the `xy_count` tiering because `xy_count` is the number of
CBDB records sharing a coordinate, not geographic precision, and declared
coordinate confidence "not decidable with the available fields".

New data were subsequently located and standardized by
`scripts/a9_import_new_sources.py`:

- `<private CBDB SQLite>` (CBDB build 2026-11-07),
  tables `ADDR_CODES` (30,160 rows; has `c_admin_type`, `CHGIS_PT_ID`,
  `x_coord`, `y_coord`) and `BIOG_ADDR_DATA` (person→address links; 41,043 links
  for the 27,711 Ming Jinshi PersonIDs).
- `data/derived/a9_cbdb_addr_admin_level.csv`,
  `data/derived/a9_person_addr_link.csv`.

`c_admin_type` provides the administrative **level** of the recorded address
(Xian/xian/County = county; Zhou/Fu/Jun/Dudufu = prefecture; Dao/Lu/Jiedu =
circuit/province-level). This is the missing field. Step 2 can now be run.

## 2. Frozen tier definition (before seeing any result)

For each v0.3 elite-extension record (2,841 normalized 1甲/2甲 Jinshi,
`scripts/corrected_robustness.py: load_jinshi()`), join `PersonID →
BIOG_ADDR_DATA.c_addr_id → ADDR_CODES.c_admin_type`.

| Tier | `c_admin_type` (case-insensitive, trimmed) | Meaning |
|---|---|---|
| 1 — county | `xian`, `county`, `shixiaqu` | address resolved to a county-level unit |
| 2 — prefecture | `zhou`, `fu`, `jun`, `dudufu`, `wei`, `pu`, `shi`, `fengjun`, `qi`, `zhangguansi`, `shouyu qianhusuo` | prefecture / garrison-level unit |
| 3 — coarse or unknown | `dao`, `lu`, `jiedu`, `du`, `state`, `fengjun` variants not above, any other non-null value, **and** records with no CBDB address link | circuit / province level, or unresolvable |

Rules (frozen):

- If a person has several address links, use the **finest** tier present
  (1 beats 2 beats 3) and report the multi-address share.
- `c_addr_type` is **not** used to prefer one address type (no post-hoc choice).
- Missing / unmatched PersonIDs go to tier 3 and are reported, not dropped
  silently from a rate denominator.
- The tier assignment is computed once by `scripts/a10_coordinate_confidence.py`
  and written to `data/derived/a10_coordinate_tiers.csv` before any model run.

## 3. Frozen sensitivity run

- Keep tiers 1 + 2 (drop tier 3), rebuild the v0.3 grid panel with the **same**
  `corrected_robustness.build_panel` / `run_granger` pipeline (no method change),
  and report: grids tested, FDR-significant grids, median selected lag.
- Baseline for comparison: the frozen v0.3 values (48/135 FDR under the 20-lag
  search, median selected lag 6.5 yr) — explicitly a diagnostic, not a headline.
- Report the tier composition, the share dropped, and the CBDB match rate.

## 4. Failure / interpretation criteria (frozen)

- If the CBDB address-link match rate is **< 60%** or tier 3 exceeds **50%** of
  records, declare coverage insufficient and write a method note only (no
  coefficient-style claim).
- If dropping tier 3 changes the FDR count by more than ±50% of the 20-lag
  baseline, report it as a **sensitivity limitation**, not as a corrected
  headline; no re-specification is allowed.
- No new thresholds, no alternative tier maps, no subgroup search after seeing
  the result.

## 5. What will not be done

- No re-tuning of §2 proxies or §4 time shifts.
- No SHAP / ML surrogate (roadmap §4).
- No claim that CBDB `c_admin_type` equals measured coordinate error; it is an
  **administrative-level proxy** for precision.
- No redistribution of the CBDB SQLite file; only derived CSV tiers are written.

## 6. Effect on the headline

If the run succeeds, `docs/a8_freeze_review.md` §6 item 2 and
`docs/b_feasibility_memo.md` are updated by a dated note (not by silently
editing them). The route-A headline numbers in `docs/a3_main_results.md` are
**not** changed by this amendment; this is a robustness addition.
