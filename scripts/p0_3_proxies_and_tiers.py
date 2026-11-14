"""P0-3 steps 1–2 (pre-registered): dual-proxy stratification and coordinate tiers.

Step 1 — record-intensity stratification with two fixed proxies, compared on the
FDR-discovery rate of the real v0.3 Granger table.
Step 2 — rebuild the Jinshi extension without the pre-registered tier-3
(xy_count > 10) rows and re-estimate Granger/FDR.

Choices and failure criteria are frozen in docs/p0_3_preregistration.md. This
script APPENDS its sections to docs/p0_3_sensitivity.md (idempotently).

Usage::

    python scripts/p0_3_proxies_and_tiers.py

Outputs::

    data/derived/p0_3_proxy_stratification.csv
    data/derived/p0_3_coordinate_tiers.csv
    docs/p0_3_sensitivity.md   (appended sections)

Reads private real data; outputs are aggregate only.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import corrected_robustness as cr  # noqa: E402

V03 = ROOT / "output" / "v03"
OUT_PROXY = ROOT / "data" / "derived" / "p0_3_proxy_stratification.csv"
OUT_TIERS = ROOT / "data" / "derived" / "p0_3_coordinate_tiers.csv"
DOC = ROOT / "docs" / "p0_3_sensitivity.md"

# Private real inputs. Same paths documented in corrected_robustness.py;
# overridable via the same MING_* environment variables.
PRIVATE = {
    "RAW": r"data/private/明进士.xlsx",
    "FAMINE_MERGED": r"data/private/merged_data.csv",
    "FAMINE_EXT": r"data/private/table_generals1521_1619.xlsx",
    "CITYS": r"data/private/table_citys.xlsx",
    "JINSHI_ALL": r"data/private/ming_general.csv",
}
ENV_KEYS = {
    "RAW": "MING_JINSHI_RAW",
    "FAMINE_MERGED": "MING_FAMINE_MERGED",
    "FAMINE_EXT": "MING_FAMINE_EXT",
    "CITYS": "MING_CITYS",
    "JINSHI_ALL": "MING_JINSHI_ALL",
}
for attr, default in PRIVATE.items():
    setattr(cr, attr, Path(os.environ.get(ENV_KEYS[attr], default)))

# FROZEN in docs/p0_3_preregistration.md.
PROXY_GAP_PP = 10.0
TIER3_THRESHOLD = 10
BASE_FDR = 48
BASE_LAG = 6.5


def step1() -> pd.DataFrame:
    """Dual-proxy high/low split; outcome = mean FDR-discovery rate."""
    granger = pd.read_excel(V03 / "granger_v03.xlsx")
    panel = pd.read_csv(V03 / "panel_v03.csv.gz")
    outcome = granger[["grid_x", "grid_y", "gc_z_to_j_fdr_sig"]].copy()

    # Proxy A — endogenous record density (famine records per grid).
    a = (
        panel.groupby(["grid_x", "grid_y"])["zaihuang_count"]
        .sum()
        .rename("proxy_a")
        .reset_index()
    )
    # Proxy B — exogenous administrative point density (251 city points).
    city = pd.read_excel(cr.CITYS)
    city["grid_x"] = np.floor(city["x"] / 1.0) * 1.0 + 0.5
    city["grid_y"] = np.floor(city["y"] / 1.0) * 1.0 + 0.5
    b = city.groupby(["grid_x", "grid_y"]).size().rename("proxy_b").reset_index()

    m = outcome.merge(a, on=["grid_x", "grid_y"], how="left").merge(
        b, on=["grid_x", "grid_y"], how="left"
    )
    m[["proxy_a", "proxy_b"]] = m[["proxy_a", "proxy_b"]].fillna(0)

    rows = []
    for key, label in (("proxy_a", "A endogenous record density"),
                       ("proxy_b", "B exogenous administrative density")):
        nonzero = m.loc[m[key] > 0, key]
        median = float(nonzero.median()) if len(nonzero) else 0.0
        hi = m[m[key] > median]["gc_z_to_j_fdr_sig"]
        lo = m[m[key] <= median]["gc_z_to_j_fdr_sig"]
        hi_rate, lo_rate = float(hi.mean()), float(lo.mean())
        gap = (hi_rate - lo_rate) * 100
        rows.append({
            "proxy": label,
            "median_nonzero": median,
            "n_high": int(len(hi)),
            "n_low": int(len(lo)),
            "fdr_rate_high": hi_rate,
            "fdr_rate_low": lo_rate,
            "gap_pp": gap,
            "meets_10pp": bool(gap >= PROXY_GAP_PP),
        })
    df = pd.DataFrame(rows)
    OUT_PROXY.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PROXY, index=False)
    return df


def step2() -> dict:
    """Drop tier-3 (xy_count > 10) elite rows, rebuild panel, re-run Granger."""
    for attr in PRIVATE:
        if not Path(getattr(cr, attr)).exists():
            raise SystemExit(f"missing private input: {getattr(cr, attr)}")
    famine = cr.load_famine()
    _, new_j, _ = cr.load_jinshi()
    base = pd.read_csv(cr.JINSHI_ALL).rename(columns={"EntryYear": "year"})[
        ["year", "X", "Y"]
    ]

    xy = pd.to_numeric(new_j.get("xy_count"), errors="coerce")
    tier = np.where(
        xy.isna(), "unknown",
        np.where(xy == 1, "1", np.where(xy <= TIER3_THRESHOLD, "2", "3")),
    )
    counts = pd.Series(tier).value_counts().to_dict()

    # NaN xy_count cannot be tiered; keep it (conservative) and record it.
    keep = new_j[xy.isna() | (xy <= TIER3_THRESHOLD)][["year", "X", "Y"]]
    panel_t = cr.build_panel(famine, pd.concat([base, keep], ignore_index=True))
    g = cr.run_granger(panel_t)
    fdr = g["gc_z_to_j_fdr_sig"]
    result = {
        "elite_rows_before": int(len(new_j)),
        "elite_rows_kept": int(len(keep)),
        "tier_counts": counts,
        "tier3_share": float(counts.get("3", 0)) / max(int(len(new_j)), 1),
        "grids_tested": int(len(g)),
        "fdr_sig": int(fdr.sum()),
        "median_lag": (
            float(g.loc[fdr, "gc_z_to_j_lag"].median())
            if fdr.any()
            else float("nan")
        ),
    }
    pd.DataFrame([{
        "elite_rows_before": result["elite_rows_before"],
        "elite_rows_kept": result["elite_rows_kept"],
        "tier3_share": result["tier3_share"],
        "tier1": int(counts.get("1", 0)),
        "tier2": int(counts.get("2", 0)),
        "tier3": int(counts.get("3", 0)),
        "unknown": int(counts.get("unknown", 0)),
        "grids_tested": result["grids_tested"],
        "fdr_sig": result["fdr_sig"],
        "median_lag": result["median_lag"],
    }]).to_csv(OUT_TIERS, index=False)
    return result


def append_doc(proxy: pd.DataFrame, tiers: dict) -> None:
    marker = "## Step 1 — dual-proxy record stratification"
    amendment = ROOT / "docs" / "p0_3_preregistration_amendment_1.md"
    void_notice = ""
    if amendment.exists():
        void_notice = (
            "> ⚠️ **VOID per `docs/p0_3_preregistration_amendment_1.md` "
            "(2026-11-14)**: `xy_count` is the number of records sharing the "
            "same (X,Y) coordinate, not a coordinate-precision proxy. The tier "
            "rule below and its results are withdrawn; step 2 is not decidable "
            "with the available fields. Values are kept only as an audit trail."
        )
    existing = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    base = (
        existing.split(marker)[0].rstrip() + "\n\n"
        if marker in existing
        else existing.rstrip() + "\n\n"
    )

    proxy_rows = [
        f"| {r.proxy} | {r.median_nonzero:.1f} | {r.n_high} | {r.n_low} | "
        f"{r.fdr_rate_high:.3f} | {r.fdr_rate_low:.3f} | {r.gap_pp:+.1f} | "
        f"{'yes' if r.meets_10pp else 'no'} |"
        for r in proxy.itertuples(index=False)
    ]
    both = bool(proxy["meets_10pp"].all())
    a_row = proxy[proxy["proxy"].str.startswith("A")].iloc[0]
    b_row = proxy[proxy["proxy"].str.startswith("B")].iloc[0]
    asym = (
        f"Asymmetry worth recording: proxy A gap = {a_row.gap_pp:+.1f} pp "
        f"(below the bar), proxy B gap = {b_row.gap_pp:+.1f} pp (above it). "
        "The exogenous proxy does indicate a higher FDR-discovery rate in "
        "administratively dense grids, while the endogenous proxy does not "
        "amplify the gap. Under the frozen two-proxy rule the joint condition "
        "is not met, so no record-bias attribution is claimed; this asymmetry "
        "is a prompt for a dedicated study, not evidence."
    )
    c = tiers["tier_counts"]
    share = tiers["tier3_share"] * 100

    lines = [
        marker,
        "",
        "Pre-registered: split each proxy at the median of **non-zero** grids; "
        "outcome is the mean of `gc_z_to_j_fdr_sig` in the real v0.3 Granger "
        "table. A record-bias explanation is supported only if **both** "
        f"proxies show a gap ≥ {PROXY_GAP_PP:.0f} pp.",
        "",
        "| Proxy | median (non-zero) | n high | n low | FDR rate high | FDR rate low | gap (pp) | ≥10pp |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
        *proxy_rows,
        "",
        f"**Dual-proxy verdict: {'SUPPORTED' if both else 'NOT SUPPORTED'}** "
        f"({'both proxies clear 10 pp' if both else 'at least one proxy fails the 10 pp bar'}). "
        "Proxy A is endogenous with the famine series, so a gap there alone is "
        "an upper bound on record bias, not a causal estimate.",
        "",
        asym,
        "",
        "## Step 2 — coordinate-confidence tier drop",
        "",
        void_notice,
        "",
        f"Pre-registered tiers on `xy_count`: tier 1 = 1, tier 2 = 2–{TIER3_THRESHOLD}, "
        f"tier 3 = > {TIER3_THRESHOLD} (dropped). `xy_count` is a geographic "
        "ambiguity proxy, **not** a 县/府/省 label in the source.",
        "",
        "| Quantity | Value |",
        "|---|---:|",
        f"| elite extension rows before | {tiers['elite_rows_before']:,} |",
        f"| tier 1 (`xy_count`=1) | {int(c.get('1', 0)):,} |",
        f"| tier 2 (2–10) | {int(c.get('2', 0)):,} |",
        f"| tier 3 (>10, dropped) | {int(c.get('3', 0)):,} ({share:.1f}%) |",
        f"| unknown (NaN, kept) | {int(c.get('unknown', 0)):,} |",
        f"| elite rows kept | {tiers['elite_rows_kept']:,} |",
        f"| grids tested after drop | {tiers['grids_tested']} |",
        f"| FDR-significant after drop | {tiers['fdr_sig']} (baseline {BASE_FDR}) |",
        f"| median FDR lag after drop | {tiers['median_lag']:.1f} yr (baseline {BASE_LAG}) |",
        "",
        "Limitation: `ming_general.csv` (the 6,935-row base series) has no "
        "`xy_count` column, so the tier drop applies only to the elite "
        "extension; NaN `xy_count` rows were kept. This is a partial "
        "coordinate-precision check, not a full re-geocoding.",
        "",
        f"⚠️ **Validity caveat (recorded, not post-hoc tuned)**: tier 3 covers "
        f"{share:.1f}% of the elite extension, so the drop shrinks the series "
        f"from {tiers['elite_rows_before']:,} to {tiers['elite_rows_kept']:,} rows. "
        "The change in FDR-significant grids and median lag is therefore "
        "**confounded with a large sample-size reduction** and cannot be "
        "attributed to coordinate precision. The semantics of `xy_count` (it "
        "may count records sharing a coordinate, not geographic ambiguity) "
        "must be verified before step 2 is interpretable. Per pre-registration "
        "§7 the threshold is NOT changed here; this is logged as a design "
        "defect requiring a dated amendment.",
        "",
        "## Combined conclusion",
        "",
        "- **Time perturbation**: see the table and figure above; the "
        "discovery-count and lag conclusions survive ±1 yr and most larger "
        "shifts, but the pre-registered lag tolerance is breached at k=+5.",
        f"- **Record bias**: dual-proxy condition "
        f"{'is' if both else 'is not'} met; the 48/135 finding "
        f"{'cannot be' if both else 'is not shown to be'} attributed to record "
        "intensity on this evidence.",
        "- **Coordinate precision**: dropping the pre-registered tier-3 elite "
        f"rows changes FDR-significant grids from {BASE_FDR} to "
        f"{tiers['fdr_sig']} and the median lag from {BASE_LAG} to "
        f"{tiers['median_lag']:.1f} yr, but ~{share:.0f}% of the extension is "
        "removed, so this is **not interpretable** as a coordinate-precision "
        "effect (see the validity caveat above).",
        "",
        "## Under which perturbation the conclusion fails",
        "",
        "The median-lag conclusion fails the pre-registered tolerance at "
        "k=+5 (12.0 yr vs 6.5 yr baseline, a 5.5 yr deviation). The discovery "
        "count stays within [24, 72] for every |k|=1 run, so 48/135 itself "
        "survives conservative year error; it is the **lag claim** that is "
        "least robust. Step 2 is not interpretable until `xy_count` semantics "
        "are verified.",
        "",
        f"Appended by `python scripts/p0_3_proxies_and_tiers.py` "
        f"({datetime.now().strftime('%Y-%m-%d %H:%M')}). "
        "Machine-readable: `data/derived/p0_3_proxy_stratification.csv`, "
        "`data/derived/p0_3_coordinate_tiers.csv`.",
        "",
    ]
    DOC.write_text(base + "\n".join(lines), encoding="utf-8")


def main() -> None:
    proxy = step1()
    print("step1 (dual proxy):")
    print(proxy.to_string(index=False))
    tiers = step2()
    print("step2 (coordinate tiers):", tiers)
    append_doc(proxy, tiers)
    print(f"appended sections to {DOC}")


if __name__ == "__main__":
    main()
