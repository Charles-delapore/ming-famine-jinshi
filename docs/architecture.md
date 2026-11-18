# Architecture

## Data flow

```
private inputs (never committed)
  CBDB export · famine tables · CHGIS basemap
        │
        ▼
scripts/  ──►  output/            (intermediate panels, model fits)
        │           │
        │           ├──► figures/           (PDF/SVG/PNG)
        │           └──► data/derived/      (aggregate tables, published)
        │
        └──► docs/     (method notes, audits, results)
```

## Layers

| Path | Role | Public? |
|---|---|---|
| `src/` | analysis modules: panel construction, Granger, GWR, GeoDetector, clustering | yes |
| `scripts/` | one script per analysis or figure; run from the repository root | yes |
| `tools/` | checks and utilities (`check_public_tree.py`, sample verifier) | yes |
| `data/sample/` | synthetic tables with the production schema | yes |
| `data/derived/` | aggregate counts, coefficients and grid summaries | yes |
| `figures/` | static figures and the standalone map | yes |
| `docs/` | provenance, audits, method notes, release checklist | yes |
| `output/` | intermediate panels and model fits | no (gitignored) |
| private raw tables | CBDB, famine, CHGIS, external event data | no |

## Boundary rules

1. Raw or person-level tables stay outside the repository.
2. `data/derived/` contains aggregates only; the data dictionary lists the grain.
3. `tools/check_public_tree.py` enforces the boundary; CI runs it on every push.
4. The synthetic sample lets the code run without the private tables.

## Entry points

| Command | Purpose |
|---|---|
| `python run_pipeline.py` | 14-step analysis pipeline (needs private inputs) |
| `python scripts/make_sample_data.py` | regenerate the synthetic sample |
| `python scripts/run_sample_figures.py` | figures 1–4 from the sample |
| `python scripts/make_interactive_map.py` | standalone map (real or `--sample`) |
| `python -m pytest -q` | unit and contract tests |
| `python tools/check_public_tree.py` | publication boundary check |

## Design decisions

- One script per result; the script-to-table-to-document map is in
  `docs/a3_main_results.md`.
- Every published number must be reproducible from a script and a table.
- Lag-search results are reported as diagnostics, not as the headline.
