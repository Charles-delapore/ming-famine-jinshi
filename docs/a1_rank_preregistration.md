# A1 pre-registration — rank-share model (2026-11-14)

**Written BEFORE running `scripts/a1_rank_analysis.py`.** Thresholds and design
are frozen here; any change requires a new dated amendment (roadmap §5).

## 1. Question

Does famine exposure change the **rank composition** of Jinshi (share of 1甲/2甲)
rather than only the number of Jinshi? This is the A5 research question in
roadmap §1.1, executed as work package A1.

## 2. Unit of analysis

1° grid × exam year (`EntryYear`), 1521–1619, from the CBDB export
`明进士.xlsx` (28,761 rows). Grid assignment uses the same `floor(X)+0.5` /
`floor(Y)+0.5` rule as `scripts/corrected_robustness.py`.

## 3. Outcome (frozen denominator)

`share_top = count(rank_class ∈ {1,2}) / count(rank_class ∈ {1,2,3})`
per unit. `rank_class` comes from `src/data_processing/jinshi_rank.py`
(normalizes Arabic and Chinese numerals). Records with an unparsed / missing
rank are excluded from **both** numerator and denominator. No imputation.

## 4. Exposure (frozen window)

`famine_1_5` = mean of `zaihuang_severity` at years `t−1 … t−5` in the same
grid, from `output/v03/panel_v03.csv.gz`. The famine series is identical in
v0.2 and v0.3, so this is unaffected by the encoding fix. Only the 1–5 year
window is tested (roadmap §4: no 20-year tails).

## 5. Sample restrictions (fixed)

- unit denominator ≥ 3 records;
- grid has ≥ 5 valid exam-year units;
- exam years 1521–1619 only.

## 6. Model (fixed)

Weighted least squares:

```
share_top ~ famine_1_5 + log(total) + C(grid) + C(exam_year)
```

weights = `total` (the denominator), standard errors clustered by grid.
One primary coefficient: `famine_1_5`. `log(total)` absorbs mechanical
denominator effects; grid and exam-year fixed effects absorb time-invariant
geography and cohort shocks.

## 7. Null / failure criteria (fixed)

- **Null** if the 95% CI of `famine_1_5` includes 0 **and** |standardized beta|
  < 0.05.
- If null: record as a zero result and **stop**. No alternative windows, no
  alternative denominators, no added controls, no subgroup search.
- Report coefficient, 95% CI, n units, n grids and R² regardless of direction.

## 8. Pre-specified descriptive check

Permutation test: shuffle `famine_1_5` across exam years within each grid
(200 replicates, seed `20261114`); report the two-sided permutation p. It is
**descriptive only** and cannot rescue a null.

## 9. What will not be done

- No 6–10 / 11–20 year windows.
- No separate 1甲-only or 2甲-only models.
- No ML / SHAP surrogate (roadmap §4).
- No re-specification after seeing the coefficient.

## 10. Outputs

`data/derived/a1_rank_coefficients.csv`, `data/derived/a1_rank_units.csv`,
`figures/a1_rank_share.{png,pdf}`, `docs/a1_rank_results.md`.
