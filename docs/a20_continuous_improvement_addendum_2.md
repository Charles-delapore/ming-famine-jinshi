# A20 — continuous-improvement addendum 2 (2026-11-14)

**User instruction**: continue improvement and data analysis, keep per-segment
worklog, literature/resource search and external-data acquisition allowed.
**Constraints**: private inputs, aggregate outputs.

Sits on top of `docs/a8_freeze_review.md` (freeze),
`docs/a11_freeze_addendum.md`, `docs/a16_continuous_improvement_addendum.md`.
Third round. Route A remains frozen; `docs/a3_main_results.md` headline
numbers are **unchanged**.

---

## 1. What triggered this round

The previous round closed P1-7 (elite network) as **NO-GO** at 15.4% coverage,
but noted that CBDB `KIN_DATA` (565,276) / `ASSOC_DATA` (190,164) had not been
audited. This round audits them and decomposes A12's early-Ming contribution.

## 2. Three analyses

| # | Script | Pre-registration | Result |
|---|---|---|---|
| A17 | `a17_cbdb_network_coverage.py` | same 30% gate as A14, unchanged | **GO, 56.4%** |
| A18 | `a18_ego_network_analysis.py` | `docs/a18_ego_network_preregistration.md` (frozen before run) | descriptive inventory |
| A19 | `a19_early_ming_decomposition.py` | `docs/a19_early_ming_preregistration.md` (frozen before run) | early Ming drives A12's extra grids |

### A17 — P1-7 prerequisite flipped to GO

| Source | unique persons | Jinshi overlap | coverage |
|---|---:|---:|---:|
| `KIN_DATA` | 288,981 | 15,089 | 54.5% |
| `ASSOC_DATA` | 44,834 | 4,585 | 16.5% |
| `ENTRY_DATA` | 221,605 | 27,501 | 99.2% (exam entries, **not** a network) |
| **KIN ∪ ASSOC** | 313,115 | **15,616** | **56.4%** |

Using the **same pre-declared 30% gate** as A14 (no threshold change), the
full CBDB graph clears it: A14's 15.4% was an artifact of using three
incomplete query exports. P1-7's prerequisite is now met. `ENTRY_DATA`
coverage is reported separately and excluded from the verdict.

### A18 — descriptive ego-network (no inferential claim)

`docs/a18_ego_network_preregistration.md` froze all measures before the run.

- **15,616 egos** (56.35% of 27,711 Jinshi PersonIDs); median total degree
  **9** (Q25 7 / Q75 12, max 334); 89.9% have degree ≥ 5, 43.4% ≥ 10.
- 133,868 kin edges / 39,989 association edges; top kinship types are
  **弟 (31,161), 兄 (19,849), 父 (14,406), 祖父 (14,117), 曾祖 (14,017),
  妻子 (13,627), 母 (13,085)** — close agnatic/direct kin.
- Kin address coordinate coverage **51.5%** (just above the 50% gate), so
  geographic measures are estimable: median kin distance **0.000°**,
  **95.4%** of kin in the same 1° grid.
- Grid correlations: network degree vs v0.3 Jinshi count r = **0.906**
  (Spearman 0.950); vs famine level r = 0.690 (0.605).

**Mandatory caveat (written into both the script and the results doc)**: the
r≈0.91 correlation is **mechanically expected** — both quantities come from
the same Jinshi persons in a grid; more egos means both more recorded kin and
more Jinshi. The ~95% same-grid share largely reflects CBDB recording family /
ancestral addresses at one location. **Neither is evidence that social
networks explain elite production.** No model, no p-value, no causal claim.
The three-stage funnel (举人完整度) remains out of scope.

### A19 — A12's extra grids come from early Ming

Same panel, same method, four frozen windows:

| Window | Years | grids tested | FDR grids | % |
|---|---|---:|---:|---:|
| early 1368–1520 | 153 | 127 | **10** | 7.87% |
| v0.3 1521–1619 | 99 | 142 | **1** | 0.70% |
| late 1620–1643 | 24 | **0** | 0 | not estimable |
| full 1368–1643 | 276 | 155 | 8 | 5.16% |

FDR is recomputed within each window, so counts are **not additive**. The
late window is below the ≥30-observation filter. The full-window 8 grids are
attributable to the **early-Ming** slice, where records are sparser and
differently documented — a documentation caveat, not a stronger effect. This
**reinforces** the methodological warning that a "full-window" count is not a
single stable effect. No verdicts, no respecification.

## 3. Literature / resource search (allowed)

Web search on 明代会试南北中卷配额 returned concrete **institutional time
variation** relevant to B1's G1 gate:

- 洪熙元年 (1425) 南北卷；宣德二年 (1427) 正式南/北/中卷 **55/35/10**；
- 正统元年「六、三、一」→ 正统四年「五五、三五、十」；
- 景泰年间短暂废止，五年后恢复；
- 成化二十二年 (1486) 中卷加额；正德三年 (1508) 中卷并入南北、南北均额，
  不久恢复旧例；
- 《明史选举志考论》含「明代各直省乡试录取额数沿革表」「明代历科会试、
  殿试、庶吉士录取名数表」；郭培贵《中国科举制度通史·明代卷》为制度来源。

**Status update for B1 G1**: from "unknown / promising lead" to
"**documented institutional variation exists in the literature, but no
machine-readable quota×year table was obtained**". G2/G3 remain unknown;
B1 is still **No-Go for modelling**. No table was fabricated. All items are
leads requiring verification before use.

## 4. What changed and what did not

| Item | Status |
|---|---|
| `docs/a3_main_results.md` headline numbers | **unchanged** |
| P1-7 (elite network) | **NO-GO → GO** on coverage; descriptive ego-network executed; funnel still out of scope |
| A14 (`docs/a14_elite_network_audit.md`) | superseded by A17 for the coverage verdict (its 15.4% was export-limited) |
| A12 full-window result | attributed to early Ming; documented, not re-interpreted |
| Route-A core claims | unchanged; A19 strengthens the "no single stable full-window effect" warning |
| B1 / B2 / C | still need external data; C still frozen |
| Push | **none** |

## 5. New open items

1. A18's descriptive correlations are mechanical; a genuine network question
   would require a **new dated pre-registration** with a design that separates
   degree from person count (e.g. mean degree per ego, or external instruments).
2. The 51.5% kin-address coverage is marginal; better geocoding would be needed
   before any spatial network claim.
3. B1 still needs a digitised quota table (library / 郭培贵 tables); B2 a
   hazard-typed source; C Qing data.
4. CBDB auto-generated kinship edges are not independently verified.
5. Push / Zenodo DOI / GitHub release remain deferred.

## 6. When this addendum would fail

- A18's correlations are quoted as evidence about elite reproduction.
- A19 counts are treated as independent samples or as a new effect.
- Search leads are treated as acquired data.
- Any headline or public page is changed without re-running
  `python scripts/a0_apply_claims.py --check`.

Private inputs; aggregate outputs only.
