# A12 pre-registration — full-Ming independent replication (2026-11-14)

**Written BEFORE running `scripts/a12_full_ming_replication.py`.** Frozen
design; any change requires a new dated amendment. This is a **replication**,
not an attempt to enlarge the v0.3 headline (roadmap §4).

## 1. Question

Can the v0.3 short-window finding — a fixed 1–5 year joint Granger test
significant in **2/135** grids — be reproduced with an **independent famine
source**, on the **full Ming window (1368–1643)**, using the **same method**?

## 2. Data (frozen)

| Input | Source | Notes |
|---|---|---|
| famine | `<local private input; not distributed>` (from `灾荒数据.zip/table_level.json`, 69,276 city-year rows, 251 cities, 1368–1643, `level` 0–5) | independent of `merged_data.csv` used for v0.3 |
| Jinshi | `<path to the private CBDB export>` (28,761 rows; 1368–1643) | same CBDB export as v0.3, but **full** year range, not 1521–1619 |

## 3. Panel construction (frozen)

- Spatial unit: **1° grid**, `floor(X)+0.5` / `floor(Y)+0.5` — same as v0.3.
- Famine exposure `z`: per (year, grid), **sum of city `level`** in that grid
  (`merged_data.csv` used a severity sum; `level` is the analogous grade).
- Outcome `j`: per (year, grid), count of Jinshi records with a **parsed rank**
  (`rank_class` ∈ {1,2,3}), `X/Y` present, and `EntryYear` in 1368–1643.
- Full rectangular panel: every grid × every year; missing filled with 0.
- Windows reported:
  1. **full 1368–1643** (primary, 276 years);
  2. **1521–1619** (secondary, exact v0.3 window — isolates the data-source change).

## 4. Method (frozen — no re-specification)

Exactly reuse `scripts/long_tail_analysis.py`:

- `fixed_lag_pvalue(z, j, lags=(1,2,3,4,5))` — joint F test of restricted
  (y-only) vs unrestricted (+x) models, no lag selection;
- `fixed_lag_panel` sample filters: ≥3 non-zero famine years, ≥3 non-zero
  Jinshi years, ≥30 observations per grid;
- `fdr_correction(..., alpha=0.05)` (BH) across grids.
- Diagnostic only: `GridGrangerCausality(max_lag=5)` and `max_lag=20` with BH,
  to show the search-window inflation on the new source.

## 5. Decision criteria (frozen, before results)

Let `N` = grids tested and `k` = FDR-significant grids in the fixed 1–5 test.

| Result | Verdict |
|---|---|
| `k = 0` | **not replicated** — record as a zero result, no respecification |
| `1 ≤ k ≤ 0.10·N` | **partially replicated**: still a minority of grids with a short-window signal |
| `k > 0.10·N` | **inconsistent** — report both, do not tune to match 2/135 |

Comparison with v0.3 is on **order of magnitude and existence only**: `N`
differs (different source/coverage), so exact equality with 2/135 is not
expected and is not a pass criterion.

## 6. Failure / interpretation limits

- `level` is a grade, not the v0.3 severity sum; absolute coefficients are not
  comparable.
- 251 city points → fewer 1° grids than v0.3's 291; report the coverage.
- `明进士.xlsx` has stray `EntryYear` up to 1871; the 1368–1643 filter is
  applied explicitly and the excluded count is reported.
- Early-Ming (1368–1520) record density is lower; the 1521–1619 secondary
  window is the cleaner like-for-like check.
- No Granger lag is interpreted causally.

## 7. What will not be done

- No alternative lag windows, FDR alphas, grid sizes or transformations after
  seeing `k`.
- No new control variables, no SHAP, no ML surrogate.
- No change to `docs/a3_main_results.md` headline numbers; a dated addendum
  records the replication outcome.
- Outputs are aggregate only.

## 8. Outputs

`data/derived/a12_full_ming_fixed_lag.csv`,
`data/derived/a12_full_ming_lag_window.csv`,
`<local private panel; not distributed>`,
`docs/a12_full_ming_replication.md`.
