# A19 — A12 early-Ming decomposition (2026-11-14)

- Generated: 2026-11-14 18:08
- Command: `python scripts/a19_early_ming_decomposition.py`
- Pre-registration: `docs/a19_early_ming_preregistration.md` (frozen before run). Pure decomposition, **no verdicts**.
- Panel: `<local private panel; not distributed>` (independent famine source, 1368–1643, 202 grids).
- Method unchanged from A12: `fixed_lag_pvalue(1..5)` joint F test, same sample filters, BH FDR 0.05.

| Window | Years | n years | grids tested | FDR grids | % |
|---|---|---:|---:|---:|---:|
| early_1368_1520 | 1368-1520 | 153 | 127 | 10 | 7.87% |
| v03_1521_1619 | 1521-1619 | 99 | 142 | 1 | 0.70% |
| late_1620_1643 | 1620-1643 | 24 | 0 | 0 | nan% |
| full_1368_1643 | 1368-1643 | 276 | 155 | 8 | 5.16% |

## Attribution (descriptive)

- Full window (A12 primary): **8/155**.
- v0.3-period slice: **1/142** (A12 secondary reported 1/142; identical method confirmed here).
- Early Ming (1368–1520): **10/127**.
- Late Ming (1620–1643): **0/0** (24 years; below the 30-observation filter for many grids).

FDR is recomputed **within each window**, so counts are deliberately **not additive** — this table attributes where the full-window grids are estimable, it does not partition them arithmetically.

## Interpretation limits (frozen)

- Early-Ming records are sparser and differently documented; extra grids there may reflect record density, not a stronger effect.
- Windows are slices of one panel, not independent samples.
- The late window is short; `not estimable` grids are excluded by the same ≥30-observation filter as A12, not by a new rule.
- **No pass/fail verdict, no significance claim about differences, no respecification.** No change to `docs/a3_main_results.md` or `docs/a12_full_ming_replication.md`.

## When this would fail

- The panel or the method changes without re-running A12 and A19.
- Windows are merged/split after seeing counts (forbidden).
- These descriptive counts are quoted as a new effect.

Machine-readable: `data/derived/a19_early_ming_decomposition.csv`.

Private inputs; aggregate outputs only.
