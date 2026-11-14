# B — exploratory feasibility memo (2026-11-14)

**Scope (roadmap §2 / user instruction)**: exploratory research only — data
lists, threshold status, earliest start, and who must supply what. **No B model
was run, no B result is claimed, no public text was changed for B.** Route C
remains frozen.

Literature / resource search performed on 2026-11-14 (allowed by the user) to
find new directions; every item below is a **lead requiring verification**, not
an acquired dataset.

---

## B1 — examination quotas as a moderator

**Question.** Did the 南/北/中卷 quota (55/35/10) moderate famine effects on
Jinshi? H1: tighter quotas weaken the *count* effect (seats fixed); H2: famine
still changes *rank composition* (marginal competition).

### Data needed

| # | Item | Status |
|---|---|---|
| 1 | Province/volume quota table, 1435–1619, with **time variation** | **unknown** — not in the repo |
| 2 | Quota changes over time | **lead found** (see below) |
| 3 | Province boundary → 1° grid mapping | **unknown** — CHGIS `province.shp` exists but no mapping built |
| 4 | Independent competition-intensity proxy (举人/生员 or candidates) | **unknown** — 郭培贵 gives exam-level admission rates, needs province×year |

### Threshold status (roadmap §2 B1)

| Gate | Requirement | Status |
|---|---|---|
| G1 | usable variation in quota by province × period; No-Go if fixed after 1435 | **unknown / promising** — search found documented changes: 正统元年「六、三、一」→ 正统四年「五五、三五、十」, plus later 科次 fluctuations; but no machine-readable table yet |
| G2 | reproducible province→grid mapping, ≥95% coverage | **unknown** (not attempted; B is plan-only) |
| G3 | competition proxy from an independent source, not reverse-engineered from Jinshi counts | **unknown** — 郭培贵《明代科举各级考试的规模及其录取率》gives 乡试 ~10%→5.9%→3.3%, 会试 ~8.6% average; a usable series, not yet acquired |

### Search leads (2026-11-14, verify before use)

- 郭培贵《中国科举制度通史·明代卷》(上海人民出版社, 2015) — quota institutions;
  郭培贵多篇论文 (光明日报/爱思想/中国社会科学网) confirm 55/35/10 and north–south
  rebalancing.
- 《明代会试分卷录取制创立、实施及变迁考实》 — reports **科次-level variation**
  in the split ratios; this is the single most relevant lead for G1.
- 郭培贵《明代科举各级考试的规模及其录取率》 — time series of 乡试/会试
  admission rates; candidate for G3, but must not be derived from our Jinshi
  counts.
- Bai & Jia (2016, *Econometrica*) — exam quotas shape regional elite outcomes
  (already cited in `docs/long_tail_analysis.md` §6.2) — institutional
  confound background.

### Go / No-Go

**Current: No-Go for modelling (data not acquired).** G1 has a plausible
positive lead, so B1 is *worth revisiting* rather than discarded. If a
machine-readable quota×year table is obtained and G1–G3 all pass, the
pre-registered model would be `famine × quota_tightness` on a fixed 1–5 year
window, reporting count and rank-share outcomes (the latter is already a
**null** in A1, which weakens H2).

### Earliest start / who supplies what

- After route A is frozen **and** a dated Go decision is recorded (roadmap §3).
- Needs: a digitised quota table (historian / library copy of 明会典 or
  郭培贵's tables), province→grid GIS work (project side), and an independent
  competition series. None can be produced automatically in this session.

---

## B2 — multi-hazard contrast

**Question.** Is famine special? Do flood, drought, locust and epidemic give
different conclusions on the same panel and fixed 1–5 year window?

### Data audit (step 1, actually performed — no modelling)

| Real table | Shape | Columns | Hazard-type field? |
|---|---|---|---|
| `merged_data.csv` | 15,311 × 5 | `year, code, level, X, Y` | **No** (`level` = severity 0–5) |
| `table_generals1521_1619.xlsx` | 5,767 × 5 | `_id, title, year, code, level` | **No** — `title` is "place + reign year" (e.g. 枣庄 正德十六年); the 104 hits on 「水」 are place names, not a flood label |
| `drought_events.xlsx` | 1,285 × 7 | `code, start_year, end_year, duration, max_level, avg_level, severity` | **No** — drought-episode aggregates, no type column |

**Coverage of a hazard-type field: 0%.** G4 (≥80% coverage, not a single
「灾荒」label) is **not met**.

### Threshold status

| Gate | Requirement | Status |
|---|---|---|
| G4 | hazard field ≥80% coverage, not a single label | **NOT MET** (0%) |
| G5 | ≥300 records per hazard class with spatial variation | **unknown** (no field to count) |
| G6 | consistent classification over time | **unknown** |

### Search leads (2026-11-14, verify before use)

- 夏明方 (2015)《大数据与生态史：中国灾害史料整理与数据库建设》,《清史研究》
  2:67–82 — survey of Chinese disaster-source databases.
- 《中国近三千年气象记录总集》、《中国蝗灾史》 — compiled sources used by
  李钢等 (2020)《1615—1619年中国蝗灾时空演化及环境背景研究》(地球环境学报
  11(3):245–254), which covers the tail of our window.
- 《明代雹灾的关联信息挖掘研究》 — a purpose-built Ming hail database with
  quantified severity; a model for how a hazard-specific table could be built.
- 山西大学《清代自然灾害史料长编》 — Qing only, useful as a *method* template,
  not as Ming data.

### Go / No-Go

**Current: No-Go.** Per roadmap §2, the fallback is a 30–50 record epidemic
pilot with a method note only — **not executed in this round** (B is plan-only).
Building a hazard-typed Ming table is a separate data project, not a modelling
task.

### Earliest start / who supplies what

- Needs a hazard-typed source (library/《总集》 or a collaborator's
  hazard database) plus 300+ records per class; then a fresh dated Go decision.
- Earliest: after route A freeze and a Go decision; project side would do the
  type harmonisation and G6 consistency check.

---

## B3 — one-page deliverable (this file)

- Two question data lists: §B1 and §B2 tables above.
- Every gate's current status: unknown / not met / promising lead (explicit).
- Earliest start and required suppliers: stated per section.
- **New directions discovered by search**: quota variation at the 科次 level
  (G1), province-level admission-rate series (G3), and existing Ming
  hail/locust hazard databases (G4 workaround).
- Not done: no model, no B result, no public-text change, no new data download.

## When this memo would fail

- If any lead is treated as an acquired dataset without verification.
- If a B model is run before a dated Go decision (roadmap §3 freeze rule).
- If route A is not actually frozen when B is revisited.
