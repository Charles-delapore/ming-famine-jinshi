# v0.3 model outputs (aggregate)

This page records the v0.3 model metrics so the headline numbers are not only
prose. Only aggregate metrics are published; the grid-level inputs and outputs
stay private.

| Metric | v0.2 | v0.3 | Note |
|---|---:|---:|---|
| Jinshi records in panel | 4,806 | 5,401 | `ming_general` + elite extension |
| Granger grids tested | 135 | 135 | enough non-zero years |
| Granger z→j causal (p<0.05) | 71 | 67 | before FDR |
| **Granger FDR-significant** | **56** | **48** | BH q<0.05 |
| Median significant lag | 11.0 yr | 6.5 yr | FDR-significant grids |
| GWR cells | 158 | 159 | both variables > 0 |
| **GWR significant** | **125** | **123** | \|t\|>1.96 |
| GWR median coefficient | 0.456 | 0.442 | local coefficient |
| GWR global R² | 0.757 | 0.759 | |
| Multiscale short (1–5 yr) | — | **8** | FDR-significant |
| Multiscale medium (6–10 yr) | — | **0** | |
| Multiscale long (11–20 yr) | — | **0** | |
| GeoDetector q, severity | — | **0.3368** | |
| GeoDetector q, longitude | — | **0.1857** | |
| GeoDetector q, latitude | — | **0.1284** | |
| GWR coefficient r, v0.2 vs v0.3 | — | **0.9914** | 158 common grids |
| Significant-grid overlap | — | **122/125** | v0.2-only 3; v0.3-only 0 |

Machine-readable copy:
[`data/derived/v03_model_summary.csv`](../data/derived/v03_model_summary.csv).

## How these were produced

```bash
set MING_JINSHI_RAW=<path to the private CBDB export>
set MING_FAMINE_MERGED=<path to the private famine table>
set MING_FAMINE_EXT=<path to the private famine export>
set MING_CITYS=<path to the private city points>
set MING_JINSHI_ALL=<path to the private Jinshi extension>

python scripts\corrected_robustness.py
python scripts\build_v03_figure_inputs.py
```

`corrected_robustness.py` writes `output/v03/summary.json` and the v0.2/v0.3
Granger/GWR tables. `build_v03_figure_inputs.py` writes the multiscale and
GeoDetector tables consumed by Figure 2.

## Reading notes

- The v0.2 reconstruction reproduces the published grid results exactly
  (56/135 FDR, 125/158 GWR), which validates the re-run.
- Spatial effects are robust (r = 0.991; 122/125 significant grids overlap).
- Discovery count and lag are not fully robust (56→48; 11→6.5 years).
- The README rounds q to 0.337/0.186/0.128; the unrounded values are above.
- The sample `geodetector_results.xlsx` (0.35/0.19/0.13; 6/0/0) is synthetic
  and is not evidence for the v0.3 numbers.
