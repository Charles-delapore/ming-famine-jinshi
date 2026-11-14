# Famines and Imperial Exams in Ming China, 1521–1619

**A 1° grid × 114-year panel analysis of 5,736 famine records and 2,841 Jinshi graduates.**

[Gallery](https://charles-delapore.github.io/ming-famine-jinshi/) ·
[Interactive map](web/interactive_map.html) ·
[中文](README.zh.md) ·
[Technical notes](docs/project_notes.md) ·
[Citation](CITATION.cff)

![Overview](figures/fig3_framework.png)

## Overview

Did famine history shape success in the Ming imperial examinations, and did the
relationship vary across space and time? The project combines 5,736 famine
records with 2,841 Jinshi (1甲/2甲) records on a 1° grid × 114-year panel
covering 1521–1619.

## Results

- Famine belts and Jinshi core areas overlap only partially.
- Famine→Jinshi Granger survives FDR in **48/135** grids; multiscale models find
  **8** short-horizon grids and **0** at 6–10 and 11–20 years.
- GWR is locally significant in **123/159** grids; famine severity is the
  strongest GeoDetector factor (**q = 0.337**).

## Methods and stack

Python 3.13 · GeoPandas · PySAL · mgwr · statsmodels · scikit-learn ·
Matplotlib. Grid-level Granger with FDR control, multiscale LASSO/BIC,
GWR/SDM and GeoDetector.

## Data and citation

Famine: Hu Peng, *Ming famine database*. Jinshi: CBDB. Basemap: CHGIS v6.
Climate: Mann et al. 2009; Schneider et al. 2015. Raw data are not redistributed.

Please cite this repository and the data sources; see
[CITATION.cff](CITATION.cff).

## License

MIT for code; historical data remain under their original terms.
