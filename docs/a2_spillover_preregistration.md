# A2 pre-registration — spatial spillover (2026-11-14)

**Written BEFORE running `scripts/a2_spillover_analysis.py`.** Frozen design;
changes require a new dated amendment (roadmap §5).

## 1. Question

Does famine in **neighbouring** grids predict local Jinshi output beyond local
famine (migration, relief, market integration)? This is the A6 research
question in roadmap §1.1, executed as work package A2.

## 2. Unit of analysis

1° grid × exam year, 1521–1619, restricted to grids with at least one Jinshi
record in the CBDB export. Counts include **all parsed ranks** (1甲/2甲/3甲);
this is a count model, not the elite-only series.

## 3. Exposures (both frozen at the 1–5 year window)

- `direct` = mean `zaihuang_severity` at `t−1 … t−5` in the same grid.
- `spillover` = mean of `direct` over **queen neighbours** (the 8 cells with
  |Δgrid_x| = 1° and |Δgrid_y| = 1°). Cells with no in-panel neighbour get
  `spillover = 0` and are flagged in a `has_neighbour` indicator that is
  reported but **not** added to the model.

Source: `output/v03/panel_v03.csv.gz` (famine series identical v0.2/v0.3).

## 4. Model (fixed)

Negative-binomial GLM with log link:

```
jinshi_count ~ direct + spillover + C(exam_year) + C(grid)
```

SE clustered by grid. `alpha` is estimated from a simple intercept-only NB fit;
if that fails, `alpha = 1.0` is used and the choice is reported. Both
`direct` and `spillover` coefficients and 95% CIs are the deliverable.

## 5. Interpretation rule (fixed, before results)

| Result | Interpretation |
|---|---|
| spillover CI excludes 0 and \|spillover\| > \|direct\| | **regional famine**; A3's "local famine" wording must be rewritten |
| direct CI excludes 0, spillover includes 0 | local interpretation kept |
| both include 0 | **null**, recorded and stop (no respecification) |

## 6. Failure / identification criteria (fixed)

- If < 60% of units have at least one queen neighbour in the panel, declare the
  spillover **not identifiable** and report the coverage instead of a coefficient.
- Model non-convergence → report it; do not silently switch estimator.
- Null → no window, adjacency, control or FE changes after seeing results.

## 7. What will not be done

- No spatial lag of the dependent variable (SAR/SEM).
- No alternative adjacency (rook, distance bands) after seeing results.
- No 6–20 year windows.
- No post-hoc subgroup splitting.

## 8. Outputs

`data/derived/a2_spillover_coefficients.csv`,
`data/derived/a2_spillover_units.csv`, `docs/a2_spillover_results.md`.
