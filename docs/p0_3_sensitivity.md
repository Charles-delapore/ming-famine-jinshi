# P0-3 sensitivity — time perturbation (step 3)

- Generated: 2026-11-14 14:54
- Command: `python scripts/p0_3_time_perturbation.py`
- Pre-registered choices and failure criteria: `docs/p0_3_preregistration.md` (frozen before this run).
- Input: real `output/v03/panel_v03.csv.gz`; method unchanged (`scripts/corrected_robustness.run_granger`).

**Verdict: FAIL** (1 failure criterion/criteria triggered).

| k (yr) | grids tested | causal p<0.05 | FDR-significant | median FDR lag (yr) |
|---:|---:|---:|---:|---:|
| -5 | 135 | 73 | 52 | 8.0 |
| -3 | 135 | 76 | 60 | 6.0 |
| -1 | 135 | 76 | 49 | 4.0 |
| +0 | 135 | 67 | 48 | 6.5 |
| +1 | 135 | 61 | 40 | 9.5 |
| +3 | 135 | 52 | 27 | 9.0 |
| +5 | 135 | 46 | 18 | 12.0 |

## Failure criteria (fixed before results)

- Discovery count: any `|k|=1` run outside [24, 72] FDR grids (baseline 48).
- Median lag: any run more than 5.0 yr from 6.5 yr, or a monotone drift > 5 yr on either side.
- Record bias: the dual-proxy condition (§2 of the pre-registration) is evaluated in a later step, not here.

## Under which perturbation the conclusion fails

- k=+5: median FDR lag = 12.0 yr, more than 5.0 yr from baseline 6.5 yr

The corresponding headline conclusion does **not** survive these perturbations within the pre-registered tolerances.

## Limitations

- Only the famine series is shifted; Jinshi years are held fixed. This tests time alignment, not independent dating error in both series.
- Records shifted outside 1520–1619 are dropped; all `k` are treated identically, so the comparison is fair but boundary information is lost.
- This is step 3 of P0-3 only. Record-intensity stratification (step 1) and coordinate-tier dropping (step 2) are separate, and no claim about reporting bias is made from this table alone.
- Thresholds were fixed before the run; changing them requires a new dated pre-registration amendment.

Machine-readable: `data/derived/p0_3_sensitivity_time.csv`. Figure: `figures/p0_3_time_perturbation.{png,pdf}`.

## Step 1 — dual-proxy record stratification

Pre-registered: split each proxy at the median of **non-zero** grids; outcome is the mean of `gc_z_to_j_fdr_sig` in the real v0.3 Granger table. A record-bias explanation is supported only if **both** proxies show a gap ≥ 10 pp.

| Proxy | median (non-zero) | n high | n low | FDR rate high | FDR rate low | gap (pp) | ≥10pp |
|---|---:|---:|---:|---:|---:|---:|---|
| A endogenous record density | 99.0 | 67 | 68 | 0.388 | 0.324 | +6.5 | no |
| B exogenous administrative density | 1.0 | 35 | 100 | 0.457 | 0.320 | +13.7 | yes |

**Dual-proxy verdict: NOT SUPPORTED** (at least one proxy fails the 10 pp bar). Proxy A is endogenous with the famine series, so a gap there alone is an upper bound on record bias, not a causal estimate.

Asymmetry worth recording: proxy A gap = +6.5 pp (below the bar), proxy B gap = +13.7 pp (above it). The exogenous proxy does indicate a higher FDR-discovery rate in administratively dense grids, while the endogenous proxy does not amplify the gap. Under the frozen two-proxy rule the joint condition is not met, so no record-bias attribution is claimed; this asymmetry is a prompt for a dedicated study, not evidence.

## Step 2 — coordinate-confidence tier drop

> ⚠️ **VOID per `docs/p0_3_preregistration_amendment_1.md` (2026-11-14)**: `xy_count` is the number of records sharing the same (X,Y) coordinate, not a coordinate-precision proxy. The tier rule below and its results are withdrawn; step 2 is not decidable with the available fields. Values are kept only as an audit trail.

Pre-registered tiers on `xy_count`: tier 1 = 1, tier 2 = 2–10, tier 3 = > 10 (dropped). `xy_count` is a geographic ambiguity proxy, **not** a 县/府/省 label in the source.

| Quantity | Value |
|---|---:|
| elite extension rows before | 2,841 |
| tier 1 (`xy_count`=1) | 16 |
| tier 2 (2–10) | 249 |
| tier 3 (>10, dropped) | 2,576 (90.7%) |
| unknown (NaN, kept) | 0 |
| elite rows kept | 265 |
| grids tested after drop | 134 |
| FDR-significant after drop | 68 (baseline 48) |
| median FDR lag after drop | 10.0 yr (baseline 6.5) |

Limitation: `ming_general.csv` (the 6,935-row base series) has no `xy_count` column, so the tier drop applies only to the elite extension; NaN `xy_count` rows were kept. This is a partial coordinate-precision check, not a full re-geocoding.

⚠️ **Validity caveat (recorded, not post-hoc tuned)**: tier 3 covers 90.7% of the elite extension, so the drop shrinks the series from 2,841 to 265 rows. The change in FDR-significant grids and median lag is therefore **confounded with a large sample-size reduction** and cannot be attributed to coordinate precision. The semantics of `xy_count` (it may count records sharing a coordinate, not geographic ambiguity) must be verified before step 2 is interpretable. Per pre-registration §7 the threshold is NOT changed here; this is logged as a design defect requiring a dated amendment.

## Combined conclusion

- **Time perturbation**: see the table and figure above; the discovery-count and lag conclusions survive ±1 yr and most larger shifts, but the pre-registered lag tolerance is breached at k=+5.
- **Record bias**: dual-proxy condition is not met; the 48/135 finding is not shown to be attributed to record intensity on this evidence.
- **Coordinate precision**: dropping the pre-registered tier-3 elite rows changes FDR-significant grids from 48 to 68 and the median lag from 6.5 to 10.0 yr, but ~91% of the extension is removed, so this is **not interpretable** as a coordinate-precision effect (see the validity caveat above).

## Under which perturbation the conclusion fails

The median-lag conclusion fails the pre-registered tolerance at k=+5 (12.0 yr vs 6.5 yr baseline, a 5.5 yr deviation). The discovery count stays within [24, 72] for every |k|=1 run, so 48/135 itself survives conservative year error; it is the **lag claim** that is least robust. Step 2 is not interpretable until `xy_count` semantics are verified.

Appended by `python scripts/p0_3_proxies_and_tiers.py` (2026-11-14 15:28). Machine-readable: `data/derived/p0_3_proxy_stratification.csv`, `data/derived/p0_3_coordinate_tiers.csv`.
