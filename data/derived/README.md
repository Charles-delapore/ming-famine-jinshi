# Derived Jinshi aggregates

These files contain **aggregate counts only**. No CBDB `PersonID`, name,
address or coordinate is included.

| File | Contents |
|---|---|
| `jinshi_by_year_1521_1619.csv` | per exam year: records, 1甲/2甲/3甲, unparsed, Arabic-coded, Chinese-coded, rows with coordinates |
| `jinshi_rank_summary.csv` | headline totals, including the corrected elite denominator (2,853) and the published 911 layer |
| `jinshi_unparsed_summary.csv` | unparsed-rank groups, 武舉 counts, and the civil elite bounds |
| `v03_model_summary.csv` | aggregate v0.2/v0.3 Granger, GWR, multiscale and GeoDetector metrics |

Rebuild:

```bash
set MING_JINSHI_RAW=<path to the private CBDB export>
python scripts/make_jinshi_aggregates.py
```

Why the 911 layer is not used as a denominator:
[`../../docs/jinshi_provenance.md`](../../docs/jinshi_provenance.md) and
[`../../docs/jinshi_encoding_audit.md`](../../docs/jinshi_encoding_audit.md).

Source: China Biographical Database (CBDB), `入仕查询结果` export.

