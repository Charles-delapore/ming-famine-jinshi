# P0-3 pre-registration — fixed analysis choices (2026-11-14)

**Status: FIXED BEFORE ANY SENSITIVITY RUN.** This file records the proxy
construction, thresholds, outcome metrics and failure criteria for P0-3
("reporting bias and uncertainty") *before* looking at any perturbed result.
Decision (2026-11-14, user): adopt the recommended dual-proxy design, then
continue with the remaining P0 items.
Source memo: `docs/p0_3_data_feasibility.md`.

## 1. Question

Are the v0.3 headline results — 48/135 FDR-significant famine→Jinshi Granger
grids and a 6.5-year median significant lag — an artefact of uneven historical
record intensity, coordinate imprecision, or year-recording error?

Baseline (reproduced exactly from `output/v03/summary.json` and re-verified in
this environment): 135 grids tested, 67 causal (p<0.05), **48 FDR-significant**,
**median lag 6.5 yr**.

## 2. Record-intensity proxies (FIXED)

Two proxies are reported side by side; neither alone is "the" record strength.

- **A — endogenous record density**: for each 1° grid, sum `zaihuang_count`
  over 1522–1619 in `output/v03/panel_v03.csv.gz`. Split at the **median** of
  non-zero grids into high / low. Outcome: FDR-discovery rate
  (mean of `gc_z_to_j_fdr_sig`) in each group, from
  `output/v03/granger_v03.xlsx`.
  *Caveat*: endogenous with the famine series; any gap is an **upper bound** on
  record bias, not a causal estimate.
- **B — exogenous administrative density**: count `table_citys.xlsx` points
  (251) per 1° grid; split at the median of non-zero grids into high / low.
  Same outcome metric. Weaker coverage, but largely independent of famine
  counts.

A "record-bias explanation" is **supported only if both** proxies show a
high-group FDR rate at least **10 percentage points** above the low group.
If only A shows it, the pattern is judged an endogeneity artefact and **not**
accepted.

## 3. Coordinate-confidence tiers (FIXED)

Using `xy_count` from `明进士.xlsx` / `table_general.xlsx` as a geographic
ambiguity proxy:

| Tier | Rule | Treatment |
|---|---|---|
| 1 | `xy_count == 1` | keep |
| 2 | `2 <= xy_count <= 10` | keep |
| 3 | `xy_count > 10` | drop in the sensitivity run |

Thresholds 1 and 10 are fixed **before** examining the outcome. This is a
proxy tiering, not a 县/府/省 label in the source; that limitation must be
stated in the result. The sensitivity run rebuilds the Jinshi series without
tier-3 rows and re-estimates Granger/FDR; the reported quantity is the change
in 48/135 and 6.5 yr.

## 4. Time perturbation (FIXED)

- Input: `output/v03/panel_v03.csv.gz` (real v0.3 yearly panel, 291 grids).
- Perturbation: shift the **famine series only** (`zaihuang_level`,
  `zaihuang_count`, `zaihuang_severity`) by `k` years within each grid, keeping
  `jinshi_count` fixed. Fixed set `k ∈ {0, +1, −1, +3, −3, +5, −5}` (7 runs).
  This is a deterministic panel-level time misalignment, not random jitter.
- Re-estimate with the **unchanged** `scripts/corrected_robustness.run_granger()`
  pipeline (`GridGrangerCausality(max_lag=20, significance=0.05, min_obs=30)`
  + BH FDR). No method change, no re-tuning.
- Records shifted outside 1520–1619 are dropped; every `k` is treated
  identically, so the comparison is fair. Stated as a limitation.
- Outcomes per `k`: grids tested, causal (p<0.05), FDR-significant grids,
  median FDR lag.

## 5. Failure criteria (FIXED BEFORE SEEING RESULTS)

| Conclusion | Fails if |
|---|---|
| "48/135 FDR discovery is real, not a year-alignment artefact" | any `\|k\|=1` run gives FDR-significant grids **< 24** or **> 72** (half / 1.5× baseline) |
| "median lag 6.5 yr / short-horizon dominance" | any run (any `k`) gives a median FDR lag more than **5 years** from 6.5, or one side (`+1/+3/+5` or `−1/−3/−5`) shows a monotone median-lag drift exceeding 5 years |
| "record bias explains 48/135" | the dual-proxy condition in §2 is not met (both proxies ≥ 10 pp gap) |

If a conclusion fails, the sensitivity table must say so explicitly rather
than softening the wording. Criteria 1–2 are evaluated by
`scripts/p0_3_time_perturbation.py`; criterion 3 by the later proxy step.

## 6. Order and outputs

1. Time perturbation (fully determined) → sensitivity table + figure.
2. Dual-proxy stratification → added table section.
3. Coordinate-tier drop → added table section.
4. Combined `docs/p0_3_sensitivity.md` with one table, one figure, and one
   explicit "under which perturbation the conclusion fails" sentence.

Machine-readable: `data/derived/p0_3_sensitivity_time.csv`.
Figure: `figures/p0_3_time_perturbation.{png,pdf}`.

## 7. Will NOT be done

- No new gazetteer/population download (plan §3 暂缓).
- No threshold tuning after seeing results; any change must be a new, dated
  pre-registration amendment.
- No synthetic-data stand-in; the real v0.3 panel is present.
- No GWR re-run for the time step (mgwr bandwidth selection is not part of the
  short-horizon claim).
