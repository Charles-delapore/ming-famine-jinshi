# Data boundary audit: thesis statements vs the actual export

**Question:** does the graduation archive define the Jinshi data boundary clearly
enough to reproduce the counts?

**Short answer:** it defines the *intended* selection rules, but the headline
counts in the thesis do not reconcile with the export files. The archive is
useful for intent, not for verification.

## 1. What the archive states

Sources:

- `<private archive>\004\T1——文本新.docx` §1.3, §3.1, §4.1.1, §4.2.1, §4.3.2
- `<private archive>\009\...\古代灾荒事件...docx` §2.1 (final thesis)

Stated boundary:

| Item | Thesis statement |
|---|---|
| Source | CBDB `入仕查询结果` |
| Entry categories | 科举—进士（笼统）、科举—武举进士、科举—正奏名进士 |
| Cleaned records | **25,188** |
| Year range | 1351–1644 |
| Coordinates | based on 谭其骧《中国历史地图集》 |
| Missing-data rule | delete records with missing coordinates or year |
| Deletion rate | **12.3%** of Jinshi records (famine: 8.7%) |
| Elite subset | **1甲 297 + 2甲 5,812** |
| Code shown in thesis | literal `EntryRank.str.contains(r"第1甲|第2甲")` |

The same section explicitly shows the literal filter that later proved to be the
encoding bug. So the archive documents *how* the 911 layer was produced, but not
that the filter was correct.

## 2. What the files contain

| File | Rows | 1甲 | 2甲 | 3甲 | Unparsed |
|---|---:|---:|---:|---:|---:|
| `明进士.xlsx` | 28,761 | 263 | 6,587 | 17,874 | 4,037 |
| `明进士.xlsx`, 1351–1644 | 25,520 | 262 | 6,577 | 17,852 | 829 |
| same, with coordinates | 25,405 | 261 | 6,564 | 17,820 | 760 |
| `table_general.xlsx` | 25,187 | 260 | 6,500 | 17,644 | 783 |

The `25,187` pipeline table is one row short of the thesis `25,188` — consistent
with a minor export-version difference. The rank counts are not consistent:
thesis `297 / 5,812` vs pipeline table `260 / 6,500`.

The `12.3%` deletion rate is also not reproducible: within 1351–1644, only 115
of 25,520 rows lack coordinates (0.45%), not 12.3%.

## 3. Reconciliation table

| Quantity | Thesis | Actual export | Difference |
|---|---:|---:|---:|
| Cleaned rows | 25,188 | 25,187 (`table_general`) | −1 |
| 1甲 | 297 | 260 | −37 |
| 2甲 | 5,812 | 6,500 | +688 |
| Missing deletion | 12.3% | 0.45% (1351–1644, coordinates) | −11.85 pp |
| Year range | 1351–1644 | 1351–1643 in the subset | ~1 year |

Possible explanations (not mutually exclusive): the thesis used a different
export/query, counted before/after a different cleaning step, or the numbers
were transcribed from an intermediate run. The archive does not contain the
intermediate table that would settle it.

## 4. What this means for the project

1. **Use the archive for intent, not for counts.** The rules are clear: CBDB,
   three categories, drop missing coordinates/year, focus on 1甲/2甲. The
   headline counts are not reproducible.
2. **Use the actual export for numbers.** 28,761 raw rows; 25,187 pipeline rows;
   window 1521–1619: 11,688 rows, 1甲 101, 2甲 2,752, 3甲 8,575, unparsed 260.
3. **The 911 layer is explained by the literal filter**, not by a random sample
   or a rank-complete selection. The thesis itself shows the filter in §4.3.2.
4. **Do not cite `25,188 / 297 / 5,812 / 12.3%` as verified.** Cite them as
   "the thesis states", then give the reproducible export counts.

## 5. Version note

The export file was created **2023-12-09**; 209 of its 27,711 `PersonID`s are
absent from the 2026-11-07 CBDB build (664,158 persons). The export version is
unresolved (likely an older/merged release). This is a data-version caveat, not
a reason to stop the analysis; raw records remain private.

## 6. Bottom line

The archive gives a **stated boundary** and the exact buggy filter, but not a
**reproducible one**. The reproducible boundary is the one in
[`jinshi_provenance.md`](jinshi_provenance.md): 28,761 raw rows, 25,187 pipeline
rows, 11,688 in 1521–1619, 2,853 strict civil elite, 2,855 confirmed lower
bound.
