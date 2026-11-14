# A4 — figure QA (2026-11-14)

- Generated: 2026-11-14 17:09
- Command: `python scripts/a4_figure_qa.py`
- Colour-blind simulations: `python tools/colorblind_check.py <png>` (Machado et al. 2009), outputs written to a local `figures/qa/` directory (not committed).
- Committed QA outputs: none (generated locally).

## Changes in this work package

- Figure 1 panel B title corrected `1523–1619` → `1521–1619`; figure re-rendered from the real tables (`MING_OUTPUT=output/v03/fig_input`).
- New main mechanism figure `fig2_fixed_window.{png,pdf,svg}` from `data/derived/a3_main_results.csv`: fixed 1–5 yr = 2/135, 5-yr window = 13/135, multiscale 8/0/0; 48/135 shown only as a grey search diagnostic.
- Original `fig2_mechanism` and `fig5_correction` demoted to **supplementary** in `figures/figure_manifest.csv` (new `status` column); Figure 5 is not linked from the landing page.
- `index.html` now shows only spatial pattern, short-window result, GWR/GeoDetector and the methodological warning.

## Format / dpi check

| Figure | Status | Item | OK | Value |
|---|---|---|---|---|
| `fig1_patterns` | main | png | yes | 2469221 |
| `fig1_patterns` | main | pdf | yes | 1424762 |
| `fig1_patterns` | main | svg | yes | 3936731 |
| `fig1_patterns` | main | png dpi | yes | 600 |
| `fig2_fixed_window` | main | png | yes | 225168 |
| `fig2_fixed_window` | main | pdf | yes | 18012 |
| `fig2_fixed_window` | main | svg | yes | 58203 |
| `fig2_fixed_window` | main | png dpi | yes | 600 |
| `fig3_framework` | main | png | yes | 1358656 |
| `fig3_framework` | main | pdf | yes | 1294876 |
| `fig3_framework` | main | svg | yes | 3671682 |
| `fig3_framework` | main | png dpi | yes | 600 |
| `fig4_distribution` | main | png | yes | 255878 |
| `fig4_distribution` | main | pdf | yes | 56866 |
| `fig4_distribution` | main | svg | yes | 50305 |
| `fig4_distribution` | main | png dpi | yes | 600 |
| `fig2_mechanism` | supplementary | png | yes | 1053930 |
| `fig2_mechanism` | supplementary | pdf | yes | 791109 |
| `fig2_mechanism` | supplementary | svg | yes | 2333220 |
| `fig2_mechanism` | supplementary | png dpi | yes | 600 |
| `fig5_correction` | supplementary | png | yes | 692212 |
| `fig5_correction` | supplementary | pdf | yes | 66104 |
| `fig5_correction` | supplementary | svg | yes | 95988 |
| `fig5_correction` | supplementary | png dpi | yes | 600 |

## Colour-blind outputs

| Figure | Simulation | Present |
|---|---|---|
| `fig1_patterns` | protanopia | yes |
| `fig1_patterns` | deuteranopia | yes |
| `fig2_mechanism` | protanopia | yes |
| `fig2_mechanism` | deuteranopia | yes |
| `fig2_fixed_window` | protanopia | yes |
| `fig2_fixed_window` | deuteranopia | yes |
| `fig4_distribution` | protanopia | yes |
| `fig4_distribution` | deuteranopia | yes |
| `fig5_correction` | protanopia | yes |
| `fig5_correction` | deuteranopia | yes |

## Acceptance

- PASS: every main/supplementary figure has PNG, PDF and SVG; 600 dpi PNG verified where embedded.
- PASS: protanopia + deuteranopia outputs present for all checked figures.
- Public pages no longer carry an uncorrected `48/135` headline or a `6.5`-year median lag (`python scripts/a0_apply_claims.py --check`).

## When this would fail

- A figure is re-rendered without re-running this QA script.
- The claims audit check fails after a text edit (A8 re-checks it).
- A new main figure is added without colour-blind simulations.

Private inputs; aggregate outputs only.
