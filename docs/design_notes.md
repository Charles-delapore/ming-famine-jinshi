# Design notes

These notes document why the portfolio figures look the way they do. The short
version: every panel has one job, the encoding is honest about what the data can
support, and the figures are reproducible from result tables.

## Retiring the exploratory 3D figures

The original `SSDBSCAN` figures drew 74 famine clusters in a 3D rainbow scatter.
A diagnostic showed that **72 of those clusters contain exactly 100 events**:
`max_cluster_size=100` was cutting the dense core into equal chunks. The colours
therefore encoded an artefact of the algorithm, not a natural grouping. The
portfolio keeps clustering as an exploratory step and moves the inferential
evidence to the grid level.

Other retired figures:

- `comparison_3d.png` — 5,736 triangles + 911 circles in one 3D box; unreadable
  overlap and no faceting.
- `similarity_heatmap.png` — 72 uninterpretable cluster rows, unreadable labels.
- `dual_axis_trend_fitted.png` — x-axis 1300–1700 for 1522–1619 data; a
  high-degree polynomial created a spurious 1520 spike; dual axes implied a
  correlation the plot did not establish.

## Figure contracts

| Figure | Claim | Hero panel |
|--------|-------|------------|
| 1 Pattern | Famine belts and Jinshi cores overlap only partially; the association is spatially heterogeneous. | A/B maps |
| 2 Mechanism | The famine→Jinshi signal is spatially selective and concentrated in short horizons. | B Granger map |
| 3 Abstract | Sparse records become spatially explicit evidence through a transparent pipeline. | Real data in each step |

## Visual system

- **Palette**: Okabe–Ito colour-blind-safe categories; `YlOrRd` for famine
  severity; `RdBu_r` for signed GWR coefficients; blue for Jinshi.
- **Typography**: Arial with Microsoft YaHei fallback; 7–9 pt at 7.2 in width;
  bold panel letters.
- **Maps**: Web Mercator, no axis ticks, provincial boundaries in light grey,
  direct annotations for regions.
- **Time series**: aligned panels instead of dual axes; Jinshi shown at exam
  years only; the 5-year moving average is labelled descriptive.
- **Statistics**: N, FDR thresholds, units and data provenance on the figure.
- **Exports**: PDF (Type 42 fonts), SVG (editable text), PNG 600 dpi.

## Reproducibility

Each figure is a committed script that reads a result table through
`style/ming_style.py`. The style module resolves paths from `MING_ROOT`,
`MING_OUTPUT`, `MING_DATA` and `MING_FIG_DIR`, so the same scripts run on another
machine once the data are in place.

## What is deliberately not shown

- No decorative 3D, no rainbow palette for ordered classes, no dual axes.
- No p-value-only bar charts; counts and q values are labelled with denominators.
- No claim that Granger causality is mechanistic causality.
- No hiding of the CCM failure; it is part of the method story.
