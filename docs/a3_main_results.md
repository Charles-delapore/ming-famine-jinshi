# A3 — main results, one panel (2026-11-14)

- Generated: 2026-11-14 17:00
- Command: `python scripts/a3_assemble_main_results.py`
- Claim audit: `docs/a0_claims_audit.md` (all public wording follows this table).

## One panel

All four headline analyses use `output/v03/panel_v03.csv.gz` (291 1° grids × 114 years, 1506–1619; 5,401 Jinshi records in the grid models). The famine series is identical between v0.2 and v0.3; only the Jinshi layer was corrected, so GeoDetector/GWR descriptive results are stable while the lag-search diagnostics are not.

## Main results (script → table → document)

| Metric | Value | Script | Table | Document | Note |
|---|---:|---|---|---|---|
| `panel_grid_years` | 33174 | `scripts/corrected_robustness.py` | `output/v03/panel_v03.csv.gz` | docs/a3_main_results.md | 291 grids x 114 years, 1506-1619 |
| `panel_grids` | 291 | `scripts/corrected_robustness.py` | `output/v03/panel_v03.csv.gz` | docs/a3_main_results.md |  |
| `panel_jinshi_records` | 5401 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/v03_model_outputs.md | ming_general + normalized elite extension |
| `fixed_1_5_joint_FDR_grids` | 2 | `scripts/long_tail_analysis.py` | `data/derived/long_tail_fixed_lag.csv` | docs/long_tail_analysis.md §2 | PRIMARY short-window result |
| `multiscale_1-5_FDR_grids` | 8 | `scripts/build_v03_figure_inputs.py` | `output/v03/fig_input/multiscale_causal_short_term.xlsx` | docs/v03_model_outputs.md | column used: fdr_significant |
| `multiscale_5-10_FDR_grids` | 0 | `scripts/build_v03_figure_inputs.py` | `output/v03/fig_input/multiscale_causal_medium_term.xlsx` | docs/v03_model_outputs.md | column used: fdr_significant |
| `multiscale_11-20_FDR_grids` | 0 | `scripts/build_v03_figure_inputs.py` | `output/v03/fig_input/multiscale_causal_long_term.xlsx` | docs/v03_model_outputs.md | column used: fdr_significant |
| `GWR_significant` | 123 | `scripts/corrected_robustness.py` | `output/v03/gwr_v03.xlsx` | docs/corrected_robustness.md | |t|>1.96 |
| `GWR_cells` | 159 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/v03_model_outputs.md |  |
| `GWR_positive` | 155 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/v03_model_outputs.md |  |
| `GWR_negative` | 4 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/v03_model_outputs.md |  |
| `GWR_global_R2` | 0.7588 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/v03_model_outputs.md |  |
| `GWR_coef_r_v02_v03` | 0.9914 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/corrected_robustness.md | encoding fix robustness |
| `significant_grid_overlap` | 122 | `scripts/corrected_robustness.py` | `output/v03/summary.json` | docs/corrected_robustness.md | of 125 v0.2 grids |
| `GeoDetector_q_severity` | 0.3368 | `scripts/build_v03_figure_inputs.py` | `output/v03/fig_input/geodetector_results.xlsx` | docs/v03_model_outputs.md |  |
| `GeoDetector_q_longitude` | 0.1857 | `scripts/build_v03_figure_inputs.py` | `output/v03/fig_input/geodetector_results.xlsx` | docs/v03_model_outputs.md |  |
| `GeoDetector_q_latitude` | 0.1284 | `scripts/build_v03_figure_inputs.py` | `output/v03/fig_input/geodetector_results.xlsx` | docs/v03_model_outputs.md |  |
| `max_lag_5_FDR` | 13 | `scripts/long_tail_analysis.py` | `data/derived/long_tail_lag_window.csv` | docs/long_tail_analysis.md §1 | search-window diagnostic |
| `max_lag_5_short_lag_share` | 1.0 | `scripts/long_tail_analysis.py` | `data/derived/long_tail_lag_window.csv` | docs/long_tail_analysis.md §1 |  |
| `max_lag_20_FDR` | 48 | `scripts/long_tail_analysis.py` | `data/derived/long_tail_lag_window.csv` | docs/long_tail_analysis.md §1 | search-window diagnostic |
| `within_grid_Bonferroni_20` | 7 | `scripts/long_tail_analysis.py` | `data/derived/long_tail_lag_window.csv` | docs/long_tail_analysis.md §1 | 48/135 is a search artefact |
| `common_support_baseline_FDR` | 46 | `scripts/p0_3b_salvage.py` | `data/derived/p0_3b_time_common_support.csv` | docs/p0_3b_salvage.md §2 | restricted window 1511-1614, 133 grids |
| `common_support_pm1_pass` | True | `scripts/p0_3b_salvage.py` | `data/derived/p0_3b_time_common_support.csv` | docs/p0_3b_salvage.md §2 | within ±25% of restricted baseline |
| `common_support_pm3_pass` | True | `scripts/p0_3b_salvage.py` | `data/derived/p0_3b_time_common_support.csv` | docs/p0_3b_salvage.md §2 | within ±40% of restricted baseline |
| `record_bias_B_gap_pp` | 1.3 | `scripts/p0_3b_salvage.py` | `data/derived/p0_3b_record_bias_levels.csv` | docs/p0_3b_salvage.md §3 | non-monotone; no dose-response |
| `record_bias_A_gap_pp` | 8.8 | `scripts/p0_3b_salvage.py` | `data/derived/p0_3b_record_bias_levels.csv` | docs/p0_3b_salvage.md §3 | non-monotone; no dose-response |
| `A1_rank_share_coef` | 0.000283 | `scripts/a1_rank_analysis.py` | `data/derived/a1_rank_coefficients.csv` | docs/a1_rank_results.md | NULL: CI includes 0, permutation p=0.935 |
| `A2_direct_coef` | 0.006126 | `scripts/a2_spillover_analysis.py` | `data/derived/a2_spillover_coefficients.csv` | docs/a2_spillover_results.md | NULL: CI includes 0 |
| `A2_spillover_coef` | 0.019376 | `scripts/a2_spillover_analysis.py` | `data/derived/a2_spillover_coefficients.csv` | docs/a2_spillover_results.md | NULL: CI includes 0 |

## Authoritative headline

- **Spatial inequality**: GeoDetector q = 0.3368 (severity) vs 0.1857 (longitude) / 0.1284 (latitude); GWR locally significant in 123/159 grids, 155 positive / 4 negative, global R² = 0.759.
- **Short-window signal**: a fixed 1–5 year joint Granger test is FDR-significant in **2/135** grids; a pre-specified 5-year search window gives **13/135**; multiscale LASSO gives **8/135** at 1–5 years and **0/135** at 5–10 / 11–20 years.
- **Methodological warning**: `48/135` is a max_lag=20 search artefact (7/135 after within-grid Bonferroni); the 6.5-year median lag comes from a bimodal distribution and is not reported.
- **Robustness**: common-support ±1 and ±3 year shifts pass; no record-intensity dose-response; encoding fix leaves GWR coefficient r = 0.991 (122/125 significant-grid overlap).
- **A1/A2 zero results**: famine does not shift the 1甲/2甲 share (A1 null) and neither local nor neighbouring famine predicts Jinshi counts in the NB model (A2 null). Per roadmap §1.4 the paper is positioned as **descriptive + methodological**, targeting the stable journal tier.

## Reproduce (third party)

```bash
python scripts/corrected_robustness.py        # panel, Granger, GWR, summary.json
python scripts/build_v03_figure_inputs.py    # multiscale + GeoDetector tables
python scripts/long_tail_analysis.py         # fixed-lag + lag-window diagnostics
python scripts/p0_3b_salvage.py              # common support + record bias
python scripts/a1_rank_analysis.py           # A1 rank share
python scripts/a2_spillover_analysis.py      # A2 spillover
python scripts/a3_assemble_main_results.py   # this table
python scripts/a0_apply_claims.py --check    # public-wording acceptance
```

Private raw inputs (`明进士.xlsx`, `merged_data.csv`, `ming_general.csv`, `table_citys.xlsx`, `table_generals1521_1619.xlsx`) are required for the first two commands; see `docs/v03_model_outputs.md` for the `MING_*` environment variables. The synthetic `data/sample/` path can only verify code/layout, never these numbers.

## When this would fail

- Any source table is regenerated with different numbers without re-running this assembler (A8 re-checks it).
- A new public claim is added outside `docs/a0_claims_audit.md`.
- The panel window or grid resolution changes; all four analyses would need re-estimation.

Machine-readable: `data/derived/a3_main_results.csv`.

Private inputs; aggregate outputs only.
