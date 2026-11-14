# A12 — full-Ming independent replication (2026-11-14)

- Generated: 2026-11-14 17:52
- Command: `python scripts/a12_full_ming_replication.py`
- Pre-registration: `docs/a12_full_ming_preregistration.md` (frozen before run).
- Famine source: `灾荒数据.zip/table_level.json` (69,276 city-year rows, 1368–1643, 251 cities, 202 1° grids) — **independent** of the v0.3 `merged_data.csv`.
- Jinshi source: full `明进士.xlsx`, 1368–1643, parsed ranks only.
- Records outside 1368–1643 excluded: **3,316**.
- Method: identical `fixed_lag_pvalue(z, j, (1,2,3,4,5))` joint F test + BH FDR as `docs/long_tail_analysis.md` §2.

## Primary verdict (full 1368–1643): **PARTIALLY REPLICATED (minority of grids)**

| Window | Years | grids tested | fixed 1–5 FDR grids | % | verdict |
|---|---|---:|---:|---:|---|
| full_1368_1643 | 1368-1643 | 155 | 8 | 5.2% | PARTIALLY REPLICATED (minority of grids) |
| v03_window_1521_1619 | 1521-1619 | 142 | 1 | 0.7% | PARTIALLY REPLICATED (minority of grids) |

v0.3 reference (different source, 1506–1619 panel): **2/135** grids in the same fixed 1–5 year joint test. Comparison is on existence and order of magnitude only; the number of estimable grids differs, so exact equality is not a pass criterion (pre-registration §5).

## Lag-window diagnostic (same source)

| Window | max_lag | grids tested | FDR grids | median lag | short-lag share |
|---|---:|---:|---:|---:|---:|
| full_1368_1643 | 5 | 155 | 19 | 2.0 | 1.00 |
| full_1368_1643 | 20 | 155 | 28 | 3.5 | 0.64 |
| v03_window_1521_1619 | 5 | 142 | 4 | 2.5 | 1.00 |
| v03_window_1521_1619 | 20 | 142 | 5 | 3.0 | 0.80 |

The 20-lag search is shown only to document search-window inflation on the independent source; it is not a headline.

## Interpretation

The fixed short-window signal reappears in **8/155** grids of the full-Ming independent panel — again a small minority. This supports the route-A framing: a *short-horizon predictive association in a minority of grids*, not a general causal effect.

## When this would fail

- `level` is a 0–5 grade, not the v0.3 severity sum; absolute effect sizes are not comparable.
- Only 251 city points → 202 grids (v0.3 had 291); coverage is lower.
- Early-Ming (1368–1520) record density is lower; the 1521–1619 secondary window is the cleaner like-for-like check.
- Stray `EntryYear` up to 1871 were excluded explicitly; a different filter changes the panel.
- Any post-hoc change to lags, FDR alpha, grid size or window is forbidden by the pre-registration.

## Outputs

| Output | Path |
|---|---|
| rectangular panel | `<local private panel; not distributed>` |
| fixed-lag grid results | `data/derived/a12_full_ming_fixed_lag.csv` |
| lag-window diagnostics | `data/derived/a12_full_ming_lag_window.csv` |

Private inputs; aggregate outputs only.
