# P0-1 acceptance — sample generator reproducibility

- Generated: 2026-11-14 14:29
- Command: `python tools/verify_sample_reproducibility.py`
- Generator: `scripts/make_sample_data.py` (seed `20261113`), run twice in fresh interpreters.
- Comparison: `pandas.testing.assert_frame_equal(..., check_exact=True, check_like=False)` — strict cell values, column order and row order.

**Run-to-run: PASS (14/14 tables identical in value and row order; 1/14 byte-identical).**
**Generated vs committed HEAD: PASS (14/14 tables).**

## 1. Two consecutive runs

| Table | Rows | Cols | Values identical | Row order identical | Bytes identical | Verdict |
|---|---:|---:|---|---|---|---|
| `clustered_levels.xlsx` | 400 | 11 | PASS | PASS | no | PASS |
| `clustered_jinshi.xlsx` | 120 | 12 | PASS | PASS | no | PASS |
| `gwr_coefficients.xlsx` | 60 | 8 | PASS | PASS | no | PASS |
| `grid_granger_causality.xlsx` | 60 | 16 | PASS | PASS | no | PASS |
| `grid_data_enriched.csv` | 1200 | 23 | PASS | PASS | yes | PASS |
| `multiscale_causal_short_term.xlsx` | 60 | 20 | PASS | PASS | no | PASS |
| `multiscale_causal_medium_term.xlsx` | 60 | 20 | PASS | PASS | no | PASS |
| `multiscale_causal_long_term.xlsx` | 60 | 20 | PASS | PASS | no | PASS |
| `geodetector_results.xlsx` | 1 | 4 | PASS | PASS | no | PASS |
| `lagged_similarity_results.xlsx` | 80 | 9 | PASS | PASS | no | PASS |
| `stl_decomposition_results.xlsx` | 60 | 12 | PASS | PASS | no | PASS |
| `paleoclimate_partial_correlation.xlsx` | 60 | 7 | PASS | PASS | no | PASS |
| `ccm_summary.xlsx` | 30 | 14 | PASS | PASS | no | PASS |
| `cluster_characteristics_enhanced.xlsx` | 12 | 13 | PASS | PASS | no | PASS |

## 2. Generated output vs committed sample data (HEAD)

| Table | Values + row order match HEAD |
|---|---|
| `clustered_levels.xlsx` | PASS |
| `clustered_jinshi.xlsx` | PASS |
| `gwr_coefficients.xlsx` | PASS |
| `grid_granger_causality.xlsx` | PASS |
| `grid_data_enriched.csv` | PASS |
| `multiscale_causal_short_term.xlsx` | PASS |
| `multiscale_causal_medium_term.xlsx` | PASS |
| `multiscale_causal_long_term.xlsx` | PASS |
| `geodetector_results.xlsx` | PASS |
| `lagged_similarity_results.xlsx` | PASS |
| `stl_decomposition_results.xlsx` | PASS |
| `paleoclimate_partial_correlation.xlsx` | PASS |
| `ccm_summary.xlsx` | PASS |
| `cluster_characteristics_enhanced.xlsx` | PASS |

Generator stdout, run 1 / run 2:

```text
run 1: basemap exists: ming-portfolio\data\sample\basemap_china.geojson
sample data written to ming-portfolio\data\sample
run 2: basemap exists: ming-portfolio\data\sample\basemap_china.geojson
sample data written to ming-portfolio\data\sample
```

## When this result would fail

- The RNG seed in `make_sample_data.py` changes, or numpy/pandas change their random or sort implementations.
- The stable full-key mergesort in the event tables is replaced by a single-key/unstable sort: tied rows can then reorder across runs.
- dtype inference on read (Excel/CSV) differs between environments.
- The generator is edited to write extra tables without updating the 14-table checklist above.
- Section 2 fails after a legitimate data/schema change is committed; re-generate and review the diff before publishing.

## Scope note

These are synthetic sample tables (no real historical record). The byte-digest column is informational only: Excel container metadata (zip member timestamps) varies between writes even when all cell values and row orders are identical. Section 2 is the check that justifies restoring `data/sample/` to HEAD after the two runs.
