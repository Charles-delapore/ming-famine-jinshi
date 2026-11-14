# P0-3 data feasibility and proxy choices (2026-11-14)

**Status: read-only inventory + design memo. No model has been re-run and no
robustness conclusion is claimed here.** P0-3 ("reporting bias and uncertainty")
is the core scientific item in `<internal work plan>`; it
needs a defensible "record-intensity proxy" before any sensitivity table is
produced. This memo records what the data actually contain and where a judgement
call is still required.

## 1. Available real data (all read-only, private, not redistributed)

| Path | Shape | Columns | Relevance |
|---|---|---|---|
| `output/v03/panel_v03.csv.gz` | 33,174 × 7 | `year, grid_x, grid_y, zaihuang_level, zaihuang_count, zaihuang_severity, jinshi_count` | yearly 1° panel — **enough for time perturbation** |
| `output/v03/granger_v03.xlsx` | 135 × 16 | `grid_x, grid_y, n_years, zaihuang_years, jinshi_years, gc_z_to_j_*, gc_j_to_z_*, causal_direction, gc_z_to_j_qval, gc_z_to_j_fdr_sig` | per-grid Granger + BH FDR outcome to compare |
| `output/v03/gwr_v03.xlsx` | 159 rows | GWR cells | secondary outcome |
| `<path to the private CBDB export>` | 28,761 × 16 | `NameChn, PersonID, IndexYear, EntryYear, EntryRank, AddrName, AddrChn, X, Y, xy_count, ...` | raw CBDB Jinshi, with place names and coordinates |
| `<path to the private cleaned Jinshi table>` | 25,187 × 16 | same | cleaned pipeline Jinshi table |
| `<path to the private famine table>` | 15,311 × 5 | `year, code, level, X, Y` | famine events (`level` = severity 0–5, **not** coordinate confidence) |
| `<path to the private city points>` | 251 × 6 | `_id, title, code, type, x, y` | 251 administrative point locations; `type` is only `Point` |
| `<path to the private Jinshi extension>` | 6,935 × 3 | `EntryYear, X, Y` | Jinshi extension used by the panel |
| `<path to the private famine export>` | 5,767 × 5 | `_id, title, year, code, level` | famine events, alternate export |

Confirmed **absent**: any field for 方志存世量 (surviving gazetteer counts),
population density, or an explicit 精确到县 / 仅到府 / 仅到省 coordinate-confidence
label. `table_citys.type` is a geometry tag (`Point` for all 251 rows), and
`merged_data.level` is famine severity (counts 0:12,037, 2:1,192, 4:994,
3:847, 5:209, 1:32). Both steps 1 and 2 therefore require **constructed
proxies**, not a column lookup.

## 2. Feasibility of the three planned steps

| Step | Plan | Data support | Verdict |
|---|---|---|---|
| 1. Record-intensity stratification | compare FDR discovery rate in high vs low record areas | panel + granger tables present; proxy must be constructed | **Feasible, proxy undecided** |
| 2. Coordinate confidence | county / prefecture / province only; drop low-confidence and re-run | `AddrChn`, `X/Y`, `xy_count`, `code` available; no explicit tier label | **Feasible as a proxy tiering, rule undecided** |
| 3. Time perturbation | ±1/±3/±5 years on years, re-run short-horizon conclusion | full yearly panel + reusable `scripts/corrected_robustness.py` pipeline | **Directly executable** |

## 3. Record-intensity proxy — candidates (needs a decision)

| Candidate | Construction | Defensibility | Main risk |
|---|---|---|---|
| **A. Endogenous record density** | total `zaihuang_count` per 1° grid over 1522–1619; split high/low at the median; compare `gc_z_to_j_fdr_sig` rate | Standard "reporting density" proxy: more recorded events ⇒ better-documented region | **Endogenous** with the famine variable; high-record cells are mechanically likelier to yield a Granger signal. Any difference is an **upper bound** on bias, not a causal estimate. |
| **B. Exogenous administrative density** | count of `table_citys.xlsx` points per 1° grid (251 points) as a proxy for administrative/record coverage | Largely independent of famine counts → cleaner separation | Only 251 points; sparse outside core areas, so many grids get 0. |
| **C. Dual proxy (recommended)** | run A and B separately and report both | A difference that appears under both proxies is harder to dismiss as an artefact of A's endogeneity | More work; must still state A's endogeneity caveat. |

Recommendation: **C**, with A explicitly labelled as an upper bound and B as the
weaker-but-cleaner check. Do not present a single proxy as "the" record strength.

## 4. Coordinate-confidence tiering — candidate rule (needs a decision)

`xy_count` in the CBDB tables is the number of coordinate matches for an address
(observed values include 560, 64, 21, 12, 11, 10, ...). Larger values indicate a
generic / ambiguous place name, i.e. lower geographic precision. Candidate tiers:

- Tier 1 (highest): `xy_count == 1` — unique coordinate.
- Tier 2: `2 <= xy_count <= 10` — limited ambiguity.
- Tier 3 (lowest): `xy_count > 10` — likely a prefecture/province-level or
  heavily shared name; drop in the sensitivity run.

`AddrChn` examples (長洲, 新建, 鄱陽, 蔚州, 雲南後衛, 豐城) and `code` can be used
to sanity-check the tiers. **Caveat**: this is a *proxy* for precision, not the
three-way 县/府/省 label the plan words it as; the memo should say so explicitly
rather than implying the source contains such a label. Thresholds (10, or a
quantile split) must be fixed before looking at the outcome to avoid tuning.

## 5. Time perturbation — ready to execute

- Input: `output/v03/panel_v03.csv.gz` (1520–1619 yearly, 291 grids).
- Perturb `year` of famine events by ±1/±3/±5 under a fixed seed, rebuild the
  grid panel, and re-run the Granger + BH-FDR pipeline in
  `scripts/corrected_robustness.py` (same code path, method unchanged).
- Compare against the v0.3 baseline: 48/135 FDR grids, median significant lag
  6.5 yr, and 8/0/0 short/medium/long horizons.
- Output: one sensitivity table + one figure; state explicitly under which
  perturbation each conclusion stops holding (plan DoD item 3).

## 6. Suggested order

1. Fix the proxy choices in §3–§4 (write them down **before** running anything).
2. Step 3 (time perturbation) first — it is fully determined and gives the
   sensitivity table/figure scaffolding.
3. Step 1 with dual proxies; step 2 with the pre-registered tiers.
4. Produce the combined sensitivity table + figure and the "when it fails" sentence.

## 7. Explicitly out of scope for this memo

- No new gazetteer / population download (plan §3: 暂缓 "再收集新报告/新 zip").
- No claim that 48/135 or the 6.5-year lag is or is not an artefact — that is the
  **output** of P0-3, not an input.
- No synthetic-data stand-in for the real panel; the real v0.3 panel is present.
