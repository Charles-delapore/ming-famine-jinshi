# A8 — internal review and freeze (2026-11-14)

**Decision: route A is closed.** All work packages A0–A8 are complete; the
version is frozen locally. The freeze predates the publication step, so the
commit cadence in roadmap §1.2 A8 does not apply to this snapshot.

## 1. A0 claims audit, checked row by row

`docs/a0_claims_audit.md` has 28 rows. Re-check at freeze:

| Decision class | Count | Re-check result |
|---|---:|---|
| rewrite | 13 | all applied by `scripts/a0_apply_claims.py` (16 rewrite rules + 2 follow-ups); `--check` → PASS, 0 issues |
| keep | 14 | unchanged; 4 explicitly labelled evidence-trail / historical (pre-registration, worklog, sensitivity, long-tail diagnostics) |
| delete | 1 | `6.5-year median lag` removed as a headline from README*, index.html, figure captions and result docs |
| add | 1 | robustness sentence (±1/±3 alignment, no dose-response) present in both READMEs |

Explicit verification: `python scripts/a0_apply_claims.py --check` → **PASS (0
issues)**. No uncorrected `48/135` headline and no `6.5` string in public
pages. The remaining `48/135` occurrences are all in evidence-trail documents
and are qualified as diagnostics.

## 2. Work-package acceptance

| WP | Deliverable | Result |
|---|---|---|
| A0 | `docs/a0_claims_audit.md`, `scripts/a0_apply_claims.py` | PASS — 28-row table, 0 wording issues |
| A1 | `docs/a1_rank_preregistration.md`, `scripts/a1_rank_analysis.py`, results | **NULL** (coef 0.000283, 95% CI [−0.0059, 0.0065], permutation p = 0.935); stopped as pre-registered |
| A2 | `docs/a2_spillover_preregistration.md`, `scripts/a2_spillover_analysis.py`, results | **NULL** (direct 0.0061, spillover 0.0194; both CIs include 0); stopped as pre-registered |
| A3 | `docs/a3_main_results.md`, `scripts/a3_assemble_main_results.py` | PASS — 29 metrics with script → table → document chain on one panel |
| A4 | `docs/a4_figure_qa.md`, `scripts/fig2_fixed_window.py`, `scripts/a4_figure_qa.py` | PASS — fig1 year corrected and re-rendered; new fixed-window main figure; fig2/fig5 demoted to supplementary; 0 format/dpi issues, 0 colour-blind missing |
| A5 | `README.md`, `README.zh.md`, `index.html` | PASS — 27 / 14 lines (limits 30 / 20); site shows only spatial pattern, short-window result, GWR/GeoDetector, methodological warning |
| A6 | `docs/a6_paper_outline.md` | PASS — 2-page outline, exactly 3 contributions, journal tiers adjusted to the stable tier because A1/A2 are null |
| A7 | `docs/a7_reproducibility_pack.md` | PASS — locked environment, command list, 14/14 twice, pytest 5 passed, sample fig1–4 exported |
| A8 | this file | PASS — frozen locally, not pushed |
| B | `docs/b_feasibility_memo.md` | PASS — exploratory only; no B model, no public-text change; search leads recorded |

## 3. Verification commands re-run at freeze

```bash
python scripts/a0_apply_claims.py --check    # PASS 0 issues
python tools/verify_sample_reproducibility.py # 14/14 run-to-run, 14/14 vs HEAD
python -m pytest -q                          # 5 passed
python scripts/a4_figure_qa.py               # 0 issues
python scripts/a3_assemble_main_results.py   # 29 metrics
python scripts/run_sample_figures.py         # fig1-4 PDF/SVG/PNG
```

## 4. Roadmap failure conditions, resolved

| Roadmap §1.4 condition | Outcome |
|---|---|
| A1/A2 both null → descriptive + methodological, stable journals | **occurred**; A6 targets DSH / Historical Methods / J. Historical Geography; stretch tier deferred pending B |
| A5 rank result conflicts with count result | did not occur (A1 null) |
| A2 spillover dominates → rewrite A3 as "regional famine" | did not occur (A2 null) |

## 5. Freeze boundary

- Frozen: all public text, `docs/a3_main_results.csv`, the pre-registrations,
  the claims audit, figure statuses and the reproduction command list.
- **Not pushed**: `origin/main` is untouched by this session; the freeze is a
  local commit on `local/p0-3b-20261114`.
- Route C (birth-cohort, Ming–Qing replication) stays frozen per roadmap §3.
- Route B stays at "plan only" until a dated Go decision.

## 6. Remaining (explicitly outside this freeze)

1. A1/A2 nulls are final under their pre-registrations; any re-run needs a new
   dated amendment, not a specification tweak.
2. Coordinate-confidence sensitivity (P0-3 step 2) remains **not testable**
   with available fields; `xy_count` is record density, not precision.
3. SHAP (P1-1) remains open — `shap` is not installed and no network install
   was performed.
4. B1 quota moderator and B2 hazard-typed table need external data suppliers.
5. Push, Zenodo DOI and GitHub release are intentionally deferred.

## 7. When this freeze would fail

- Any headline number in `data/derived/a3_main_results.csv` changes without
  re-running A3 + A8.
- A public page is edited without re-running `a0_apply_claims.py --check`.
- A B model is run or a threshold is changed without a dated Go/amendment.

Private inputs; aggregate outputs only.
