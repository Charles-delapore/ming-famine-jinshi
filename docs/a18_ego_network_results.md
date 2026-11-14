# A18 — descriptive ego-network results (2026-11-14)

- Generated: 2026-11-14 18:09
- Command: `python scripts/a18_ego_network_analysis.py`
- Pre-registration: `docs/a18_ego_network_preregistration.md` (frozen before run). **Descriptive only** — no model, no p-values, no causal claim.
- Trigger: `docs/a17_cbdb_network_coverage.md` (GO, coverage 56.4%).
- Graph: CBDB `KIN_DATA` (565,276 rows) + `ASSOC_DATA` (190,164 rows), restricted to Jinshi egos; coordinates via `BIOG_ADDR_DATA` → `ADDR_CODES` (finest administrative tier).

| Metric | Value |
|---|---:|
| `jinshi_personids` | 27711 |
| `egos_with_kin_or_assoc_edge` | 15616 |
| `ego_coverage` | 0.5635 |
| `median_total_degree` | 9.0 |
| `q25_total_degree` | 7.0 |
| `q75_total_degree` | 12.0 |
| `max_total_degree` | 334 |
| `share_degree_ge_5` | 0.8989 |
| `share_degree_ge_10` | 0.4337 |
| `median_kin_degree` | 8.0 |
| `median_assoc_degree` | 0.0 |
| `kin_edges_total` | 133868 |
| `assoc_edges_total` | 39989 |
| `kinship_type_126_弟` | 31161 |
| `kinship_type_125_兄` | 19849 |
| `kinship_type_75_父` | 14406 |
| `kinship_type_62_祖父` | 14117 |
| `kinship_type_48_曾祖` | 14017 |
| `kinship_type_135_妻子` | 13627 |
| `kinship_type_111_母` | 13085 |
| `kinship_type_375_繼母` | 3832 |
| `kinship_type_180_子` | 3133 |
| `kinship_type_163_第二任妻` | 2453 |
| `kin_edges_with_both_coordinates` | 68961 |
| `kin_address_coverage` | 0.5152 |
| `median_kin_distance_deg` | 0.0 |
| `share_kin_same_1deg_grid` | 0.9541 |

## Grid-level descriptive correlations

| Target | n grids | Pearson r | Spearman r |
|---|---:|---:|---:|
| `v03_jinshi` | 273 | 0.906 | 0.950 |
| `famine_level` | 273 | 0.690 | 0.605 |

## Interpretation (strictly descriptive)

- 15,616 of 27,711 Jinshi PersonIDs have ≥1 recorded kin/association edge (56.4%).
- Median total degree 9; the distribution is reported with quartiles and ≥5 / ≥10 shares.
- Kin address coordinate coverage: **51.5%** (geographic measures estimable).
- Grid correlations are **ecological and descriptive**; degree is as much a documentation-intensity proxy as a social one. No significance claim is made and no model was fitted.
- ⚠️ The high grid correlation with `v03_jinshi` (r≈0.91) is **mechanically expected**: both are computed from the same Jinshi persons in a grid (more egos ⇒ more recorded kin AND more Jinshi). It is **not** evidence that social networks explain elite production. Likewise the ~95% same-grid kin share largely reflects CBDB recording family / ancestral addresses at one location, not a measured social-distance effect.

## Limits (frozen)

- CBDB kinship includes auto-generated / inferred relations; edge quality is not independently verified.
- `KINSHIP_CODES` labels are CBDB's own taxonomy; no re-coding.
- Ego coordinates use the finest-tier address; kin coordinates use the same rule — historical point locations, not exact residences.
- The three-stage funnel (举人完整度) remains out of scope.

## When this would fail

- CBDB replaced without re-running A17 + A18.
- Any measure/threshold changed after seeing results (forbidden).
- These numbers quoted as evidence about elite reproduction rather than as a descriptive inventory.

## Outputs

| Output | Path |
|---|---|
| summary + kinship types | `data/derived/a18_ego_network_summary.csv` |
| per-ego degrees | `<local private; not distributed>` |
| grid correlations | `data/derived/a18_grid_correlations.csv` |

Private inputs; aggregate outputs only.
