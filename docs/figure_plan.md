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
| B | Jinshi 1523–1619 | position; single blue; fixed size | Jinshi table |
| C | Temporal context | top: annual severity + 5-year moving average; bottom: Jinshi at exam years only | derived from A/B |
| D | GWR coefficient surface | signed coefficient (`RdBu_r`, centred at 0); significant cells opaque | GWR grid results |

**On figure**: n = 5,736 famine events; n = 911 Jinshi; 125/158 GWR grids
significant at p < 0.05; moving average labelled descriptive.

## Figure 2 — Mechanism

**File**: `figures/fig2_mechanism.{pdf,png,svg}`  
**Script**: `scripts/fig2_mechanism.py`

**Core claim**: *After FDR correction, the famine→Jinshi Granger signal survives
in 56/135 grid cells and is concentrated in short horizons; famine severity is
the strongest single explanatory factor.*

**Hero panel**: B (FDR-significant Granger grid map).

| Panel | Content | Encoding |
|-------|---------|----------|
| A | GWR local R² | diverging map, `TwoSlopeNorm(0)`; median annotated |
| B | Famine→Jinshi Granger FDR | orange = q < 0.05; grey = not significant |
| C | Discovery across horizons | bars: Granger any lag, short, medium, long |
| D | GeoDetector q | bars sorted by q |

**On figure**: 56/135 FDR-significant grids; 9 short-horizon FDR grids vs 0
medium/long; q = 0.349 severity, 0.189 longitude, 0.126 latitude; n = 158 GWR
grids.

## Figure 3 — Graphical abstract

**File**: `figures/fig3_framework.{pdf,png,svg}`  
**Script**: `scripts/fig3_framework.py`

**Core claim**: *Sparse historical records become spatially explicit causal
evidence through a transparent fuse → aggregate → infer pipeline.*

The panels use real method objects: event points, a 1° grid, and a GWR
coefficient surface — not generic boxes-and-arrows.

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
severity; (B) 911 Jinshi; (C) annual famine severity with a 5-year moving average
and Jinshi counts at exam years; (D) GWR coefficients (125/158 grids significant
at p < 0.05). Basemap: CHGIS v6; projection: Web Mercator.

**Fig. 2.** The famine→Jinshi signal is spatially selective and short-horizon.
(A) GWR local R²; (B) 56/135 grids with FDR-significant famine→Jinshi Granger
causality; (C) FDR-significant grid counts by horizon (9 short, 0 medium, 0
long); (D) GeoDetector q values. Granger is predictive, not mechanistic,
causality.

**Fig. 3.** A transparent pipeline turns sparse historical records into
spatially explicit evidence: fuse event, exam and climate data; aggregate to a
1° × 114-year panel; estimate Granger, GWR and GeoDetector evidence.

## Acceptance checklist

- [x] One claim per figure; caption states the conclusion.
- [x] Raw values and transformations preserved in scripts.
- [x] Colour is redundant with position/marker/panel; palette is colour-blind safe.
- [x] N, units, FDR threshold and data sources are on the figure.
- [x] No decorative 3D, no dual axes, no rainbow for ordered clusters.
- [x] PDF/SVG/PNG exported; fonts embedded in PDF.
- [x] Final-size preview at 7.2 in width.
- [ ] Verify the target venue’s current figure requirements before submission.

## Sample data

`data/sample/` contains synthetic tables with the same columns as the result
tables. `scripts/run_sample_figures.py` regenerates the figures into
`figures/sample/` with a clear “synthetic sample” footnote. This is a code and
layout verification path, not a substitute for the real data.
