# P0-3 pre-registration — Amendment 2 (2026-11-14)

**Dated amendment, written BEFORE the salvage analyses are run.** It does not
change the results reported in `docs/p0_3_sensitivity.md`; it adds a second,
pre-specified robustness round after two defects were found in the first round.

## 1. Why a second round

1. **Boundary truncation.** In step 3 the famine series was shifted while the
   observation window stayed 1506–1619. At `k=+5`, events from 1615–1619 leave
   the panel and five empty years enter at the start. The comparison therefore
   changes the *window* as well as the *alignment*, which is why the `k=+5`
   result cannot be read as a pure dating-error test.
2. **The lag estimator is bimodal.** Among the 48 baseline FDR grids the
   selected lag is either 1–3 years or 15–20 years (12 of 48 are ≥15). The
   median of a bimodal distribution is a fragile summary: a small change in
   composition moves it by several years without any change in the underlying
   short-horizon signal.
3. **Step 2 (coordinate tiers) was voided** because `xy_count` counts records
   sharing a coordinate, not geographic precision (Amendment 1).
4. **The proxy-B median split is effectively binary.** The median of non-zero
   administrative density is 1, so "high vs low" means "≥1 vs 0 city point".

## 2. Fixed design — common-support time perturbation

- **Window:** 1511–1614. The panel spans 1506–1619 and the largest shift is
  ±5 years, so 1511–1614 is the maximal common support of all shifted versions.
- **Shifts:** the same frozen set `{-5, -3, -1, 0, +1, +3, +5}`.
- **Procedure:** shift the famine series on the full panel, then clip every
  panel (including `k=0`) to 1511–1614. The number of years is then identical
  for all shifts.
- **Baseline:** `k=0` re-estimated on the same restricted window, not reused
  from the full-panel run.

## 3. Metrics and pass criteria (fixed)

Primary metric: **FDR-significant grids**.

Secondary metrics:

- **short-lag share** = share of FDR-significant grids with selected lag ≤ 5;
- **median lag** (reported, but *not* used as pass/fail because it is bimodal);
- **paired lag change** on grids that were FDR-significant at `k=0`.

Pass criteria:

| Criterion | Threshold |
|---|---|
| FDR count at `|k| = 1` | within ±25% of the restricted baseline |
| Short-lag share at `|k| = 1` | within ±10 pp of the restricted baseline |
| FDR count at `|k| = 3` | within ±40% of the restricted baseline |
| Paired median `|Δlag|` at `|k| = 1` | ≤ 2 years |
| Paired grids within ±3 years at `|k| = 3` | ≥ 60% |

Decision rule:

- pass at `|k| ≤ 1` but fail at `|k| = 3`: conclusion is "robust to ±1-year
  dating error, not to ±3";
- pass at `|k| ≤ 3`: conclusion is "robust to plausible dating error (±3
  years)"; `±5` is reported as an extreme stress test and is not decisive;
- fail at `|k| = 1`: the headline claim is not robust and must be rewritten.

## 4. Record-bias dose-response (replaces the median split)

- Proxy B (exogenous administrative density): levels **0, 1, 2+**.
- Proxy A (endogenous famine count): **quartiles** of grids, zeros included.
- Pass criterion: a **monotone** gradient in FDR rate across levels **and** a
  top-vs-bottom gap ≥ 10 pp, for **both** proxies.
- Descriptive addition: logistic regression `FDR ~ C(B level) + A quartile`;
  odds ratios are reported, not used as pass/fail.

## 5. Coordinate precision — declared not testable

The export has no administrative-level field. `AddrChn` is a place name (often
a county name without a suffix), and `X/Y` precision is undocumented. There is
no defensible county / prefecture / province tier in these fields. Step 2
remains **void**; no substitute test will be invented after seeing results.
This is recorded as a data limitation, not as a negative finding.

## 6. What will not be done

- No threshold changes after seeing results.
- No dropping of a failing shift from the report.
- No proxy invented after seeing results.
- No re-use of the full-panel baseline for the restricted-window comparison.
