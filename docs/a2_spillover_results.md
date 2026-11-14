# A2 — spatial spillover results (2026-11-14)

- Generated: 2026-11-14 16:57
- Command: `python scripts/a2_spillover_analysis.py`
- Pre-registration: `docs/a2_spillover_preregistration.md` (frozen before run).
- Model: negative-binomial GLM (log link), `jinshi_count ~ direct + spillover + C(exam_year) + C(grid)`, SE clustered by grid.
- NB alpha: 3.6307 (estimated (intercept-only NB)).
- Units: 11051; grids: 257; exam years: 43.
- Queen-neighbour coverage: **99.2%** (pre-registered minimum 60%).

## Verdict: NULL (both CIs include 0; stop, no respecification)

| term | coef | cluster SE | 95% CI | p | significant |
|---|---:|---:|---|---:|---|
| direct | +0.00613 | 0.01318 | [-0.01970, +0.03195] | 0.6420 | no |
| spillover | +0.01938 | 0.02988 | [-0.03919, +0.07794] | 0.5167 | no |

Pre-registered interpretation rule (§5) applied mechanically; no window, adjacency, control or fixed-effect changes were made after seeing the coefficients.

## When this result would fail

- If a different adjacency (rook / distance band) or lag window is used, the coefficients are not comparable; both are frozen.
- If the NB alpha is re-estimated on the full model, standard errors move.
- Counts include only CBDB records with a parsed rank; rank-missing records are not modelled (selection into parsing is a limitation).
- Zero-inflated counts are handled by NB, not by a hurdle model; over-dispersion is absorbed by alpha.

## Outputs

| Output | Path |
|---|---|
| coefficient table | `data/derived/a2_spillover_coefficients.csv` |
| unit-level data | `data/derived/a2_spillover_units.csv` |

Private inputs; aggregate outputs only.
