# A6 — paper outline (2 pages, 2026-11-14)

**Positioning (decided by evidence, not ambition).** A1 (rank share) and A2
(spatial spillover) are both **null** under their pre-registrations. Roadmap
§1.4 therefore fixes the paper as **descriptive + methodological**, targeting
the *stable* journal tier. No amount of respecification is used to manufacture
a result.

## Working title

*Famine severity and the geography of Ming elite production: a 1° grid panel,
a small short-window signal, and a warning about lag searching*

## Structure (section by section)

**1. Introduction.** Ming examination geography (Jiangnan concentration,
north–south imbalance) meets environmental shocks. Two gaps: (i) most existing
work is descriptive or uses aggregated provincial counts; (ii) climate–exam
studies report lag structures that depend on how many lags the search tries.
We ask three questions: how unequal is Jinshi production spatially; does famine
history *predict* later Jinshi in a short window; and how fragile is that claim
to specification and record bias.

**2. Data.** 5,736 famine records (Hu Peng, *Ming famine database*), CBDB
`入仕查询结果` export (28,761 rows; 2,841 mapped normalized 1甲/2甲 elite;
5,401 records in the grid panel after adding `ming_general`), CHGIS v6
basemap, 1° grid × 114 years (1506–1619). Explicitly document the
rank-encoding defect (`第1甲|第2甲` Arabic-only filter) and its correction
(`src/data_processing/jinshi_rank.py`), plus the 2,855 confirmed civil lower
bound. Raw tables are not redistributed; aggregate tables and synthetic
schema-matching samples are.

**3. Spatial inequality (strong result).** Famine belts vs Jiangnan Jinshi
core (partial overlap). GeoDetector q = 0.3368 (severity) vs 0.1857
(longitude) / 0.1284 (latitude). GWR: 123/159 locally significant, 155
positive / 4 negative, global R² = 0.759. The encoding fix leaves coefficients
at r = 0.9914 and 122/125 significant grids overlapping. Figures 1, 4.

**4. Short-window test (small but reproducible result).** Report the design
explicitly: fixed 1–5 year joint F test **2/135**; pre-specified max_lag=5
**13/135**; multiscale LASSO **8/135** at 1–5 yr, **0/135** at 5–10 and
11–20 yr. Frame as "a minority of grids show short-horizon predictive
association", never as general causation. Granger is predictive, not
mechanistic. Figure 2 (fixed-window main figure).

**5. Robustness and the methodological warning (the core contribution).**
48/135 is a max_lag=20 search artefact (13→26→34→48 as the window grows;
7/135 after within-grid Bonferroni; iid and block permutation nulls average
~7.2 discoveries). The 6.5-year median comes from a bimodal lag distribution
(1–3 or 15–20 yr) and is not reported. Common-support ±1/±3-year shifts pass
the frozen criteria; there is no record-intensity dose-response (proxy B
+1.3 pp, proxy A +8.8 pp, both non-monotone). A1 rank-share null (coef
0.000283, permutation p = 0.935); A2 direct/spillover null. Coordinate
confidence is **not testable** with available fields (Amendments 1–2):
`xy_count` counts records sharing a coordinate, not precision.

**6. Discussion.** Quotas (南/北/中卷 55/35/10 after 1435) constrain counts by
region; family background and recording intensity are omitted variables; the
Qing benchmark (Li, Liao & Teng 2026, *World Development*, 1- and 5-year
drought windows, small negative effects) supports a short horizon, not 15–20
years. The thesis's 20-year "inhibition" claim is a hypothesis, not a result
(cohort probe gives a positive, documentation-driven sign). Limits: 1° MAUP,
47.6% imputed exam age (`IndexYear = EntryYear − 30`), no subjective
well-being data.

**7. Methods.** Full reproduction chain in `docs/a3_main_results.md`;
pre-registrations (`p0_3_preregistration.md` + Amendments 1–2,
`a1_rank_preregistration.md`, `a2_spillover_preregistration.md`); claims audit
`a0_claims_audit.md`; environment in `docs/a7_reproducibility_pack.md`.

## Three contributions (exactly three)

1. **A reproducible panel + audit trail for Ming elite geography**: every
   headline number has a script → table → document chain, including the
   rank-encoding correction that changes counts but not spatial conclusions.
2. **A quantified methodological warning about lag searching**: we show how a
   20-lag search inflates 2–13 short-window discoveries into 48, and supply
   fixed-window, Bonferroni and permutation benchmarks that other historical
   climate–exam studies can adopt.
3. **Robustness boundaries**: common-support time perturbation and a
   record-intensity dose-response test delimit what the short-window signal
   can and cannot claim; two pre-registered extensions (rank composition,
   spatial spillover) are reported as nulls rather than omitted.

## Journal tiers (roadmap §1.2 A6, adjusted by the nulls)

| Tier | Venues | Status |
|---|---|---|
| Stable (target) | *Digital Scholarship in the Humanities*, *Historical Methods*, *Journal of Historical Geography* | **viable now** — descriptive + methodological framing |
| Stretch | *World Development*, *Economic History Review* | **not viable on current evidence**; requires B1 quota moderator and/or B2 multi-hazard contrast (see `docs/b_feasibility_memo.md`) |

## When this outline would fail

- If A1/A2 are re-run with a different pre-registration and become
  non-null, the "descriptive + methodological" positioning must be revisited
  (but only via a dated amendment).
- If B returns Go and an institutional moderator is added, the stretch tier
  and the contribution list must be rewritten.
- If any headline number in `docs/a3_main_results.csv` changes, sections 3–5
  must be regenerated from the assembler.

## Output

2-page outline (this file), three contributions, journal tiers. No new
analysis was run for this work package.
