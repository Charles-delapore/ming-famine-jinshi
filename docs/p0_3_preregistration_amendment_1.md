# P0-3 pre-registration — Amendment 1 (2026-11-14)

**Dated amendment, written BEFORE any re-analysis.** It supersedes §3 of
`docs/p0_3_preregistration.md`. Per the original §7, thresholds and definitions
may only change through a new dated amendment; this is that amendment. It does
**not** touch §2 (dual proxy), §4 (time perturbation) or §5 (failure criteria),
whose results stand as reported.

## 1. What triggered the amendment

The original §3 assumed `xy_count` (from the CBDB `明进士.xlsx` export) was a
geographic-ambiguity proxy and split the elite extension into tiers 1/2/3 by
`xy_count` (1 / 2–10 / >10). Step 2 then dropped tier 3, which removed 90.7% of
the rows (2,841 → 265), and the result was already flagged as uninterpretable in
`docs/p0_3_sensitivity.md`.

`scripts/p0_3_verify_xy_count.py` (reproducible; output
`data/derived/p0_3_xy_count_semantics.csv`) checked the assumption against the
real table:

| Check | Result |
|---|---|
| `corr(xy_count, #records sharing the same (X,Y))` | **1.000000** |
| `corr(xy_count, #records sharing the same AddrChn)` | 0.920 |
| non-null `xy_count` | 26,863 / 28,761 (1,898 null, excluded pairwise) |
| `xy_count` min / median / max | 1 / 54 / 560 |
| share with `xy_count == 1` | 0.72% |
| share with `xy_count > 10`, full table | 80.7% |
| share with `xy_count > 10`, 2,841-row elite extension | **90.7%** (the step-2 drop) |
| unique (X,Y) / unique AddrChn | 1,435 / 1,584 |

Example: 莆田 at (119.011101, 25.433954) has 560 records, all with
`xy_count = 560`.

**`xy_count` is the number of records sharing the same coordinate** — a measure
of geographic aggregation / recording density, **not** geographic ambiguity or
coordinate precision. The §3 tiering was a **conceptual error**, not merely a
bad threshold.

## 2. Decisions (fixed, no post-hoc tuning)

1. **§3 of the pre-registration is withdrawn.** The tier rule
   (`xy_count == 1` / `2–10` / `>10`) is void.
2. **The step-2 result in `docs/p0_3_sensitivity.md` is withdrawn as a
   coordinate-confidence finding.** The values "134 grids / 68 FDR / 10.0 yr
   median lag" reflect a ~91% sample-size reduction and must not be interpreted
   as a precision effect. They are retained in the document only as an audit
   trail, explicitly marked void.
3. **No replacement tiering is introduced in this amendment.** The CBDB export
   has no 精确到县 / 仅到府 / 仅到省 label. `AddrChn` suffixes are unreliable as
   an administrative level (suffix counts: no suffix 23,443; 州 2,363; 縣 1,926;
   衛 746; 府 271; 道 6; 路 4; 省 2) — 州/府/縣 are frequently parts of place
   names, not level markers, and 衛 is a military unit. Inventing a new proxy
   now would be post-hoc tuning.
4. **P0-3 step 2 is therefore declared "not decidable with the available data"
   and converted to a method note**, consistent with plan §2 P1-7 ("coverage
   insufficient → write a method note only"). No robustness conclusion about
   coordinate confidence is claimed.
5. **§7 still holds**: no silent threshold changes, no re-running until a
   result "looks right".

## 3. What would be needed to actually do step 2

- A geocoding table with an explicit `admin_level` (county / prefecture /
  province) per Jinshi record, or
- A human-annotated stratified sample with documented agreement, plus
- A **new dated amendment** fixing the tiers and the drop rule before any
  re-run.

Until then, the correct output for step 2 is a method note, not a number.

## 4. Constructive by-product (recorded, not acted on)

The verified meaning of `xy_count` makes it a usable **record-density**
indicator for future work (e.g. the P1-7 elite-funnel coverage audit), where
many people sharing one coordinate is exactly the quantity of interest. It is
**not** used here to re-score the P0-3 record-intensity proxies (§2), which stay
frozen.

## 5. Effect on the P0-3 headline

- Time perturbation (§4) and dual-proxy stratification (§2) are unaffected.
- The combined conclusion loses its "coordinate precision" line; the honest
  statement is: *coordinate-confidence sensitivity could not be evaluated with
  the available fields.*
- The "under which perturbation the conclusion fails" sentence (median lag at
  k=+5) is unchanged.
