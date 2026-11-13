# Data and reproduction notes

This repository contains **code, figures and documentation**, not the raw
historical datasets. The raw tables are third-party or private research data and
are not redistributed here.

## Expected local layout

```
<MING_ROOT>/
├── output/                      # result tables produced by the analysis pipeline
│   ├── clustered_levels.xlsx
│   ├── clustered_jinshi.xlsx
│   ├── gwr_coefficients.xlsx
│   ├── grid_granger_causality.xlsx
│   ├── grid_data_enriched.csv
│   ├── multiscale_causal_short_term.xlsx
│   ├── multiscale_causal_medium_term.xlsx
│   ├── multiscale_causal_long_term.xlsx
│   └── geodetector_results.xlsx
└── workbase/
    └── 002数据/
        └── 地图书明代灾荒/
            └── province.shp   # basemap used by the figure scripts
```

Set the environment variables before running the scripts:

```bash
export MING_ROOT=/path/to/Work_ming          # Windows: $env:MING_ROOT = "I:\L\Work_ming"
export MING_OUTPUT=$MING_ROOT/output         # optional
export MING_DATA=$MING_ROOT/workbase/002数据 # optional
export MING_FIG_DIR=./figures                # optional; defaults to ./figures
```

Then:

```bash
python scripts/fig1_patterns.py
python scripts/fig2_mechanism.py
python scripts/fig3_framework.py
```

## Sources

| Data | Source | Note |
|------|--------|------|
| Administrative points / basemap | CHGIS v6 (China Historical GIS, Fudan University / Harvard Yenching) | cite CHGIS; do not redistribute without permission |
| Ming famine records | Project-compiled from historical sources | private research table; not included |
| Ming Jinshi database | Project-compiled from historical sources | private research table; not included |
| Paleoclimate reconstructions | Mann et al. (2009); Schneider et al. (2015) | public scientific datasets; link to the original archives |

If you reuse the figures or pipeline, cite the data sources and this repository.
