"""Verify what `xy_count` actually means in the CBDB export.

Background: p0_3_preregistration.md §3 assumed `xy_count` was a geographic
ambiguity proxy and used it as a coordinate-confidence tier. This script checks
that assumption against the real table and writes a machine-readable verdict.

Usage::

    python scripts/p0_3_verify_xy_count.py

Output::

    data/derived/p0_3_xy_count_semantics.csv

Reads the private raw CBDB export; outputs are aggregate only.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("MING_JINSHI_RAW", r"data/private/明进士.xlsx"))
OUT = ROOT / "data" / "derived" / "p0_3_xy_count_semantics.csv"


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"missing raw CBDB export: {RAW}")
    d = pd.read_excel(RAW)
    xy = pd.to_numeric(d["xy_count"], errors="coerce")

    coord_n = d.groupby(["X", "Y"])["xy_count"].transform("size").astype(float)
    addr_n = d.groupby("AddrChn")["xy_count"].transform("size").astype(float)
    valid = xy.notna()  # 1,898 rows have no xy_count; exclude pairwise
    corr_xy = float(np.corrcoef(xy[valid], coord_n[valid])[0, 1])
    corr_addr = float(np.corrcoef(xy[valid], addr_n[valid])[0, 1])

    # The 2,841-row elite extension used by P0-3 step 2 (same loader as the
    # analysis), so the full-table and subset statistics stay distinguishable.
    sys.path.insert(0, str(ROOT / "scripts"))
    import corrected_robustness as cr  # noqa: E402

    cr.RAW = RAW
    _, elite, _ = cr.load_jinshi()
    elite_xy = pd.to_numeric(elite["xy_count"], errors="coerce")

    rows = [
        {"check": "rows_total", "value": len(d)},
        {"check": "xy_count_non_null", "value": int(xy.notna().sum())},
        {"check": "xy_count_min", "value": float(xy.min())},
        {"check": "xy_count_median", "value": float(xy.median())},
        {"check": "xy_count_max", "value": float(xy.max())},
        {"check": "corr_xycount_vs_records_sharing_same_XY", "value": corr_xy},
        {"check": "corr_xycount_vs_records_sharing_same_AddrChn", "value": corr_addr},
        {"check": "share_xycount_eq_1", "value": float((xy == 1).mean())},
        {"check": "share_xycount_gt_10_full", "value": float((xy > 10).mean())},
        {"check": "elite_extension_rows", "value": int(len(elite_xy))},
        {"check": "share_xycount_gt_10_elite", "value": float((elite_xy > 10).mean())},
        {"check": "unique_XY", "value": int(d[["X", "Y"]].drop_duplicates().shape[0])},
        {"check": "unique_AddrChn", "value": int(d["AddrChn"].nunique())},
    ]

    suffix = (
        d["AddrChn"].astype(str)
        .str.extract(r"(縣|县|府|州|省|衛|卫|路|道|軍|军)$")[0]
        .fillna("(none)")
    )
    for label, count in suffix.value_counts().items():
        rows.append({"check": f"addr_suffix_{label}", "value": int(count)})

    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(df.to_string(index=False))
    print(
        "\nVERDICT:",
        "xy_count IS the number of records sharing the same (X,Y) coordinate "
        "(corr=1.0), NOT geographic ambiguity / coordinate precision."
        if abs(corr_xy - 1.0) < 1e-9
        else "inconclusive: inspect the table",
    )
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
