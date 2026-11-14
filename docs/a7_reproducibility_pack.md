# A7 — reproducibility pack (2026-11-14)

One command list, a locked environment, and two independent checks. Raw
historical tables are private; the synthetic path verifies code and layout,
never the published numbers.

## 1. Locked environment (measured on 2026-11-14)

| Component | Version |
|---|---|
| Python | 3.13.13 |
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| openpyxl | 3.1.5 |
| pytest | 9.0.3 |
| geopandas | 1.1.3 |
| statsmodels, scikit-learn, matplotlib, mgwr, networkx | installed (see `requirements-*.txt`) |

`core.autocrlf=true` on this Windows checkout; line-ending noise is handled by
restoring `README*` after each commit (see the worklog).

## 2. Synthetic path (no private data)

```bash
python scripts/make_sample_data.py
python scripts/run_sample_figures.py        # writes figures/sample/ (fig 1-4)
python tools/verify_sample_reproducibility.py
python -m pytest -q
```

- `verify_sample_reproducibility.py` runs the generator twice in fresh
  interpreters and compares all 14 tables cell-by-cell and in row order.
  **Result: run-to-run 14/14 PASS; generated vs committed HEAD 14/14 PASS.**
- `run_sample_figures.py` verified on 2026-11-14: fig1–fig4 each exported as
  PDF + SVG + PNG into `figures/sample/`.
- `pytest -q`: **5 passed**.

## 3. Real-data path (private inputs required)

Environment variables (see `docs/v03_model_outputs.md`):

```bat
set MING_JINSHI_RAW=<path to the private CBDB export>
set MING_FAMINE_MERGED=<path to the private famine table>
set MING_FAMINE_EXT=<path to the private famine export>
set MING_CITYS=<path to the private city points>
set MING_JINSHI_ALL=<path to the private Jinshi extension>
set MING_OUTPUT=ming-portfolio\output\v03\fig_input
set MING_BASEMAP=<private province shapefile>
```

```bash
python scripts/corrected_robustness.py        # panel, Granger, GWR, summary.json
python scripts/build_v03_figure_inputs.py    # multiscale + GeoDetector tables
python scripts/long_tail_analysis.py         # fixed-lag + lag-window diagnostics
python scripts/p0_3b_salvage.py              # common-support + record-bias
python scripts/a1_rank_analysis.py           # A1 rank share (null)
python scripts/a2_spillover_analysis.py      # A2 spillover (null)
python scripts/a3_assemble_main_results.py   # the single main-results table
python scripts/fig1_patterns.py              # re-render Figure 1 (1521-1619)
python scripts/fig2_fixed_window.py          # fixed-window main figure
python scripts/a4_figure_qa.py               # format / dpi / colour-blind QA
python scripts/a0_apply_claims.py --check    # public-wording acceptance
```

## 4. Verification results (2026-11-14)

| Check | Command | Result |
|---|---|---|
| sample determinism | `python tools/verify_sample_reproducibility.py` | 14/14, twice, and vs HEAD |
| unit tests | `python -m pytest -q` | 5 passed |
| public wording | `python scripts/a0_apply_claims.py --check` | PASS, 0 issues |
| figure QA | `python scripts/a4_figure_qa.py` | 0 format/dpi issues, 0 colour-blind missing |
| sample figures | `python scripts/run_sample_figures.py` | fig1–4 in PDF/SVG/PNG |
| main numbers | `python scripts/a3_assemble_main_results.py` | 29 metrics, one panel |

## 5. Acceptance

- [x] `data/sample/` synthetic tables run figures 1–4.
- [x] One command list (§2–§3).
- [x] Environment locked (§1).
- [x] Clean-environment two-run consistency (14/14).

## 6. When this would fail

- A private input path changes without updating `MING_*`.
- A source table is regenerated without re-running `a3_assemble_main_results.py`
  (A8 re-checks this).
- `shap` or other optional packages are assumed present; they are not installed
  and no network install is performed in this session.

Private inputs; aggregate outputs only.
