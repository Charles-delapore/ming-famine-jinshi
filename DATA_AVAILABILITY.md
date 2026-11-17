# Data availability

## Published with the repository

- `data/derived/` — aggregate counts, coefficients and grid-level summaries.
  The full list, grain and columns are in
  [`docs/data_dictionary.md`](docs/data_dictionary.md).
- `data/sample/` — synthetic tables with the production schema (seed
  `20261113`); no historical record is included.
- `figures/` — static figures and the standalone interactive map.
- `src/`, `scripts/`, `tools/` — analysis, figure and check code.

## Not distributed

| Material | Reason |
|---|---|
| CBDB Jinshi export (`明进士.xlsx`) | third-party database; redistribution restricted |
| Famine event tables (`merged_data.csv`, `table_generals*.xlsx`) | private research tables |
| Person-level address links and network edges | individual-level identifiers |
| Ego-network degree table | individual-level identifiers |
| CBDB address dictionary and CHGIS county points | third-party bulk content |
| External famine event chronology and derived panel | licence not confirmed |
| Third-party Ming city/area GeoJSON | licence not confirmed |

The publication boundary is enforced by `tools/check_public_tree.py` and the
CI workflow.

## Reproducing with private inputs

Set the `MING_*` environment variables documented in
[`data/README.md`](data/README.md), place the private tables outside the
repository, and run the script named in the relevant `docs/a*.md` note. Every
published table is written by a script in `scripts/`; the script-to-table map
is in [`docs/a3_main_results.md`](docs/a3_main_results.md).

The synthetic sample exercises the code and figure layout without the private
tables:

```bash
python scripts/make_sample_data.py
python scripts/run_sample_figures.py
```

## Third-party sources

| Source | Use | Terms |
|---|---|---|
| CBDB (Harvard/PKU/Academia Sinica) | Jinshi records | academic use; no redistribution of individual records |
| CHGIS v6 | historical basemap | research/education; basemap not redistributed |
| Hu Peng, Ming famine database | famine events | private research table |
| ChinaHighPM2.5 (Wei et al.) | pollution layer (documentation) | CC BY 4.0 |
| MODIS MOD13Q1 | NDVI (documentation) | NASA open data |
| GHSL / WorldPop | population (documentation) | CC BY 4.0 |

## Corrections

If a published aggregate is wrong, open an issue with the cell, value, source
and expected value. Corrections are recorded in `CHANGELOG.md`.
