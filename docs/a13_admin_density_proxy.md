# A13 — admin-density proxy upgrade (2026-11-14)

- Generated: 2026-11-14 17:53
- Command: `python scripts/a13_admin_density_proxy.py`
- **Repeat of a pre-registered test** (`docs/p0_3_preregistration_amendment_2.md` §4) with improved data; pass criterion unchanged: monotone gradient AND ≥10 pp top-vs-bottom gap. No post-hoc tuning.
- Old proxy B: 251 `table_citys` points (median = 1, near-binary).
- New proxy: CHGIS v6 Ming-valid county points **2,183** (BEG_YR ≤ 1644, END_YR ≥ 1368), 326 grids.

| Level | n grids | median county points | FDR rate | FDR grids |
|---|---:|---:|---:|---:|
| 0 (no county point) | 0 | nan | nan | 0 |
| Q1 | 50 | 4 | 0.320 | 16 |
| Q2 | 25 | 6 | 0.280 | 7 |
| Q3 | 26 | 9 | 0.423 | 11 |
| Q4 | 34 | 13 | 0.412 | 14 |

- Monotone across levels: **False**
- Top-vs-bottom gap: **+9.2 pp** (old proxy B: +1.3 pp)
- Dose-response supported: **False**

## Interpretation

The criterion is still **not met**: discovery rates do not show a monotone ≥10 pp gradient even with a ~9x denser, time-validated administrative proxy. This **strengthens** the frozen P0-3 conclusion of no record-intensity dose-response, because the previous near-binary proxy was the weak link.

## Limits

- CHGIS county points are historical point locations; grid assignment is approximate and the panel is 1° (MAUP applies).
- `BEG_YR`/`END_YR` filter keeps units valid at some point in 1368–1644; it does not model within-period establishment/abolition.
- The outcome is the frozen v0.3 `granger_v03.xlsx` FDR flag (135 grids); no model was re-estimated.
- Quartiles are computed on non-zero density with zeros as their own level, matching Amendment 2's zero-inclusive style; this is declared here, not chosen after seeing rates.

## When this would fail

- CHGIS layer or v0.3 Granger table replaced without re-running.
- A different binning is substituted after seeing the rates.
- The result is quoted as causal (it is a descriptive dose-response).

Machine-readable: `data/derived/a13_admin_density_dose.csv`.

Private inputs; aggregate outputs only.
