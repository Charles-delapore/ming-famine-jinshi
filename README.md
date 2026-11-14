# Famines and Imperial Exams in Ming China, 1521–1619

**Spatial inequality in Ming elite production, and the short-window predictive signal of famine.**

[Gallery](https://charles-delapore.github.io/ming-famine-jinshi/) · [Interactive map](web/interactive_map.html) · [中文](README.zh.md) · [Technical notes](docs/project_notes.md) · [Citation](CITATION.cff)

![Overview](figures/fig3_framework.png)

## Question

Did famine history shape success in the Ming imperial examinations, and did the
relationship vary across space? 5,736 famine records and 2,841 Jinshi (1甲/2甲)
on a 1° grid × 114-year panel, 1521–1619.

## Results

- Famine belts and the Jiangnan Jinshi core overlap only partially.
- Famine severity is the strongest factor: GeoDetector q = 0.337 (longitude
  0.186, latitude 0.128); GWR significant in 123/159 grids, R² = 0.759.
- Short-window signal: fixed 1–5 yr joint test **2/135**; pre-specified 5-year
  window **13/135**; multiscale LASSO **8/135** at 1–5 yr, **0** at 5–10 /
  11–20 years.
- `48/135` is a 20-lag search artefact (7/135 after within-grid correction);
  lag estimates are bimodal, so no single median is reported. Common-support ±1/±3-year
  alignment and record-intensity checks pass. A1 rank-share and A2 spillover
  tests are null.

## Reproduce

`python scripts/a3_assemble_main_results.py` rebuilds every number
(script → table → document). Raw historical tables are not redistributed;
`data/sample/` verifies code and layout only. See `docs/a3_main_results.md`.

## Data and license

Famine: Hu Peng, *Ming famine database*. Jinshi: CBDB. Basemap: CHGIS v6.
Python 3.13 · GeoPandas · PySAL · mgwr · statsmodels · Matplotlib.
MIT for code; historical data remain under their original terms.
