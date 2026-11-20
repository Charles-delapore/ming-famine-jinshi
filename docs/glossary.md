# Glossary

| Term | Meaning in this repository |
|---|---|
| 进士 (Jinshi) | the highest degree in the Ming imperial examination |
| 1甲 / 2甲 / 3甲 | the three honours classes; this project's elite layer is 1甲/2甲 |
| 911 layer | the earlier Arabic-numeral-coded Jinshi subset; audit only, not the headline |
| 1° grid | cells centred at `floor(coord) + 0.5`; 291 cells appear in the panel |
| panel | grid × year table, 1506–1619 in the v0.3 build |
| famine severity | per cell-year sum of the famine grade (0–5) |
| Granger test | whether past famine improves prediction of later Jinshi **beyond past Jinshi** |
| max-F search | selecting the lag with the largest F statistic over a search window (1–20 years) |
| fixed-window test | a joint F-test with lags 1–5 fixed in advance; no lag selection |
| FDR | Benjamini–Hochberg false-discovery-rate control across grids |
| q-value | BH-adjusted p-value |
| median lag | median selected lag among FDR-significant grids (bimodal, not a headline) |
| short-lag share | share of FDR grids with selected lag ≤ 5 years |
| GWR | geographically weighted regression; local famine→Jinshi coefficient |
| local R² | GWR local fit at a grid cell |
| GeoDetector q | share of the outcome variance explained by a stratified factor |
| A1 | rank-share test: does famine change the 1甲/2甲 share? (null) |
| A2 | spillover test: does neighbouring famine predict local Jinshi? (null) |
| A12 | full-Ming replication with an independent famine source |
| A17 | CBDB network coverage audit (56.4%, above the 30% gate) |
| CC BY 4.0 | attribution-only licence used by GHSL/WorldPop and CHAP |
| ODbL | share-alike licence used by OpenStreetMap |

## Notation

- `k` — famine-series shift in years in the time-perturbation test.
- `q` — GeoDetector q statistic, not a p-value.
- `n` — number of grids, grid-years or records, stated in each table.
