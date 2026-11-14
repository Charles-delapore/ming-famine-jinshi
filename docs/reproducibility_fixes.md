# Reproducibility fixes

This file records the three reproducibility issues flagged in the 2026-11-14
digital-humanities review, plus the changes made in this repository.

## 1. Deterministic row order

`run_pipeline.py` now sorts every exported table before writing:

- `merged_data`: `year, code, x, y`
- `clustered_levels`: `year, code, x, y, cluster`
- `clustered_jinshi`: `EntryYear, NameChn, X, Y, cluster`

The synthetic sample generator already sorts event tables; the real pipeline
output is now stable across runs (assuming the same input rows). This does not
change any value, only the row order.

## 2. Data-driven colour limits

The figure scripts no longer hard-code the map colour ranges:

- `fig1_patterns.py`: GWR coefficient norm uses the observed min/max with a
  zero centre.
- `fig2_mechanism.py`: local R² norm uses the observed min/max with a zero centre.
- `fig3_framework.py`: the shared GWR norm uses the same observed range.

The colorbars therefore reflect the data actually plotted. Extreme values are
not clipped; if a future run has a long tail, review the map before publication.

## 3. `GRID_PARAMS["y_max"]`

The original value `120.257776` is not a valid latitude. It has been corrected
to `50.257776`; the grid data used in the published results cover roughly
18–41°N. This parameter is only used by `grid_integrator` when building a new
grid; it did not change the existing result tables.

## 4. `max_cluster_size = 100` — retained, documented

The cap is retained because changing it would alter the exploratory clustering
and every receipt/result tied to it. It is now explicitly documented in
`src/config.py` and `src/README.md`:

> The labels are exploratory partitions of dense areas, not natural clusters.
> They are not used as inferential evidence in the portfolio figures.

The 3D rainbow cluster figures remain retired; the hero figures use map and
grid-level evidence instead.

## 5. Jinshi sample provenance

Confirmed in `docs/jinshi_provenance.md`: the source is the CBDB
`入仕查询结果` export. The 911-record layer is an **Arabic-numeral-coded**
1甲/2甲 subset, not a representative sample; see item 7 below. The aggregate
audits are `docs/jinshi_sample_audit.md` and `docs/jinshi_encoding_audit.md`.

## 6. Zenodo DOI

Metadata is prepared in `.zenodo.json` and `docs/zenodo_release.md`. Minting the
DOI requires the author's Zenodo account and a GitHub release; the repository
does not claim a DOI until that step is complete.

## 7. Jinshi rank encoding (2026-11-14)

The 911-record layer is not a rank-complete sample: the old filter
`EntryRank.str.contains("第1甲|第2甲")` matched only Arabic-numeral ranks
(`第1甲`), dropping Chinese-numeral ranks (`第一甲`). The corrected elite
denominator for 1521–1619 is **2,855 confirmed lower bound** (2,853 strict regex; 2,841 with coordinates).
The 1523/1526 concentration is an encoding artefact, not a historical cohort.
See `docs/jinshi_provenance.md`, `docs/jinshi_encoding_audit.md`, and
`scripts/audit_jinshi_encoding.py`.

**Status:** fixed and re-run (v0.3). `src/data_processing/jinshi_rank.py`
normalizes both numeral systems; `loader.py` and `ss_dbscan.py` use it. Figures
1–5 are regenerated from the normalized elite (2,841). The direct sensitivity
check is `docs/corrected_robustness.md` and `figures/fig5_correction.*`.


