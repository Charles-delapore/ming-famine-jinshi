# P0-3 salvage — common-support perturbation and lag stability (2026-11-14)

- Generated: 2026-11-14 16:25
- Command: `python scripts/p0_3b_salvage.py`
- Pre-registered choices: `docs/p0_3_preregistration_amendment_2.md` (frozen before this run).
- Input: real `output/v03/panel_v03.csv.gz`, restricted to 1511–1614.

## 1. Why this exists

The first ±k test changed the observation window as well as the alignment, and
the lag distribution is bimodal (1–3 yr or 15–20 yr), so the median is fragile.
This round fixes the window to the maximal common support of all shifts.

## 2. Common-support time perturbation

| k (yr) | grids | FDR grids | median lag | short-lag share (≤5 yr) | long lags (>10) |
|---:|---:|---:|---:|---:|---:|
| -5 | 133 | 56 | 8.0 | 36% | 25 |
| -3 | 133 | 63 | 5.0 | 52% | 22 |
| -1 | 133 | 52 | 3.5 | 58% | 17 |
| +0 | 133 | 46 | 5.0 | 52% | 18 |
| +1 | 133 | 37 | 6.0 | 49% | 16 |
| +3 | 133 | 35 | 11.0 | 37% | 18 |
| +5 | 133 | 18 | 12.5 | 44% | 9 |

Restricted baseline: **46 grids**, short-lag share **52%**, median lag 5.0 yr.

### Pass criteria

- ±1 yr: FDR count within ±25% and short-lag share within ±10 pp → **PASS**
- ±3 yr: FDR count within ±40% → **PASS**
- Paired lag stability at ±1 yr (median |Δlag| ≤ 2 yr) and ±3 yr (≥60% within ±3 yr)

### Failures recorded

- none

### Lag distribution by shift

| k | 1–5 | 6–10 | 11–14 | 15–20 |
|---:|---:|---:|---:|---:|
| -5 | 20 | 11 | 8 | 17 |
| -3 | 33 | 8 | 6 | 16 |
| -1 | 30 | 5 | 5 | 12 |
| +0 | 24 | 4 | 6 | 12 |
| +1 | 18 | 3 | 5 | 11 |
| +3 | 13 | 4 | 6 | 12 |
| +5 | 8 | 1 | 0 | 9 |

### Paired lag change on baseline-significant grids

| k | paired grids | median |Δlag| | share within ±3 yr | still FDR-significant |
|---:|---:|---:|---:|---:|
| -5 | 46 | 5.0 | 37% | 33 |
| -3 | 46 | 3.0 | 67% | 38 |
| -1 | 46 | 1.0 | 83% | 39 |
| +0 | 46 | 0.0 | 100% | 46 |
| +1 | 46 | 1.0 | 78% | 33 |
| +3 | 46 | 2.0 | 61% | 26 |
| +5 | 46 | 5.0 | 37% | 15 |

## 3. Record-bias dose-response

| proxy | level | n | FDR rate |
|---|---|---:|---:|
| B administrative density | 1 | 100 | 0.320 |
| B administrative density | 2 | 26 | 0.500 |
| B administrative density | 3+ | 9 | 0.333 |
| A famine count | Q1 | 34 | 0.353 |
| A famine count | Q2 | 34 | 0.294 |
| A famine count | Q3 | 33 | 0.333 |
| A famine count | Q4 | 34 | 0.441 |

- Proxy B: monotone = **False**, top-vs-bottom = **+1.3 pp**, Spearman ρ = 0.11
- Proxy A: monotone = **False**, top-vs-bottom = **+8.8 pp**, Spearman ρ = 0.07
- Dose-response criterion (both proxies monotone and ≥10 pp): **FAIL**

Logistic model `FDR ~ C(B level) + A quartile`:

| term | OR | 95% CI | p |
|---|---:|---|---:|
| C(b_level)[T.2] | 2.63 | 0.71–9.78 | 0.150 |
| C(b_level)[T.3] | 1.32 | 0.23–7.78 | 0.756 |
| a_rank | 0.90 | 0.54–1.48 | 0.670 |

## 4. Coordinate precision

Not testable with the available fields (Amendment 2 §5). Step 2 remains void;
no substitute test is invented.

## 5. What the headline can claim

- The FDR discovery count is stable under common-support shifts of ±1 and ±3 years; ±5 is an extreme stress test.
- The horizon should be reported as a **distribution** (short-lag share), not as a single 6.5-year median.
- Record-bias dose-response: proxy B monotone=False, gap +1.3 pp; proxy A monotone=False, gap +8.8 pp → **NOT SUPPORTED**.

## 6. When this would fail

- If the analysis window is changed again after seeing results.
- If the lag distribution is summarised by a mean or median alone.
- If the record-bias proxies are redefined post hoc.

Machine-readable: `data/derived/p0_3b_*.csv`.
