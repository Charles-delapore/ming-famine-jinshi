# Analysis layer

This directory is the sanitized analysis layer of the Work_ming project. It is
the code behind the figures and the grid-level results, separated from the
private raw tables.

```
src/
├── config.py                 # env-based paths, cluster/grid parameters
├── algorithms/
│   ├── ss_dbscan.py          # weighted semi-supervised DBSCAN
│   ├── st_dbscan.py          # spatial-temporal DBSCAN
│   ├── gmm_cluster.py        # Gaussian mixture clustering
│   ├── dynamic_weight_dbscan.py
│   ├── st_graph.py           # graph construction for spatial clusters
│   ├── cgan_augment.py       # optional CGAN augmentation (TensorFlow or PyTorch)
│   └── run_theory_cluster.py
├── analysis/
│   ├── similarity.py         # cluster similarity + FDR helpers
│   ├── cluster_compare.py    # lagged comparison / permutation tests
│   ├── grid_analysis.py      # 1° grid panel, Granger, multiscale LASSO/BIC
│   ├── paleoclimate_analysis.py
│   ├── ccm_analysis.py       # convergent cross-mapping (documented negative)
│   ├── spatial_regression.py # SDM (spreg) + GWR (mgwr)
│   ├── sensitivity_analysis.py # resolution, STL, GeoDetector
│   └── bayesian_optimize.py  # clustering quality / GP search
├── data_processing/
│   ├── loader.py             # event table loaders
│   ├── grid_integrator.py    # event → grid aggregation
│   └── paleoclimate_loader.py
└── visualization/            # legacy 2D/3D/dual-axis helpers
```

## Paths

`config.py` reads `MING_DATA`, `MING_OUTPUT`, `MING_PALEO`, `MING_OLD_VERSION`
from the environment. There are no machine-specific paths in this directory.

## Notes before reusing

- `CLUSTER_PARAMS` keeps `max_cluster_size=100`. This caps dense clusters and is
  the reason the exploratory 3D figures were retired; see
  `docs/design_notes.md`. Do not present the resulting labels as natural clusters.
- `GRID_PARAMS["y_max"]` is 120.257776 in the original code, which is not a valid
  latitude. It is kept as published for provenance; verify it before re-running
  `grid_integrator` on new data.
- `cgan_augment.py` imports TensorFlow or PyTorch lazily. Install one of them
  only if you need the augmentation branch.
- `run_pipeline.py` at the repository root is the 14-step orchestrator. It needs
  the full raw dataset; the figure scripts run on the synthetic sample data.

## Minimal smoke test

```bash
python scripts/make_sample_data.py
python scripts/run_sample_figures.py
```

The sample tables are synthetic (see `data/sample/README.md`); they exercise the
code paths and figure layout without redistributing historical records.
