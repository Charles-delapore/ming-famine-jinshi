# A18 pre-registration — descriptive ego-network study (2026-11-14)

**Written BEFORE running `scripts/a18_ego_network_analysis.py`.** Triggered by
`docs/a17_cbdb_network_coverage.md`: with the full CBDB graph, KIN ∪ ASSOC
coverage of Jinshi PersonIDs clears the pre-declared 30% gate (A14's 15.4%
was an artifact of using incomplete query exports).

This is a **descriptive** study. It does not estimate a causal effect, does not
predict elite reproduction, and does not revisit route-A's frozen headline.

## 1. Scope

P1-7's "three-stage funnel" (举人完整度) still lacks data and is **out of
scope**. Only the **ego-network** part is executed, descriptively.

## 2. Data (frozen)

| Input | Source |
|---|---|
| kinship edges | CBDB `KIN_DATA` (565,276 rows; `c_personid`, `c_kin_id`, `c_kin_code`) |
| association edges | CBDB `ASSOC_DATA` (190,164 rows) |
| kinship type labels | CBDB `KINSHIP_CODES` |
| person → address coordinates | `data/derived/a9_person_addr_link.csv` + `a9_cbdb_addr_admin_level.csv` (`x_coord`, `y_coord`, `c_admin_type`) |
| Jinshi universe | `明进士.xlsx` PersonIDs (27,711) |
| grid outcomes | `<local private input; not distributed>` and `output/v03/panel_v03.csv.gz` |

## 3. Unit and measures (frozen)

- Ego = each **Jinshi PersonID** with ≥1 KIN or ASSOC edge.
- Per ego (descriptive):
  - `kin_degree` = number of distinct `c_kin_id` in `KIN_DATA`;
  - `assoc_degree` = number of distinct association counterparts;
  - `total_degree` = union of both;
  - dominant kinship type from `KINSHIP_CODES` (top-1 by count).
- Geographic (descriptive):
  - ego address coordinate = **finest administrative tier** address
    (same rule as Amendment 3), else the first available;
  - kin address coordinates via `BIOG_ADDR_DATA` → `ADDR_CODES`;
  - `mean_kin_distance_deg` = mean great-circle-free degree distance from ego
    to kin coordinates (reported as degrees, not km);
  - share of kin in the **same 1° grid** as the ego.
- Grid-level (descriptive correlation only):
  - aggregate `total_degree` by ego grid;
  - Pearson/Spearman correlation with (a) grid Jinshi count in the v0.3 panel,
    (b) grid famine level in the full-Ming panel.

## 4. Decision / reporting rules (frozen)

- **All results are descriptive.** No p-value, no significance claim, no
  model, no control variables, no subgroup search after seeing results.
- Report distributions (median, quartiles, share with degree ≥ 1 / ≥ 5 / ≥ 10),
  the top-10 kinship types, and the two grid-level correlations with their n.
- If a correlation is weak or negative, record it as-is; do not respecify.
- If address coverage for kin is < 50%, report the geographic measures as
  **not estimable** rather than imputing.
- No threshold, unit or measure is changed after seeing results.

## 5. Failure / interpretation limits

- CBDB kinship includes auto-generated / inferred relations; edge quality is
  not independently verified.
- `KINSHIP_CODES` labels are CBDB's own taxonomy; no re-coding.
- Degree is a **recording-intensity proxy** as much as a social one — a
  well-documented person has more recorded kin. This is stated, not corrected.
- Address coordinates are historical point locations, not exact residences.
- Grid correlations are ecological and may reflect documentation density.

## 6. What will not be done

- No ego-network → Jinshi causal model, no regression, no SHAP/ML.
- No three-stage funnel (举人完整度 missing).
- No change to `docs/a3_main_results.md` headline numbers.
- Outputs are aggregate only.

## 7. Outputs

`data/derived/a18_ego_network_summary.csv`,
`<local private; not distributed>`,
`data/derived/a18_grid_correlations.csv`,
`docs/a18_ego_network_results.md`.
