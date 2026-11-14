# A19 pre-registration — decomposing the A12 early-Ming contribution (2026-11-14)

**Written BEFORE running `scripts/a19_early_ming_decomposition.py`.**

## 1. Question

A12 found 8/155 grids in the fixed 1–5 year test on the full 1368–1643
independent panel, but only 1/142 on the 1521–1619 sub-window (v0.3's own
window gave 2/135). Where do the extra grids come from? This is a **pure
decomposition** of an existing result, not a new hypothesis and not an attempt
to enlarge the headline.

## 2. Data and method (frozen — no change from A12)

- Panel: `<local private panel; not distributed>` (built by
  `scripts/a12_full_ming_replication.py`, 1368–1643, 202 1° grids).
- Method: identical `fixed_lag_pvalue(z, j, lags=(1,2,3,4,5))` joint F test,
  identical `fixed_lag_panel` sample filters (≥3 non-zero famine years,
  ≥3 non-zero Jinshi years, ≥30 observations), BH FDR at alpha = 0.05.
- No re-estimation of the panel, no new variables.

## 3. Windows (frozen before results)

| Tag | Years | Purpose |
|---|---|---|
| `early_1368_1520` | 1368–1520 | before v0.3 |
| `v03_1521_1619` | 1521–1619 | same period as v0.3 (A12 secondary) |
| `late_1620_1643` | 1620–1643 | after v0.3 |
| `full_1368_1643` | 1368–1643 | A12 primary reference |

## 4. Reporting rule (frozen)

For each window report: grids tested, FDR-significant grids, percentage,
median selected lag (diagnostic only). **No pass/fail verdict, no significance
claim about differences between windows, no respecification.** The purpose is
to attribute A12's 8 grids to periods, not to claim a new effect.

If a window has < 30 years, `fixed_lag_pvalue` cannot be estimated; report it
as not estimable rather than changing the filter.

## 5. Interpretation limits

- Early-Ming Jinshi and famine records are sparser and differently documented;
  any extra grids there may reflect record density, not a stronger effect.
- The late window (24 years) is below the 30-observation filter for many grids.
- Windows are **not independent samples**; they are slices of one panel.
- FDR is recomputed within each window, so counts are not additive.

## 6. What will not be done

- No new lag windows, FDR alphas, grid sizes or transformations.
- No merging/splitting windows after seeing counts.
- No causal or mechanistic interpretation.
- No change to `docs/a3_main_results.md` or `docs/a12_full_ming_replication.md`.
- Outputs are aggregate only.

## 7. Outputs

`data/derived/a19_early_ming_decomposition.csv`,
`docs/a19_early_ming_decomposition.md`.
