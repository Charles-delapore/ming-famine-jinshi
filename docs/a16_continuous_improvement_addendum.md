# A16 — continuous-improvement addendum (2026-11-14)

**User instruction**: continue improvement and data analysis, keep per-segment
worklog, literature/resource search and external-data acquisition allowed.
**Constraints**: private inputs, aggregate outputs.

This addendum sits on top of `docs/a8_freeze_review.md` (route-A freeze) and
`docs/a11_freeze_addendum.md` (first data-acquisition round). It records a
second round of **new data + four analyses**. Route A remains frozen; the
`docs/a3_main_results.md` headline numbers are **unchanged**.

---

## 1. Data acquired this round

**Local archive, previously unused**: `000毕设/008/.../原始数据/灾荒数据.zip`
contained a complete, balanced famine panel that the project had never opened:

| File | Rows | Content |
|---|---:|---|
| `table_level.json` | 69,276 | 251 cities × 276 years, **1368–1643**, `level` 0–5 |
| `table_city.json` | 251 | city point coordinates (100% matched) |
| `table_calendar.json` | 276 | 公历/干支/年号 mapping |

Standardized by `scripts/a12_import_full_ming_famine.py` into
`<local private input; not distributed>` (202 1° grids). This is an
**independent famine source** from the `merged_data.csv` used for v0.3 and
extends the window from 114 to 276 years.

**External (network, allowed)**: GitHub repository search hit
`Fengx06/Data-of-Famine-Cannibalism-in-Ancient-China` (MIT). Via the GitHub
contents API (the `raw` domain is blocked), two result CSVs were downloaded:
`a15_external_famine_summary.csv` (6,293 B) and
`a15_external_famine_chronology.csv` (533,791 B, with `year_ce`, province/
city/county and WGS84 coordinates).

Also reused: full `明进士.xlsx` (1368–1643, not just 1521–1619), CHGIS v6 Ming
county points (2,183), and three social-network workbooks (~40k edges).

## 2. Four analyses

| # | Script | Pre-registration | Result |
|---|---|---|---|
| A12 | `a12_full_ming_replication.py` | `docs/a12_full_ming_preregistration.md` (frozen before run) | **PARTIALLY REPLICATED** |
| A13 | `a13_admin_density_proxy.py` | repeat of Amendment 2 §4 (criterion unchanged) | criterion **still not met** |
| A14 | `a14_elite_network_audit.py` | P1-7 coverage gate declared before computation | **NO-GO** (15.4% < 30%) |
| A15 | `a15_external_famine_crosscheck.py` | descriptive cross-check | positive external validity |

### A12 — full-Ming independent replication (the main result)

Same `fixed_lag_pvalue(z, j, (1,2,3,4,5))` + BH FDR as v0.3, on the independent
source and the full 1368–1643 window:

| Window | grids tested | fixed 1–5 FDR grids | % | verdict |
|---|---:|---:|---:|---|
| 1368–1643 (primary) | 155 | **8** | 5.2% | partially replicated |
| 1521–1619 (v0.3 window) | 142 | **1** | 0.7% | partially replicated |
| v0.3 reference | 135 | 2 | 1.5% | — |

- The like-for-like 1521–1619 window gives **1/142** vs v0.3's **2/135** —
  the same order of magnitude under a pure data-source change.
- Lag-search inflation reappears on the independent source: max_lag 5 → 20
  gives 19 → 28 grids (full window) and 4 → 5 (v0.3 window).
- **Both route-A core claims are strengthened**: a short-window association
  exists in a minority of grids, and its headline size is purchased by lag
  searching. No respecification was used to obtain this.

### A13 — record-intensity proxy upgrade

CHGIS Ming-valid county points (2,183, ~9× denser than the old 251-point
proxy, with BEG_YR/END_YR) → all 135 v0.3 grids have points. Dose-response:
Q1 0.320 / Q2 0.280 / Q3 0.423 / Q4 0.412 → **non-monotone**, top-vs-bottom
**+9.2 pp < 10 pp**. The pre-registered criterion is **still not met**, which
**strengthens** the frozen "no record-intensity dose-response" conclusion —
the earlier near-binary proxy was the weak link.

### A14 — elite social network (P1-7 prerequisite)

40,450 raw edges → 22,459 deduplicated; 6,902 actors; 20,767 edges with both
coordinates. Jinshi PersonIDs with any network edge: **4,276 / 27,711 =
15.4%**, below the declared 30% gate → **NO-GO**. Per roadmap §2 P1-7 the
correct output is a method note only; no ego-network or funnel was built.
`Edge Dist.` units are undocumented (median 1.0, no value < 1) and were not
interpreted as geographic distance.

### A15 — external extreme-famine chronology cross-check

1,856 raw rows → 1,361 Ming rows with coordinates, 133 event years.

| Check | Value |
|---|---:|
| Pearson r, annual famine level vs extreme events | **0.583** |
| Spearman r | **0.664** |
| Pearson r, affected-city count vs events | 0.461 |
| event grid-years with local level > 0 | **61.8%** (477/772) |

The independent extreme-event chronology tracks the local famine panel's
temporal pattern. This supports the famine series' external validity. It is
**not** a hazard-typed table: **B2 gate G4 remains unmet**.

## 3. What changed and what did not

| Item | Status |
|---|---|
| `docs/a3_main_results.md` headline numbers | **unchanged** |
| Route-A core claim 1 (minority short-window signal) | **independently replicated** |
| Route-A core claim 2 (lag-search inflation) | **independently reproduced** |
| P0-3 "no record-bias dose-response" | **strengthened** with a 9× denser proxy |
| P1-7 elite network | **closed as NO-GO** (coverage 15.4%) |
| B2 G4 (hazard field) | still not met; external chronology is extreme-event only |
| B1 quota table / C Qing data | still need external suppliers |
| Route C | still frozen |
| Push | **none** |

## 4. New open items

1. A12 shows 8/155 on the full window but 1/142 on the v0.3 window; the
   early-Ming (1368–1520) contribution to the extra grids is not decomposed
   (would need a new dated pre-registration).
2. A14's 15.4% coverage refers to the three query workbooks; CBDB
   `KIN_DATA` (565,276) / `ASSOC_DATA` (190,164) may raise it but were not
   audited here.
3. A15 external files' ancient-place geocoding was done by their authors;
   residual error is not audited.
4. B1/B2/C and push/DOI/release remain deferred.

## 5. When this addendum would fail

- Any of these descriptive/replication numbers is quoted as a causal result.
- A headline or public page is changed without re-running
  `python scripts/a0_apply_claims.py --check`.
- Source files (灾荒数据.zip, CHGIS, network workbooks, external CSVs) are
  replaced without re-running the `a12`–`a15` scripts.

Private inputs; aggregate outputs only.
