# Jinshi data: source, selection and known defect

Status: **confirmed from the 2024 graduation-project archive** (private: final
thesis, selection code and raw CBDB export). This replaces the earlier
"pending author confirmation" draft.

## 1. Source

| Item | Value |
|---|---|
| Database | China Biographical Database (CBDB), Harvard University / Peking University / Academia Sinica |
| Export | `入仕查询结果` sheet, 16 columns |
| Raw file | `明进士.xlsx` — 28,761 rows, 27,711 unique `PersonID` |
| Pipeline input | `table_general.xlsx` — 25,187 rows (cleaned export) |
| Entry types | observed: `科舉: 進士(籠統)` 28,697 + `科舉: 武舉進士` 64. The thesis also names `正奏名進士`, but that string does not occur in this export; treat it as a CBDB query category, not an observed value. |
| Fields | `Name`, `NameChn`, `PersonID`, `IndexYear`, `EntryDesc`, `EntryChn`, `EntryYear`, `EntryRank`, `KinType`, `KinName`, `KinChn`, `AddrName`, `AddrChn`, `X`, `Y`, `xy_count` |

All 911 published records are civil `進士(籠統)`; no 武舉 record is in the figures.

The thesis reports 25,188 cleaned Jinshi records; the attached
`table_general.xlsx` has 25,187 (one-record export difference). The full CBDB
export is **not redistributed**; only aggregate counts are published.

**Version note (2026-11-14):** the xlsx was created 2023-12-09; 209 of the
27,711 `PersonID`s are absent from the 2026-11-07 CBDB build (664,158 persons).
The export version is therefore unresolved (likely an older/merged release).
This is a data-version caveat, not a conclusion about redistribution; raw
records remain private.

**Boundary note:** the thesis states 25,188 cleaned records, 1甲 297, 2甲 5,812
and a 12.3% deletion rate. Those figures do **not** reconcile with the export
(25,187 / 260 / 6,500 / 0.45%). Use the archive for the intended rules, and the
actual export for counts. Full reconciliation:
[`data_boundary_audit.md`](data_boundary_audit.md).

## 2. Coverage

Aggregate tables are published in
[`data/derived/`](../data/derived/README.md): `jinshi_by_year_1521_1619.csv`
and `jinshi_rank_summary.csv`. They contain counts only, no individual records.

| Metric | Raw export | 1521–1619 window |
|---|---:|---:|
| Rows | 28,761 | 11,688 |
| Unique `PersonID` | 27,711 | 11,624 |
| 1甲 | 263 | 101 |
| 2甲 | 6,587 | 2,752 |
| 3甲 | 17,874 | 8,575 |
| Rank unparsed | 4,037 | 260 (244 missing + 16 malformed) |
| Elite (1甲 + 2甲, strict regex, civil) | — | 2,853 |
| Elite with coordinates | — | 2,841 |

### 2.1 Unparsed ranks and 武舉

The 260 unparsed window rows are not all unknown ranks:

| Group | Rows | With coordinates |
|---|---:|---:|
| Missing `EntryRank` | 244 | 225 |
| `0` placeholder | 11 | 11 |
| `第1/2/3名` | 3 | 3 |
| Prose containing `二甲` | 2 | 1 |

Malformed strings are only six distinct values (`0`, `第1/2/3名`, two prose
`二甲` forms). 武舉: 64 rows in the export, 9 in 1521–1619, **0 elite in the
window**; one 2甲 武舉 is dated 1637, outside the window. The 2,853 layer is
civil-only.

Civil elite bounds:

| Definition | Rows |
|---|---:|
| Strict regex, civil 1甲/2甲 | 2,853 |
| + 2 prose `二甲` (confirmed) | **2,855** |
| + 2 civil `第1/2/3名` (probable 1甲) | 2,857 |
| Upper bound: all civil unparsed treated as elite | 3,104 |

Use **2,855** as the confirmed lower bound and 3,104 as the civil-only upper
bound. The published 2,841 is the strict-with-coordinates layer; adding the one
prose `二甲` with coordinates gives 2,842. The difference is 1–3 records, so the
models are not re-run. Full audit: [`jinshi_unparsed_audit.md`](jinshi_unparsed_audit.md).

## 3. Selection used for the published 911 layer

The analysis code (`000SS进士.py`, `102进士聚类保存.py`) does:

```python
data = pd.read_excel("table_general.xlsx").dropna(subset=["EntryRank"])
important = data[data["EntryRank"].str.contains(r"第1甲|第2甲", na=False)]
important = important.dropna(subset=["EntryYear"])
important["level"] = important["EntryRank"].apply(
    lambda x: 1 if "第1甲" in x else 2
)
# SS-DBSCAN, eps=0.7, min_samples=3, weights=[1,1,0.3,0.1],
# max_cluster_size=100, is_important = level in [1, 2]
```

It is **not** a random sample and **not** a rank-complete sample.

## 4. Known defect: mixed numeral systems

CBDB encodes the same rank in two ways:

| Encoding | Example | Matches `第1甲|第2甲` |
|---|---|---|
| Arabic | `第1甲第3名` | yes |
| Chinese | `第一甲第三名` | **no** |

Within 1521–1619 the elite records split 929 Arabic vs 1,916 Chinese
(32.6% / 67.2%). The literal regex therefore keeps only the Arabic-coded
third of the elite population.

Reconciliation to the published table:

| Step | Rows |
|---|---:|
| Raw export | 28,761 |
| Arabic 1/2甲 in 1521–1619 (raw export) | 929 |
| Pipeline table `table_general.xlsx` | 25,187 |
| Arabic 1/2甲 in 1521–1619 (pipeline table) | 918 |
| Same, from 1522 (嘉靖 era) | **911** |
| Published `clustered_jinshi.xlsx` | **911** |

The 7-record gap (918 → 911) is exactly the 1521 exam cohort (7 × 第2甲); the
published layer starts in 1523.

## 5. Consequences

1. **The 1523/1526 peak is an encoding artefact.** Both years are written
   almost entirely in Arabic numerals (1523: 135 Arabic / 0 Chinese;
   1526: 91 / 0), while 1521, 1529, 1535, 1538, 1541, 1544, 1547, 1550,
   1553, 1556, 1559 and 1562 are written mostly in Chinese numerals and were
   silently dropped. The 24.6% concentration is therefore not a historical
   cohort effect.
2. **Zero 3甲 is by design**, not missing data: `is_important` keeps 1甲/2甲.
3. **Cluster sizes of exactly 100** come from `max_cluster_size=100`; they are
   truncated partitions, not natural clusters.
4. **The 911 layer cannot support** statements about exam-year composition,
   regional shares of all Jinshi, or "elite Jinshi" as a whole. It is **not**
   the input to the grid models: those use a broader series
   (`ming_general` + elite extension). A direct v0.2/v0.3 comparison is in
   [`corrected_robustness.md`](corrected_robustness.md): FDR discovery moves
   from 56/135 to 48/135, GWR coefficients agree at r = 0.991, and the median
   significant lag shifts from 11 to 6.5 years.

## 6. Corrected denominator

Use **2,855 elite records as the confirmed lower bound** (2,853 strict regex;
2,841 with coordinates), or **11,688 records** for all Jinshi in the window.
Normalize the rank field before filtering:

```python
RANK_RE = re.compile(r"^\s*(?:第)?\s*([一二三123])\s*甲")
```

Never match the literal string `第1甲` alone.

## 7. Reproduction

```bash
set MING_JINSHI_RAW=<path to the private CBDB export>
set MING_JINSHI_PIPELINE=<path to the private cleaned Jinshi table>
python scripts/audit_jinshi_encoding.py
# -> docs/jinshi_encoding_audit.md (aggregate only)
```

The raw tables stay outside the repository in a git-ignored private directory;
the graduation-project archive is private as well.

## 8. Wording for the README

> Jinshi records: CBDB `入仕查询结果` export (28,761 rows; 11,688 in
> 1521–1619). The 911-record figure layer is an **Arabic-numeral-coded subset**
> of the 1甲/2甲 elite, not a representative sample; see
> `docs/jinshi_encoding_audit.md`. Corrected elite denominator: 2,855 confirmed
> lower bound (2,853 strict regex; 2,841 with coordinates). Individual records
> are not redistributed.

