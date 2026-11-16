# Data provenance

Status: **Jinshi provenance confirmed** (2026-11-14) from the 2024 graduation
archive. The earlier "pending author confirmation" version is superseded by
[`jinshi_provenance.md`](jinshi_provenance.md) and
[`jinshi_encoding_audit.md`](jinshi_encoding_audit.md).

## Layers

| Layer | Source | Status |
|---|---|---|
| Jinshi | CBDB `入仕查询结果` export (28,761 rows; 11,688 in 1521–1619) | confirmed; 911 figure layer is a format-selected subset |
| Famine | Work_ming v5 result tables (5,736 clustered events) | confirmed; private raw tables |
| Basemap | CHGIS v6 province boundaries; Natural Earth 1:110m for the synthetic sample | confirmed |
| Climate | Paleoclimate reconstruction used by Work_ming v5 | upstream tables not redistributed |

## Jinshi in one paragraph

The raw CBDB export contains 1甲, 2甲 and 3甲 records. The earlier v0.2
figures used **911 records** produced by filtering `EntryRank` with
`第1甲|第2甲`. Because CBDB writes ranks in both Arabic (`第1甲`) and Chinese
(`第一甲`) numerals, that filter kept only the Arabic-coded third of the elite.
The 1523/1526 spike and the absence of 3甲 are artefacts of this filter.
Corrected elite denominator for 1521–1619: **2,855 confirmed lower bound**
(2,853 strict regex; 2,841 with coordinates). Details, counts and the
normalization rule are in [`jinshi_provenance.md`](jinshi_provenance.md),
[`jinshi_unparsed_audit.md`](jinshi_unparsed_audit.md) and
[`data_boundary_audit.md`](data_boundary_audit.md).

**The 911 layer is retained only as an audit.** The v0.3 figures and grid
models use the normalized elite extension; the v0.2/v0.3 sensitivity check is in
[`corrected_robustness.md`](corrected_robustness.md).

## Redistribution

- Individual CBDB records are **not** redistributed.
- Famine and Jinshi raw tables stay outside the repository.
- The public repository ships synthetic sample data plus aggregate audits only.
- Aggregate counts in `docs/jinshi_*.md` may be cited with attribution to CBDB.

## Route A sources (2026-11-14/15)

- **A9**: CBDB SQLite address dictionary, historical urban population workbook,
  late-Ming Jinshi table and CHGIS county points. Read-only, private.
- **A12**: independent famine source (`灾荒数据.zip` / `table_level.json`,
  69,276 city-year rows); licence not confirmed, so event rows and the derived
  panel are not redistributed.
- **A14/A17/A18**: CBDB `KIN_DATA` / `ASSOC_DATA` network tables. Person-level
  edges and ego degrees stay private; only coverage and summary aggregates are
  published.
- **A10**: the coordinate-tier assignment joins `PersonID` to coordinates and
  is private; only tier counts and sensitivity aggregates are published.

The published aggregates are described in
[`data_dictionary.md`](data_dictionary.md).
