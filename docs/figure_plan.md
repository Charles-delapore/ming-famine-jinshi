# Figure plan and contracts

This project follows a one-claim-per-figure contract: each figure has a written
core claim, a hero panel, and the statistics that must appear on the page. The
style and encoding rules are those of the
[scientific-visualization](https://github.com/K-Dense-AI/scientific-agent-skills)
and [Icarus Figures](https://github.com/TAO-QKV/Icarus-Figures) skills.

## Figure 1 — Pattern

**File**: `figures/fig1_patterns.{pdf,png,svg}`  
**Script**: `scripts/fig1_patterns.py`

**Core claim**: *Famine events form broad river-basin belts while Jinshi are
concentrated in the southeast; the famine–Jinshi association is spatially
heterogeneous rather than uniform.*

**Hero panels**: A (famine severity map) and B (Jinshi map).

| Panel | Content | Encoding | Data |
|-------|---------|----------|------|
| A | Famine events 1522–1619 | position; colour = severity 1–5 (`YlOrRd`); fixed size | famine event table |
| B | Jinshi 1521–1619 (normalized 1甲/2甲 elite) | position; single blue; fixed size | Jinshi table |
| C | Temporal context | top: annual severity + 5-year moving average; bottom: Jinshi at exam years only | derived from A/B |
| D | GWR coefficient surface | signed coefficient (`RdBu_r`, centred at 0); significant cells opaque | GWR grid results |

**On figure**: n = 5,736 famine events; n = 2,841 Jinshi; 123/159 GWR grids
significant at p < 0.05; moving average labelled descriptive.

## Figure 2 — Mechanism

**File**: `figures/fig2_mechanism.{pdf,png,svg}`  
**Script**: `scripts/fig2_mechanism.py`

**Core claim**: *After FDR correction, the famine→Jinshi Granger signal survives
in 2/135 grids under a fixed 1–5 year joint test (13/135 with a 5-year search
window); famine severity is
the strongest single explanatory factor.*

**Hero panel**: B (FDR-significant Granger grid map).

| Panel | Content | Encoding |
|-------|---------|----------|
| A | GWR local R² | diverging map, `TwoSlopeNorm(0)`; median annotated |
| B | Famine→Jinshi Granger FDR | orange = q < 0.05; grey = not significant |
| C | Discovery across horizons | bars: Granger any lag, short, medium, long |
| D | GeoDetector q | bars sorted by q |

**On figure**: 2/135 fixed-window FDR grids (48/135 is only the 20-lag search
diagnostic); 8 multiscale short-horizon FDR grids vs 0
medium/long; q = 0.337 severity, 0.186 longitude, 0.128 latitude; n = 159 GWR
grids.

## Figure 3 — Graphical abstract

**File**: `figures/fig3_framework.{pdf,png,svg}`  
**Script**: `scripts/fig3_framework.py`

**Core claim**: *Sparse historical records become spatially explicit causal
evidence through the fuse → aggregate → infer pipeline.*

The panels use real method objects: event points, a 1° grid, and a GWR
coefficient surface — not generic boxes-and-arrows.

## Figure 4 — Statistical companion

**File**: `figures/fig4_distribution.{pdf,png,svg}`  
**Script**: `scripts/fig4_distribution.py`

**Core claim**: *The maps are not the whole story: GWR effects are mostly
positive with a right tail, famine severity is concentrated in levels 2–4, and
the 911-record Jinshi subset is dominated by 1523/1526 because of the old
Arabic-only rank filter.*

| Panel | Content | Encoding |
|-------|---------|----------|
| A | GWR coefficient distribution | histogram; zero line; median |
| B | Famine severity composition | ordered bars, severity colours |
| C | Jinshi records by exam year | bars; 1523/1526 highlighted |

This is the S6 statistical companion; maps carry spatial pattern, this figure
carries numeric comparison.

## Figure 5 — Rank-encoding correction (audit figure)

> **Status (A4, 2026-11-14): supplementary material.** Figure 5 is an encoding
> audit, not a main result; it is not linked from the landing page. The fixed-window
> `fig2_fixed_window.{png,pdf,svg}` is the main mechanism figure.

**File**: `figures/fig5_correction.{pdf,png,svg}`  
**Script**: `scripts/fig5_correction.py`

**Core claim**: *Normalizing the Jinshi rank field changes discovery counts and
lag claims, but leaves the spatial GWR association nearly unchanged — the
famine→Jinshi spatial result is robust while the long-lag claim is not.*

This is an **audit figure**, not a new causal claim. It is a v0.2 → v0.3
comparison, and the only figure where v0.2 baseline numbers are intentionally
quoted.

| Panel | Content | Encoding | Data |
|---|---|---|---|
| A | Exam-year composition, old 911 layer vs corrected 2,841 elite | two lines (grey = v0.2, blue = v0.3); 1523/1526 spike annotated | `output/v03/fig_input/clustered_jinshi.xlsx`; legacy `clustered_jinshi.xlsx` |
| B | Grid-level discovery (Granger FDR, GWR significance) | paired bars, denominators in x labels | `output/v03/granger_v02.xlsx`, `granger_v03.xlsx`, `gwr_v02.xlsx`, `gwr_v03.xlsx` |
| C | GWR coefficient agreement on common grids | scatter, r annotated | the two GWR tables |
| D | Lag distribution of FDR-significant Granger grids | v0.2 vs v0.3 | the two Granger tables |

**On figure (v0.2 → v0.3)**: Granger FDR-significant grids 56 → 48 (of 135);
GWR significant 125/158 → 123/159; coefficient r = 0.991 (122/125 overlap);
selected lag 11.0 → 6.5 years (bimodal distribution; reported as a share, not
a headline). The v0.2 values here are **baseline comparison values**, not
current headline figures. Current headline values are 2/135 (fixed 1–5 yr
joint), 13/135 (5-yr window), 123/159, 8/0/0 and q = 0.337/0.186/0.128;
`48/135` is only the 20-lag search diagnostic (Figures 1–2 and
`docs/corrected_robustness.md`). Export and QA: `figures/figure_manifest.csv`
row `fig5`; `docs/figure_qa.md` covers fig5.

## Interactive map

`web/interactive_map.html` is a Folium map of the aggregated 1° cells: mean
famine severity, Jinshi totals, GWR coefficients, and FDR-significant Granger
cells. It includes a layer control, scale control, legend and north arrow. No
individual records are embedded.

**Status**: a local standalone example, not a published online service. It is
outside the five-figure contract and its QA checklist; the `Live gallery` /
`在线图册` links in the READMEs point to the project site, not to a released
map product.

## Style contract

| Item | Rule |
|------|------|
| Width | 7.2 in (double-column / web) |
| Heights | 8.4 in (fig 1), 6.4 in (fig 2), 3.15 in (fig 3) |
| Fonts | Arial + Microsoft YaHei fallback; panel letters 10 pt bold; body 7–8 pt |
| Palette | Okabe–Ito categories; `YlOrRd` severity; `RdBu_r` signed coefficients |
| Maps | Web Mercator; no axis ticks; light grey boundaries |
| Uncertainty | FDR threshold stated; moving average labelled descriptive |
| Missing data | Jinshi zeros are not drawn as a continuous annual series |
| Exports | PDF (Type 42), SVG (editable text), PNG 600 dpi |
| Provenance | source table, projection, transform, N in every footnote |

## Captions (conclusion-first)

**Fig. 1.** Famine belts and Jinshi core areas overlap only partially, and the
famine–Jinshi association changes sign across space. (A) 5,736 famine events by
severity; (B) 2,841 Jinshi records; (C) annual famine severity with a 5-year moving average
and Jinshi counts at exam years; (D) GWR coefficients (123/159 grids significant
at p < 0.05). Basemap: CHGIS v6; projection: Web Mercator.

**Fig. 2.** The famine→Jinshi signal is spatially selective and short-horizon.
(A) GWR local R²; (B) 2/135 grids with fixed 1–5 yr FDR-significant
famine→Jinshi Granger
causality; (C) FDR-significant grid counts by horizon (8 short, 0 medium, 0
long); (D) GeoDetector q values. Granger is predictive, not mechanistic,
causality.

**Fig. 3.** The analysis pipeline turns sparse historical records into
spatially explicit evidence: fuse event, exam and climate data; aggregate to a
1° × 114-year panel; estimate Granger, GWR and GeoDetector evidence.

**Fig. 4.** The maps hide three distributions: GWR effects are mostly positive
but right-skewed; famine severity is concentrated in levels 2–4; and the
normalized 1甲/2甲 Jinshi series declines gently by exam year. The old 911-record
1523/1526 spike is an Arabic-only rank artefact; the comparison is Fig. 5A.
See `docs/jinshi_provenance.md`.

**Fig. 5.** Rebuilding the Jinshi layer with normalized ranks (2,841 elite)
moves FDR discovery from 56 to 48 of 135 grids under the 20-lag search
(2/135 in a fixed 1–5 yr test), while GWR coefficients remain
nearly identical (r = 0.991; 122/125 significant grids overlap). The median
selected lag shifts from 11 to 6.5 years in a bimodal distribution, so lag
claims are the least robust
part of the result. See `docs/corrected_robustness.md`.

## Acceptance checklist

- [x] One claim per figure; caption states the conclusion.
- [x] Raw values and transformations preserved in scripts.
- [x] Colour is redundant with position/marker/panel; palette is colour-blind safe.
- [x] N, units, FDR threshold and data sources are on the figure.
- [x] No decorative 3D, no dual axes, no rainbow for ordered clusters.
- [x] PDF/SVG/PNG exported; fonts embedded in PDF.
- [x] Final-size preview at 7.2 in width.
- [x] S4 scale bar / north arrow added to Fig. 1–2; S6 statistical companion Fig. 4 added.
- [x] 8-standard QA checklist in `docs/figure_qa.md`; colour-blind outputs generated locally (not committed).
- [ ] Re-check venue-specific pt/width before submission.

## Sample data

`data/sample/` contains synthetic tables with the same columns as the result
tables. `scripts/run_sample_figures.py` regenerates the figures into
`figures/sample/` with a clear “synthetic sample” footnote. This is a code and
layout verification path, not a substitute for the real data.

**Synthetic q values**: the GeoDetector q values in
`data/sample/geodetector_results.xlsx` (0.35 / 0.19 / 0.13) are smoke-test
values, **not** the published q = 0.337 / 0.186 / 0.128. The same applies to the
synthetic p-values and significance flags in the other sample tables. Never
quote a number from `data/sample/` as a research result; see
`data/sample/README.md` and `docs/v03_model_outputs.md`.



