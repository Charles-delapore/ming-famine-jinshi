# A11 — dated addendum to the A8 freeze (2026-11-14)

**User instruction**: attempt to acquire more relevant data; if acquired,
bring it into the system for continuous improvement and analysis.
**Constraint**: private inputs, aggregate outputs.

Route A remains **frozen** (`7ee12d9`). This addendum does **not** silently edit
`docs/a8_freeze_review.md` or `docs/a3_main_results.md`; it records what new
data were obtained and what the resulting analyses showed, with dates.

---

## 1. Data-acquisition attempt (network)

| Step | Result |
|---|---|
| `webfetch https://raw.githubusercontent.com/.../2014_usa_states.csv` | **failed** — Transport error |
| `webfetch https://api.github.com/repos/plotly/datasets` | **succeeded** → network available, `raw.githubusercontent.com` blocked |
| GitHub repository search (chgis / cbdb / china historical data) | 87 hits; relevant: `cga-harvard/chgis.github.io` (official, site only) and `ChenSK23/GIS` ("GeoJSON boundary and point data exported from ArcGIS: historical China (CHGIS)") |
| `webfetch raw.../ming_city.json` and `README.md` | **failed** (raw domain) |
| GitHub **contents API** via shell `urllib` | **succeeded** → 3 files downloaded and saved locally |

Downloaded (via `https://api.github.com/repos/ChenSK23/GIS/contents/<file>?ref=main`,
base64-decoded, saved under `data/derived/`):

| File | Bytes | Content |
|---|---:|---|
| `a9_external_ming_city.json` | 3,687 | GeoJSON FeatureCollection, **27 Ming city points** with Chinese `NAME` and lon/lat |
| `a9_external_ming_mian.json` | 113,836 | `GeometryCollection` with **4 geometries** (3 Polygon + 1 MultiPolygon), no attribute properties — a coarse Ming territory outline, **not** province boundaries |
| `a9_external_source_README.md` | 6,811 | repository data inventory and provenance |

No database, quota table or hazard-typed Ming table was downloadable from this
source; B1/B2 still need external suppliers. No licence claim is made for the
downloaded files; they are used only as an independent coordinate cross-check.

## 2. Local data newly brought into the table system

`scripts/a9_import_new_sources.py` standardized five previously unused local
sources into `data/derived/` (see `docs/a9_new_data_inventory.md`):

| Source | Rows | Output |
|---|---:|---|
| CBDB SQLite 2026-11-07 `ADDR_CODES` | 30,160 | `a9_cbdb_addr_admin_level.csv` (`c_admin_type`, `CHGIS_PT_ID`, coordinates) |
| CBDB `BIOG_ADDR_DATA` links | 41,043 | `a9_person_addr_link.csv` |
| Historical urban population | 157 | `a9_ming_urban_population.csv` |
| Late-Ming Jinshi 1627–1644 | 1,950 | `a9_jinshi_1627_1644.csv` |
| CHGIS v6 county points (WGS84) | 10,522 | `a9_chgis_county_points.csv` (also `TYPE_CH`, `LEV_RANK`, `BEG_YR`/`END_YR`) |

## 3. Amendment 3 — coordinate confidence is now TESTABLE (open item closed)

`docs/p0_3_preregistration_amendment_3.md` was written **before** the analysis,
freezing the tier map (`c_admin_type`: county → tier 1, prefecture → tier 2,
coarse/unmatched → tier 3), the ≥60% match / ≤50% tier-3 coverage gates, and
the ±50% FDR criterion. `scripts/a10_coordinate_confidence.py` then ran:

| Quantity | Value |
|---|---:|
| CBDB address-link match rate | **99.2%** |
| tier 1 (county) / tier 2 (prefecture) / tier 3 | 2,556 / 258 / **27 (1.0%)** |
| persons with >1 address link | 64.1% |
| elite rows kept after dropping tier 3 | 2,814 of 2,841 |
| grids tested / FDR / median lag | **135 / 48 / 6.5 — identical to baseline** |

**Conclusion**: dropping coarse / unresolvable addresses changes nothing
(ΔFDR = 0). Coordinate precision does **not** drive the descriptive spatial
results. This **closes A8 §6 item 2** ("coordinate-confidence sensitivity not
testable") — it is now a passed robustness test, not an open limitation.
`c_admin_type` is an administrative-level proxy, not measured geocoding error;
the multi-address share is reported, not hidden.

## 4. Out-of-sample replication (1627–1644)

`scripts/a10_new_data_replication.py`, descriptive only:

- 1,842 late-Ming records with parsed rank + coordinates (from 1,950 rows;
  raw `EntryYear` extends to 1871, so 1627–1644 is filtered explicitly),
  197 grids.
- Grid-level Jinshi correlation with the v0.3 panel: **Pearson r = 0.865,
  Spearman r = 0.837**; top-20 grid overlap **14/20** (Jaccard 0.538).
- The Jiangnan-core spatial inequality finding **persists after the study
  window**. The famine series ends in 1619, so this is explicitly **not** a
  famine→Jinshi test.

## 5. External city points — coordinate cross-check

- 27 external points, lon 91.43–127.22, lat 19.98–50.57 (far north-east
  heavy; a small reference set, not a national sample).
- Nearest local CHGIS v6 county point: median distance **0.109°**;
  **77.8% within 0.25°**, **85.2% within 0.5°**.
- The downloaded GeoJSON is coordinate-consistent with the local CHGIS layer
  and is therefore usable as an independent reference. `ming_mian.json` has
  only 4 geometries and no attributes, so it is **not** usable for the B1
  province→grid mapping.

## 6. Population file — recorded as NOT usable as a national proxy

- 135 rows (1400–1620), 31 unique cities, **29 1° grids**, overlapping only
  **26 of 291 panel grids (8.9%)**.
- Coverage is far too sparse for a record-intensity or competition proxy.
  Per roadmap §4 no new control variable is fitted without pre-registration;
  the file is kept as a candidate for a future dated Go decision, not used.

## 7. What changed and what did not

| Item | Status |
|---|---|
| `docs/a3_main_results.md` headline numbers | **unchanged** (ΔFDR = 0; no new causal model) |
| `docs/a8_freeze_review.md` §6 item 2 | **superseded by this dated addendum**: coordinate confidence now tested and passed |
| `docs/b_feasibility_memo.md` B1 G2 (province→grid) | still unknown — `ming_mian.json` has no province attributes |
| `docs/b_feasibility_memo.md` B2 G4 | still **not met** — no hazard-typed table acquired |
| Route C | still frozen |
| Push | **none** — all work is local |

## 8. New open items (honest record)

1. B1 quota table and B2 hazard-typed table still need external suppliers;
   the network attempt did not produce either.
2. 64.1% of elite persons have more than one CBDB address link; Amendment 3
   takes the finest tier as frozen, but a person-level address-type study is
   not done.
3. Late-Ming analysis is descriptive; a famine series for 1627–1644 does not
   exist in the current assets.
4. External `ChenSK23/GIS` licence terms were not verified; files are used
   only as a read-only coordinate cross-check.
5. Push, Zenodo DOI and GitHub release remain deferred.

## 9. When this addendum would fail

- Any of the descriptive numbers is quoted as a causal result.
- CBDB / CHGIS / external files are replaced without re-running
  `a9_import_new_sources.py` and the `a10_*` scripts.
- A headline or public page is changed without re-running
  `python scripts/a0_apply_claims.py --check`.

Private inputs; aggregate outputs only.
