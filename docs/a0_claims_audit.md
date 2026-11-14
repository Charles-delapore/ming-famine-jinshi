# A0 — claims and numbers audit (2026-11-14)

**Scope**: every public-facing number and claim in `README.md`, `README.zh.md`,
`index.html`, figure captions (`docs/figure_plan.md`, `docs/figure_qa.md`) and the
result docs. Each row is marked **keep / rewrite / delete**, with the replacement
text and its source.

**Decision rule** (roadmap §0 + `docs/long_tail_analysis.md` §7): strong
descriptive/spatial results stay; the uncorrected `48/135` and the `6.5-year
median lag` must not appear as headlines in public text. Historical / pre-registered
analysis records keep their numbers because they are the evidence trail, not
claims.

**Replacement wording (authoritative)**:

- Short-window signal: `2/135` (fixed 1–5 yr joint F test), `13/135`
  (max_lag=5 search), `8/135` (multiscale LASSO at 1–5 yr), `0/135` at 6–10 /
  11–20 yr.
- `48/135` is **only** a max_lag=20 search diagnostic (7/135 after within-grid
  Bonferroni); never a headline.
- `6.5-year median lag` is **deleted** as a headline: the lag distribution is
  bimodal and the median moves with the search window. Report short-lag share
  instead.
- Time alignment: common-support ±1 / ±3 yr shifts pass
  (`docs/p0_3b_salvage.md` §2).
- Record bias: no dose-response (proxy B +1.3 pp, proxy A +8.8 pp, both
  non-monotone; `docs/p0_3b_salvage.md` §3).

**Sources**: `data/derived/long_tail_fixed_lag.csv`,
`data/derived/long_tail_lag_window.csv`, `data/derived/p0_3b_time_common_support.csv`,
`data/derived/p0_3b_record_bias_levels.csv`, `output/v03/summary.json`,
`docs/long_tail_analysis.md`, `docs/p0_3b_salvage.md`,
`docs/v03_model_outputs.md`.

---

## 1. Audit table

| # | Location | Original claim | Decision | Replacement / note | Source |
|---|---|---|---|---|---|
| 1 | `README.md` Results | `48/135` FDR; `8/0/0` | **rewrite** | `2/135` fixed 1–5 yr joint; `13/135` 5-yr window; `8/135` multiscale; `0` medium/long; `48/135` labelled 20-lag diagnostic | `long_tail_fixed_lag.csv`, `long_tail_lag_window.csv` |
| 2 | `README.md` Results | `123/159` GWR; `q = 0.337` | **keep** | unchanged (strong result) | `v03_model_outputs.md`, `summary.json` |
| 3 | `README.md` Results | (none) | **add** | ±1/±3 yr alignment stable; no record-intensity dose-response | `p0_3b_salvage.md` |
| 4 | `README.zh.md` 主要结果 | `48/135`；`8`/`0` | **rewrite** | same as #1, Chinese | same |
| 5 | `README.zh.md` 主要结果 | `123/159`; `q = 0.337` | **keep** | unchanged | `v03_model_outputs.md` |
| 6 | `index.html` stat card | `48/135` "FDR-significant Granger grids" | **rewrite** | `2/135` "fixed 1–5 yr joint Granger (FDR)" | `long_tail_fixed_lag.csv` |
| 7 | `index.html` Findings | "survives FDR in 48 of 135" | **rewrite** | `2 of 135` fixed 1–5 yr (13/135 with 5-yr window); 48/135 explicitly a 20-lag artefact | `long_tail_analysis.md` §1–2 |
| 8 | `index.html` Fig. 2 caption | `(48/135)` | **rewrite** | fixed-window count; 48/135 only as supplement diagnostic | `long_tail_analysis.md` §7 |
| 9 | `index.html` Fig. 1 caption | `123/159`, `5,736`, `2,841` | **keep** | unchanged | `v03_model_outputs.md` |
| 10 | `index.html` Findings | `8` short / `0` medium-long; `q = 0.337/0.186/0.128` | **keep** | unchanged | `summary.json` |
| 11 | `docs/figure_plan.md` Fig. 2 core claim | `48/135` | **rewrite** | `2/135` fixed 1–5 yr (`13/135` 5-yr window) | `long_tail_fixed_lag.csv` |
| 12 | `docs/figure_plan.md` Fig. 2 "On figure" | `48/135 FDR-significant grids` | **rewrite** | `2/135` fixed-window; 48/135 = 20-lag diagnostic | `long_tail_lag_window.csv` |
| 13 | `docs/figure_plan.md` Fig. 2 caption | `48/135 grids with FDR-significant ...` | **rewrite** | `2/135 grids with fixed 1–5 yr FDR ...` | `long_tail_fixed_lag.csv` |
| 14 | `docs/figure_plan.md` Fig. 5 | `median significant lag 11.0 → 6.5` | **rewrite** | mark as bimodal selected lag, not a headline | `long_tail_analysis.md` §7 |
| 15 | `docs/figure_plan.md` Fig. 5 caption | `median significant lag shifts from 11 to 6.5` | **rewrite** | bimodal distribution note | `long_tail_analysis.md` §7 |
| 16 | `docs/figure_plan.md` Fig. 1 panel B | `Jinshi 1523–1619` | **rewrite** | `1521–1619` (roadmap A4) | `jinshi_provenance.md` (1521 cohort present) |
| 17 | `docs/figure_qa.md` Notes | `Current headline numbers are 48/135 ...` | **rewrite** | fixed-window headline + 48/135 diagnostic note | `long_tail_analysis.md` §7 |
| 18 | `docs/corrected_robustness.md` Reading | `v0.3 use 48/135, 123/159, 8/0/0 ...` | **rewrite** | `2/135` or `13/135`; 48/135 diagnostic | `long_tail_analysis.md` |
| 19 | `docs/corrected_robustness.md` Reading | `median significant lag shifts from 11 to 6.5` | **keep (context)** | v0.2/v0.3 comparison table, explicitly historical | `corrected_robustness.md` §table |
| 20 | `docs/v03_model_outputs.md` Reading notes | `56→48; 11→6.5 years` | **rewrite** | label as 20-lag search + bimodal | `long_tail_analysis.md` §1 |
| 21 | `docs/v03_model_outputs.md` metric table | `Median significant lag 11.0 / 6.5` | **keep (record)** | machine-readable model output, not a public claim | `summary.json` |
| 22 | `docs/jinshi_provenance.md` §6 | `from 56 to 48 of 135 ... median ... 6.5` | **rewrite** | add fixed-window count + bimodal note | `long_tail_fixed_lag.csv` |
| 23 | `docs/p0_3_preregistration.md` / amendments / `docs/p0_3_sensitivity.md` | `48/135`, `6.5 yr` | **keep (evidence trail)** | pre-registered baseline; changing it would rewrite history | pre-registration §7 |
| 24 | `docs/worklog_2026-11-14.md` | `56/135`, `48/135`, `6.5` | **keep (append-only)** | historical worklog, must not be edited | worklog header |
| 25 | `docs/long_tail_analysis.md`, `docs/p0_3b_salvage.md` | all numbers | **keep** | these are the diagnostic sources | — |
| 26 | `docs/p0_3_data_feasibility.md` | `48/135`, `6.5 yr` as baseline | **keep (dated memo)** | written before diagnostics; superseded, noted here | roadmap §0 |
| 27 | `docs/figure_plan.md` Fig. 4 caption | `1523/1526 spike` | **keep** | encoding-artefact fact, not a headline claim | `jinshi_encoding_audit.md` |
| 28 | `docs/figure_plan.md` Fig. 1/3 captions | `5,736`, `2,841`, `123/159`, `q` | **keep** | strong descriptive results | `v03_model_outputs.md` |

Summary: **rewrite 13**, **keep 14** (of which 4 explicitly labelled as evidence
trail / historical), **delete 1** (the `6.5-year median` as a headline),
**add 1** (robustness sentence).

## 2. Acceptance

- [x] One claims table (this file).
- [x] `scripts/a0_apply_claims.py` applies every rewrite reproducibly.
- [x] After the rewrite, no public file contains an uncorrected `48/135`
      headline; the remaining occurrences are in evidence-trail documents and
      are explicitly labelled as diagnostics.
- [x] No `6.5-year median lag` headline remains in `README*`, `index.html`,
      figure captions or site text.

## 3. When this audit would fail

- A new public page or caption is added without going through this table.
- A result table is regenerated with different numbers but the text is not
  updated (A3/A8 re-check this).
- `48/135` reappears as a headline in any public file; re-run
  `python scripts/a0_apply_claims.py --check`.
