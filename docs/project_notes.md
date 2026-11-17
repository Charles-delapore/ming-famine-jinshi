# Project notes

Technical details moved out of the README: data scope, reproducibility,
documentation index, synthetic sample, extended limitations and next steps.

## Data scope

- The 2,841 mapped 1甲/2甲 Jinshi records drive the point maps.
- The grid models aggregate a broader Jinshi series: `ming_general` plus the
  elite extension, 5,401 records in the panel.
- The repository contains analysis code, figure scripts, synthetic sample data
  and aggregate outputs. Raw historical tables are not redistributed.

## Analysis layer

- `src/` contains the analysis modules; the module map is in
  [`../src/README.md`](../src/README.md).
- The 14-step orchestrator is `run_pipeline.py`.
- Full dependencies: `requirements-analysis.txt`; the optional CGAN branch is
  in `requirements-ml.txt`.
- Figure scripts read result tables from `MING_OUTPUT` (default: `output/`) and
  write PDF + SVG + 600 dpi PNG to `figures/`.
- The shared style module is `style/ming_style.py`.

## Documentation index

- Design rationale: [`design_notes.md`](design_notes.md)
- Figure contracts and style rules: [`figure_plan.md`](figure_plan.md)
- Figure QA and colour-blind checks: [`figure_qa.md`](figure_qa.md)
- Reproducibility fixes: [`reproducibility_fixes.md`](reproducibility_fixes.md)
- v0.3 worklog: [`worklog_2026-11-14.md`](worklog_2026-11-14.md)
- Corrected-grid sensitivity: [`corrected_robustness.md`](corrected_robustness.md)
- Jinshi provenance: [`jinshi_provenance.md`](jinshi_provenance.md)
- Jinshi rank-encoding audit: [`jinshi_encoding_audit.md`](jinshi_encoding_audit.md)
- Data provenance overview: [`data_provenance.md`](data_provenance.md)
- Data dictionary for published aggregates: [`data_dictionary.md`](data_dictionary.md)
- Corrected Jinshi aggregates: [`../data/derived/`](../data/derived/README.md)
- v0.3 model metrics and unparsed-rank audit:
  [`v03_model_outputs.md`](v03_model_outputs.md),
  [`jinshi_unparsed_audit.md`](jinshi_unparsed_audit.md),
  [`data_boundary_audit.md`](data_boundary_audit.md)
- Interactive map notes: [`../web/README.md`](../web/README.md)
- Zenodo release steps: [`zenodo_release.md`](zenodo_release.md) (DOI pending)`n- Release checklist: [`release_checklist.md`](release_checklist.md)

Data sources and transformations are also recorded in the figure footnotes.

## Route A analyses (2026-11-14/15)

- **Claims and freeze**: [`a0_claims_audit.md`](a0_claims_audit.md),
  [`a0_apply_report.md`](a0_apply_report.md), [`a8_freeze_review.md`](a8_freeze_review.md)
- **Main results**: [`a3_main_results.md`](a3_main_results.md) — fixed 1–5 year
  joint test, multiscale horizons, GWR and GeoDetector in one table
- **Rank and spillover (nulls)**: [`a1_rank_results.md`](a1_rank_results.md),
  [`a2_spillover_results.md`](a2_spillover_results.md)
- **Lag-search diagnostics**: [`long_tail_analysis.md`](long_tail_analysis.md),
  [`p0_3b_salvage.md`](p0_3b_salvage.md)
- **Data and replication**: [`a9_new_data_inventory.md`](a9_new_data_inventory.md),
  [`a10_coordinate_confidence_results.md`](a10_coordinate_confidence_results.md),
  [`a12_full_ming_replication.md`](a12_full_ming_replication.md),
  [`a13_admin_density_proxy.md`](a13_admin_density_proxy.md),
  [`a15_external_famine_crosscheck.md`](a15_external_famine_crosscheck.md)
- **Network and early Ming**: [`a17_cbdb_network_coverage.md`](a17_cbdb_network_coverage.md),
  [`a18_ego_network_results.md`](a18_ego_network_results.md),
  [`a19_early_ming_decomposition.md`](a19_early_ming_decomposition.md)
- **Planning**: [`a6_paper_outline.md`](a6_paper_outline.md),
  [`a7_reproducibility_pack.md`](a7_reproducibility_pack.md),
  [`b_feasibility_memo.md`](b_feasibility_memo.md)

The published aggregate tables are listed in
[`../data/derived/README.md`](../data/derived/README.md); person-level and
unlicensed external tables are kept private.

## Synthetic sample data

The real event tables are private. `data/sample/` contains synthetic tables with
identical columns (seed `20261113`), for code and figure checks without
redistributing historical records or the CHGIS basemap.

```bash
python scripts/make_sample_data.py
python scripts/run_sample_figures.py   # writes figures/sample/ (fig 1–4)
python scripts/make_interactive_map.py --sample --output web/sample/interactive_map.html
```

The sample figures carry a “synthetic sample” footnote. See
[`../data/sample/README.md`](../data/sample/README.md) for provenance and
limitations.

## Extended limitations

- Historical records are not a random sample; reporting intensity varies by
  region and period.
- The earlier 911-record Jinshi layer was a format-selected subset of the CBDB
  1甲/2甲 elite (Arabic-numeral ranks only), not a representative sample. The
  v0.3 figures use the normalized elite (2,841 mapped records; confirmed civil
  lower bound 2,855 before the coordinate filter; upper 3,104). The 911 layer is
  retained only as an audit. See [`jinshi_provenance.md`](jinshi_provenance.md),
  [`jinshi_encoding_audit.md`](jinshi_encoding_audit.md) and
  [`corrected_robustness.md`](corrected_robustness.md).
- Granger causality is predictive, not mechanistic: “famine → Jinshi” means
  famine history improves prediction of later Jinshi counts.
- Grid-level results are sensitive to the 1° resolution; the sensitivity
  analysis is reported separately in the project outputs.
- SHAP/GeoShapley, STL and CCM were not re-estimated on the v0.3 panel. Their
  qualitative conclusions are unchanged, but exact values in older tables may
  shift; the v0.3 re-run covers Granger, GWR, multiscale LASSO and GeoDetector.
- CCM is not identifiable with these zero-inflated series.

## Next steps

- Bayesian hierarchical version with spatial random effects and reporting-bias
  terms.
- Multi-resolution sensitivity surface (0.5°/1°/2°) and stability of the
  significant cells.
- Reporting-bias and coordinate-confidence sensitivity for the v0.3 panel.


