# Data dictionary — published aggregates

Only aggregate counts, coefficients or grid-level summaries are published.
Person-level links, full event tables and unlicensed external tables are not in
the repository. The authoritative file list is
[`../data/derived/README.md`](../data/derived/README.md).

| Family | Files | Grain | Key columns | Use |
|---|---|---|---|---|
| Main results | `a3_main_results.csv` | one row per metric | `metric`, `value`, `script`, `table`, `document` | single source for headline numbers |
| Rank share | `a1_rank_coefficients.csv`, `a1_rank_units.csv` | grid × exam year | `share_top`, `famine_1_5`, `total` | A1 null result |
| Spillover | `a2_spillover_coefficients.csv`, `a2_spillover_units.csv` | grid × exam year | `jinshi_count`, `direct`, `spillover` | A2 null result |
| Coordinate confidence | `a10_coordinate_tiers_summary.csv`, `a10_coordinate_sensitivity.csv`, `a10_late_ming_geography.csv`, `a10_external_city_crosscheck.csv` | tier / grid | `tier`, `n`, `share` | tier composition and sensitivity |
| Full-Ming replication | `a12_full_ming_cities.csv`, `a12_full_ming_fixed_lag.csv`, `a12_full_ming_lag_window.csv` | city / lag set / max-lag | `fdr_sig`, `median_lag`, `grids` | independent replication |
| Administrative density | `a13_admin_density_dose.csv` | dose level | `proxy`, `level`, `fdr_rate` | record-intensity dose response |
| External famine | `a15_external_famine_summary.csv`, `a15_external_famine_crosscheck.csv` | source / match class | `n`, `matched_share` | external chronology cross-check |
| Elite network | `a14_network_coverage.csv`, `a17_cbdb_network_coverage.csv`, `a18_ego_network_summary.csv`, `a18_grid_correlations.csv` | audit / ego summary / grid | `coverage`, `ego_coverage`, `degree` | network coverage and descriptive summary |
| Early Ming | `a19_early_ming_decomposition.csv` | window | `grids_tested`, `fdr_sig`, `share` | early/late decomposition |
| Lag diagnostics | `long_tail_*.csv` | lag set / shift / replicate | `fdr_sig`, `median_lag`, `short_share` | fixed window and null calibration |
| P0-3 sensitivity | `p0_3_*.csv`, `p0_3b_*.csv` | proxy / shift / grid | `fdr_rate`, `gap_pp`, `median_lag` | record bias, time alignment |
| STL | `p1_1_*.csv` | grid / metric | `sig_trend`, `sig_resid`, `r` | v0.2/v0.3 STL comparison |
| Jinshi totals | `jinshi_by_year_1521_1619.csv`, `jinshi_rank_summary.csv`, `jinshi_unparsed_summary.csv` | exam year / rank class | `records`, `unparsed`, `elite` | denominator audit |
| Model summary | `v03_model_summary.csv` | panel version | `granger_fdr_sig`, `gwr_sig`, `q` | v0.2/v0.3 aggregate comparison |

## Conventions

- `grid_x`, `grid_y` are 1° cell centres (`floor(coord) + 0.5`).
- `fdr_sig` is the Benjamini–Hochberg decision at α = 0.05.
- `qval` is the BH-adjusted p-value.
- `lag` is in years, selected by the max-F rule unless a fixed window is named.
- `famine_1_5` is the sum of famine severity over lags 1–5.

## Not published

Person-level links, ego degrees, full famine events, CBDB address dictionaries,
CHGIS county points and unverified external GeoJSON. See
[`../data/derived/README.md`](../data/derived/README.md).
