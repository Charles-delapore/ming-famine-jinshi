# Figure QA — journal standards

Based on the 8 standards in the 2026-11-14 geography research bundle
(`08-期刊级科研绘图管线`). This is the checklist applied to `fig1`–`fig5`.

## S1 分面先行，一图一结论

- [x] Figure 1: A–D each has one job; the famine/Jinshi maps and the GWR panel
      share the same extent.
- [x] Figure 2: A–D separate model fit, FDR discovery, horizon counts and factor q.
- [x] Figure 3: fuse → aggregate → infer, one object per step.
- [x] Figure 4: three distributions, one per panel.
- [x] Figure 5: A–D separate exam-year composition, discovery counts, GWR
      coefficient agreement and lag distribution. It is an audit comparison
      (v0.2 vs v0.3), not a new causal claim; see `docs/figure_plan.md`
      § Figure 5.

## S2 配色讲语义

- [x] `YlOrRd` for famine severity (ordered), `RdBu_r` for signed GWR
      coefficients (diverging, zero-centred), blue for Jinshi (single category).
- [x] Figure 5 uses grey = v0.2 / blue = v0.3 consistently across panels A–D.
- [x] Categories ≤ 5–7.
- [x] Colour-blind simulations generated with `tools/colorblind_check.py`
      (Machado et al. 2009) into a local `figures/qa/` directory (not committed).
- [x] Grayscale check: the significance category is also encoded by layer
      selection, not colour alone.

## S3 底图退后

- [x] Province boundaries are light grey; no saturated basemap.
- [x] Interactive map uses OpenStreetMap only as a reference basemap.
- [x] Figure 5 has no basemap (all panels are statistical comparisons).

## S4 四件套齐全

- [x] Legend/colorbar with units and thresholds.
- [x] Scale bar (`figure_kit.scale_bar`, approximate at map-centre latitude).
- [x] North arrow (`figure_kit.north_arrow`).
- [x] Data source, projection and software in the footer.
- [ ] Final visual check at 200% for overlap/clipping (manual).

## S5 字体三级

- [x] Titles 9–10 pt, axis/legend 6.5–8 pt, footer 6 pt at 7.2 in width.
- [x] Arial + Microsoft YaHei fallback; CJK renders correctly.
- [ ] Publisher-specific pt values must be rechecked at the target print width.

## S6 统计图与地图分工

- [x] Maps do not carry numeric labels.
- [x] Figure 4 is the statistical companion: GWR coefficient distribution,
      famine composition, exam-year composition.
- [x] Figure 5 is an audit companion: all four panels carry numeric comparisons
      and no map is used. v0.2 baseline values appear only in this figure and in
      `docs/corrected_robustness.md`, always labelled as baseline.
- [x] Counts and medians are annotated; no map is used for numeric comparison.

## S7 阈值标在图上，图注自足

- [x] GWR zero line and FDR threshold are stated on the figure.
- [x] Each figure has a source/notes footer.
- [x] Captions in `docs/figure_plan.md` state the conclusion first.

## S8 复现信息进图注

- [x] Figure scripts and source tables are listed in `figures/figure_manifest.csv`
      (all five rows, including `fig5`).
- [x] Projection (Web Mercator) and software stack are in the footer.
- [x] `MING_OUTPUT` / `MING_BASEMAP` are documented in `data/README.md`.
- [ ] Zenodo DOI pending author action (see `docs/zenodo_release.md`).

## Colour-blind check

```bash
python tools/colorblind_check.py \
  figures/fig1_patterns.png \
  figures/fig2_mechanism.png \
  figures/fig4_distribution.png \
  figures/fig5_correction.png
```

Outputs `*_protanopia.png` and `*_deuteranopia.png` next to the inputs; move them
to a local `figures/qa/` directory for the QA record. Checked pairs for fig1, fig2, fig4
and fig5 are generated locally (not committed).

## Notes

- Scale bars are approximate because Web Mercator distorts distance away from
  the standard parallel; the footer says so.
- The graphical abstract (Fig. 3) is a schematic and does not carry a scale bar;
  the scale/north furniture applies to the analytical maps (Fig. 1–2).
- Figure 5 is an audit figure: it quotes v0.2 baseline numbers (56 vs 48 FDR
  grids under a 20-lag search, 11.0 vs 6.5 yr selected lag) solely to show what
  the rank fix changes. Current headline: 2/135 (fixed 1–5 yr joint), 13/135
  (5-yr window), 8/0/0, 123/159 and q = 0.337/0.186/0.128. `48/135` is kept
  only as a 20-lag search diagnostic (`docs/long_tail_analysis.md`).
- The interactive map uses aggregated 1° cells only; individual records are not
  embedded.

