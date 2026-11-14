# Long-tail diagnostics: is the 15–20 year Granger tail real?

Date: 2026-11-14
Status: local analysis, not published
Inputs: `output/v03/panel_v03.csv.gz`, `output/v03/granger_v03.xlsx`
Scripts: `scripts/long_tail_analysis.py`, `scripts/long_tail_null.py`

## 0. Question

The v0.3 headline is "famine→Jinshi Granger survives FDR in 48/135 grids,
median lag 6.5 years". The lag distribution is bimodal: 21 of 48 grids select
lag ≤5 years and 19 select lag ≥15 years. This memo asks whether the long tail
is a substantive long-run effect or an artefact of the lag search.

## 1. The discovery count depends on how many lags the search may try

`scripts/long_tail_analysis.py` re-runs the identical max-F Granger pipeline
with different `max_lag` values, and adds a within-grid Bonferroni correction
over the lag candidates actually tried (`p × max_lag`, then BH across grids).

| max_lag | FDR grids | FDR after within-grid Bonferroni | median lag | share lag ≤5 | grids with lag ≥15 |
|---:|---:|---:|---:|---:|---:|
| 5 | 13 | 0 | 2.0 | 100% | 0 |
| 10 | 26 | 2 | 2.0 | 69% | 0 |
| 15 | 34 | 3 | 3.0 | 59% | 3 |
| 20 | **48** | **7** | 6.5 | 44% | 19 |

The count rises monotonically with the search window (13 → 26 → 34 → 48) while
the corrected count stays small (0 → 2 → 3 → 7). Most of the headline is
purchased by trying 20 lags per grid.

## 2. A fixed, pre-specified short-lag test

A joint F-test with lags fixed in advance (no selection) gives:

| lag set | grids tested | FDR grids |
|---|---:|---:|
| 1–3 | 135 | 0 |
| 1–5 | 135 | 2 |
| 1–10 | 135 | 3 |

This is the cleanest design and the closest to the Qing-China benchmark
(1-year and 5-year drought windows). It finds a **small** short-horizon signal,
not a large one.

## 3. Transformation checks

| transform | max_lag=5 FDR | max_lag=20 FDR | lag ≥15 at 20 |
|---|---:|---:|---:|
| raw levels | 13 | 48 | 19 |
| linear detrend per grid | 14 | 48 | 14 |
| first differences | 1 | 42 | 18 |

Linear trend is not the driver. First differences remove the level information
and collapse the short-lag signal (13 → 1) while the long-lag count stays high,
which is what over-fitting 20 lags to 114 points looks like.

## 4. Permutation null

`scripts/long_tail_null.py` permutes the Jinshi series within each grid
(famine fixed) and reruns the identical pipeline. 50 replicates, seed 20261114.

- mean FDR grids under the null: **7.2**
- 95th percentile: 15; maximum: 28
- observed: 48

The observed count is above the iid-permutation null (p < 1/50), so *some*
association exists; but the uncorrected pipeline already produces ~7
"discoveries" from noise, the same order as the 7 grids that survive
Bonferroni. `scripts/long_tail_block_null.py` repeats the exercise with a
circular block shuffle (block length 10, preserving local autocorrelation):
mean 7.2, maximum 16 over 30 replicates. Observed 48 is still above it, so the
signal is not pure noise; it is the *size* of the claim that is fragile.

## 5. Are long-lag grids a distinct ecology?

19 long-lag grids (≥15 yr) vs 21 short-lag grids (≤5 yr), among the 48:

| variable | short (≤5) | long (≥15) | Mann–Whitney p |
|---|---:|---:|---:|
| famine severity (sum) | 190 | 191 | 0.47 |
| famine records | 102 | 106 | 0.44 |
| Jinshi records | 41 | 25 | 0.06 |
| famine years | 77 | 81 | 0.88 |
| grid_x | 117.5 | 114.5 | 0.13 |
| grid_y | 30.5 | 34.5 | 0.21 |

Long-lag grids are not more famine-prone and are not spatially clustered
(mean pairwise distance 8.9° vs 8.6° under random draws, p = 0.67). The only
difference is fewer Jinshi records — i.e. weaker signal, where the lag search
has more freedom.

## 6. Literature check

### 6.1 From the graduation archive

| Source | What it gives us | Use |
|---|---|---|
| 邓君等, 2020, 图书情报工作 64(17) | CBDB Ming Jinshi, SNA + GIS, Jiangnan concentration | direct precedent; our contribution is inference/robustness, not description |
| 邓君等, Qing counterpart | same design for 1644–1911 | comparative chapter |
| 宋传银, 明代湖北双籍进士 | dual registration and migration | secondary mechanism |
| 郑立勇, 吉安府科第 | regional elite formation in Jiangxi | regional case |
| 郭培贵 (2021 项目成果) | 24,586 Ming Jinshi; 1甲 267 / 2甲 6,469; mean exam age 32.65; 43.46% from commoner families; 南/北/中卷 quotas 55/35/10 | denominators, age structure, **quota confound** |
| 钱茂伟, 国家、科举与社会 | 乡试 ~4%, 会试 ~10% | competition context |
| DBSCAN / event-clustering papers | methods only | already used |

### 6.2 New literature (search, 2026-11-14)

| Source | Finding | Use |
|---|---|---|
| Li, Liao & Teng, 2026, *World Development*, doi:10.1016/j.worlddev.2026.107587 | Qing panel 1646–1904, 234 prefectures: drought 1 year before exams **−6%** Jinshi density; additional droughts in past 5 years **−2.6%** per period; results stable after proxying recording capacity with meteorological word counts | **direct benchmark**: short horizon, small effect, same direction |
| Chen et al., 2020 (Great Chinese Famine) | up to 3.8 years less schooling | early-life mechanism, 20–30 yr horizon |
| Meng & Qian, 2009 (NBER w14917) | in-utero/early-childhood exposure affects education and labour supply | early-life mechanism |
| 2022 IJERPH cognition study | childhood exposure, long-run cognition | mechanism, not exam outcome |
| Bai & Jia, 2016, *Econometrica* | exam quotas shape regional elite outcomes | quota confound |
| *Social Mobility in Late Imperial China*, 2020 | family background predicts Jinshi | omitted-variable caveat |

The independent Qing result supports a **short** window (1 and 5 years) and a
**small** effect. No study in this set reports a 15–20 year exam-lag effect.

### 6.3 The thesis's 20-year claim

The graduation thesis reports the opposite long-run picture: a lagged cluster
similarity model finds the maximum similarity at **20 years** (max 0.824,
p < 0.01) and says most significant cluster pairs peak at 20 years. That claim
is the origin of the long tail and deserves a direct check.

`scripts/long_tail_cohort_probe.py` builds the implied cohort design: count
future Jinshi by birth grid and birth year (`IndexYear`), merge famine severity
at birth and over ages 0–5, and estimate two-way (grid + birth-year) fixed
effects on log1p counts and on the extensive margin.

| outcome | exposure | coef | se | p |
|---|---|---|---:|---:|---:|
| log1p count | famine at birth | +0.0025 | 0.0014 | 0.076 |
| log1p count | famine ages 0–5 | +0.0014 | 0.0005 | 0.010 |
| any Jinshi | famine at birth | +0.0010 | 0.0012 | 0.423 |
| any Jinshi | famine ages 0–5 | +0.0010 | 0.0005 | 0.030 |

The sign is **positive**, not the negative "inhibition" the thesis reports.
This is almost certainly documentation intensity: years and grids with more
famine records also have more Jinshi records. It is not evidence for a
20-year effect, and it shows that the cohort design is not identified without
a reporting-intensity control. The 20-year claim should be treated as a
hypothesis, not a result.

Two further caveats: 47.6% of records have `IndexYear = EntryYear − 30`
exactly (imputed age), and the Ming quota system (南/北/中卷, 55/35/10 after
1435) constrains Jinshi counts by region regardless of local human capital.

## 7. What this means for the Ming claims

1. **Do not report 48/135 as the headline.** It is a max-lag search result.
   Report the design explicitly: "13/135 at a 5-year window; 7/135 after
   within-grid correction; 2/135 in a fixed 1–5-year joint test; 8/135 in the
   multiscale LASSO at 1–5 years."
2. **Do not report a 6.5-year median lag.** The distribution is bimodal and the
   median moves with the search window. Report the share of grids with lag ≤5
   (44–100% depending on window) or the fixed-window result.
3. **Drop long-run claims.** The 15–20-year tail is not ecologically distinct,
   is not supported by the multiscale model (0 grids at 11–20 years), and is not
   supported by the Qing benchmark.
4. **Keep the strong positive results**: GeoDetector severity q = 0.337 vs
   0.186/0.128; GWR 123/159 locally significant, median local R² 0.59; spatial
   mismatch between famine belts and the Jiangnan Jinshi core.
5. **This is still a publishable story**: "Famine severity dominates the
   geography of elite production, and short-horizon shocks predict Jinshi
   outcomes in a minority of grids; longer lags are a search artefact."

## 7b. Positive-findings inventory (what survives)

| Finding | Number | Robustness |
|---|---|---|
| Famine severity is the strongest factor | GeoDetector q = 0.337 (vs 0.186 longitude, 0.128 latitude) | unchanged v0.2 → v0.3 |
| Local effects are mostly positive | GWR 155 positive / 4 negative; 123/159 significant; global R² 0.759 | coefficient r = 0.991 between v0.2 and v0.3 |
| Short-horizon predictive signal | 8/135 (multiscale, fixed lags 1/3/5); 2/135 (fixed 1–5 joint); 13/135 (max_lag 5) | consistent across three designs |
| No medium/long-horizon signal | multiscale 0/135 at 5–10 and 0/135 at 10–20 | independent of Granger lag search |
| No record-intensity dose-response | proxy B +1.3 pp, proxy A +8.8 pp, both non-monotone | dose-response test, 3 and 4 levels |
| Time alignment | stable at ±1 and ±3 years (common support) | pre-registered Amendment 2 |
| Encoding fix does not move GWR | 122/125 significant-grid overlap; r = 0.991 | v0.2 vs v0.3 |

The weak link is the **size** of the grid-level signal (2–13 grids, not 48),
not its existence. The descriptive and spatially local results are strong.

## 8. Proposed next step (not done)

A birth-cohort test using `IndexYear`: 47.6% of records have age exactly 30,
which suggests imputation, so the cohort design is only partially identified.
If we use it, pre-register: exposure at birth and ages 0–5, grid fixed effects,
and a placebo cohort. This is the correct way to test the 20–30-year
early-life mechanism; it is not a Granger lag.

## 9. When this conclusion would fail

- If a pre-specified distributed-lag model with a defensible lag window finds
  a large short-horizon effect (it does not: 2/135).
- If block-permutation nulls (preserving autocorrelation) show the observed 48
  is within the null range (the iid permutation says it is above).
- If the Qing benchmark does not replicate on Ming data with the same design.
