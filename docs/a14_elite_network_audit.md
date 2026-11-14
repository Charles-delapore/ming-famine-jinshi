# A14 — elite social-network coverage audit (2026-11-14)

- Generated: 2026-11-14 17:56
- Command: `python scripts/a14_elite_network_audit.py`
- Scope: P1-7 **prerequisite** (CBDB relationship-coverage audit). Exploratory and descriptive only — no ego-network, no funnel model, no causal claim.
- Source: three `ming_general/*社会关系网络查询结果.xlsx` workbooks, previously unused by the project.

| Metric | Value |
|---|---:|
| `edge_rows_raw` | 40450 |
| `edge_rows_deduplicated` | 22459 |
| `unique_person_ids` | 2678 |
| `unique_node_ids` | 6136 |
| `unique_actors_total` | 6902 |
| `jinshi_ids_in_export` | 27711 |
| `jinshi_ids_with_any_network_edge` | 4276 |
| `jinshi_network_coverage` | 0.1543 |
| `edges_with_both_coordinates` | 20767 |
| `median_edge_distance` | 1.0 |
| `share_edges_within_1_degree` | 0.0 |
| `coverage_go_threshold` | 0.3 |

## Go / No-Go: **NO-GO**

Declared before computation: ≥30% of Jinshi PersonIDs must appear in at least one network edge. Observed: **15.4%**.

Coverage is below the declared threshold. Per roadmap §2 P1-7 the correct output is a **method note only**: do not build ego-networks or a funnel on a biased subset of elites. The relationship tables may still support descriptive network statistics (reported below), but not an inferential elite-reproduction model.

## Descriptive network statistics (not inferential)

- Kin / Non distribution: `{'N': 20054, nan: 2405}`
- Top relation types: `{'致书【关系人】': 2771, '总合多种关系': 2405, '答【关系人】书': 1855, '被致书由【关系人】': 1751, '为【关系人】作墓志铭': 1426, '为【关系人】作临别赠言(送别诗、序)': 911, '收到【关系人】的答书': 865, '赠诗、文': 825, '为【关系人】作传': 789, '为【关系人】作祭文': 550, '为【关系人】所著书作序': 520, '祭文由【关系人】所作': 517}`
- Edge-distance median: 1.000 (n = 21,703)

## Limits

- The three workbooks are **query results**, not the full CBDB graph; CBDB `KIN_DATA` (565,276 rows) / `ASSOC_DATA` (190,164 rows) are larger but were not used here.
- Duplicate edges were removed on (PersonID, NodeID, relation type); different relation types between the same pair are kept.
- `Edge Dist.` units are **undocumented** in the source workbooks: the observed median is 1.0 and no value is below 1, so it is not interpreted as a geographic distance. It may be a categorical or binned code; the distance statistics above are reported as-is only.
- Coverage is measured against the `明进士.xlsx` export (28,761 rows), which includes non-Jinshi/wuju rows; this is a conservative denominator.

## When this would fail

- Network workbooks replaced without re-running the audit.
- The coverage threshold changed after seeing the number (declared above).
- Descriptive statistics quoted as evidence about elite reproduction.

## Outputs

| Output | Path |
|---|---|
| coverage table | `data/derived/a14_network_coverage.csv` |
| normalized edges | `<local private; not distributed>` |

Private inputs; aggregate outputs only.
