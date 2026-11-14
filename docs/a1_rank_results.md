# A1 — rank-share results (2026-11-14)

- Generated: 2026-11-14 16:58
- Command: `python scripts/a1_rank_analysis.py`
- Pre-registration: `docs/a1_rank_preregistration.md` (frozen before run).
- Input: CBDB `明进士.xlsx` (28,761 rows) + real `output/v03/panel_v03.csv.gz`.
- Model: WLS `share_top ~ famine_1_5 + log(total) + C(grid) + C(exam_year)`, weights = denominator, SE clustered by grid.

**Verdict: NULL (zero result; stop expansion)**

| Quantity | Value |
|---|---:|
| coefficient on famine_1_5 | +0.000283 |
| cluster SE | 0.003155 |
| 95% CI | [-0.005901, +0.006467] |
| standardized beta | +0.0033 |
| p (cluster) | 0.9286 |
| permutation p (200 reps) | 0.9350 |
| units / grids / exam years | 1298 / 81 / 34 |
| R² | 0.2351 |

## Interpretation (pre-registered rule)

- Null criterion: 95% CI includes 0 **and** |standardized beta| < 0.05 → met.

**Zero result.** Famine exposure in the preceding 1–5 years does not shift the 1甲/2甲 share of Jinshi in this specification. Per the pre-registration this is recorded as-is and **no expansion is undertaken**: no alternative windows, denominators, controls or subgroups.

## When this result would fail

- If the rank normalizer changes (unparsed ranks are currently excluded from both numerator and denominator).
- If the 1–5 year exposure window or the ≥3 denominator / ≥5-units-per-grid restrictions are changed; all are frozen in the pre-registration.
- If grid/exam-year fixed effects are dropped, the coefficient is not comparable.
- Rank composition is measured on CBDB records with a parsed rank only; selection into parsed ranks is not modelled.

## Outputs

| Output | Path |
|---|---|
| coefficient table | `data/derived/a1_rank_coefficients.csv` |
| unit-level data | `data/derived/a1_rank_units.csv` |
| figure | `figures/a1_rank_share.{png,pdf}` |

Private inputs; aggregate outputs only.
