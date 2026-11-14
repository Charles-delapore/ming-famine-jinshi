"""Publish aggregate Jinshi counts from the private CBDB export.

No individual records leave this script: the outputs are year-level counts and
rank-class totals only. They give downstream users the corrected denominator
(2,853 elite records in 1521-1619) without redistributing CBDB rows.

Usage:
    set MING_JINSHI_RAW=I:\\L\\Work_ming\\raw\\明进士.xlsx
    python scripts/make_jinshi_aggregates.py
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("MING_JINSHI_RAW", ROOT / "raw" / "明进士.xlsx"))
OUT = Path(os.environ.get("MING_AGG_OUT", ROOT / "data" / "derived"))

RANK_RE = re.compile(r"^\s*(?:第)?\s*([一二三123])\s*甲")
NUM = {"一": 1, "二": 2, "三": 3, "1": 1, "2": 2, "3": 3}


def rank_class(value: object) -> int | None:
    if pd.isna(value):
        return None
    match = RANK_RE.match(str(value))
    return NUM[match.group(1)] if match else None


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"raw export not found: {RAW}")

    df = pd.read_excel(RAW)
    df["year"] = pd.to_numeric(df.get("EntryYear"), errors="coerce")
    df["rank_class"] = df.get("EntryRank").map(rank_class)
    df["arabic"] = df.get("EntryRank").astype(str).str.contains(r"第[123]甲", na=False)
    df["chinese"] = df.get("EntryRank").astype(str).str.contains(r"第[一二三]甲", na=False)

    win = df[df["year"].between(1521, 1619)].copy()
    win["has_xy"] = win[["X", "Y"]].notna().all(axis=1)

    by_year = (
        win.groupby("year")
        .agg(
            records=("year", "size"),
            rank_1=("rank_class", lambda s: int((s == 1).sum())),
            rank_2=("rank_class", lambda s: int((s == 2).sum())),
            rank_3=("rank_class", lambda s: int((s == 3).sum())),
            rank_unparsed=("rank_class", lambda s: int(s.isna().sum())),
            arabic_coded=("arabic", "sum"),
            chinese_coded=("chinese", "sum"),
            with_coordinates=("has_xy", "sum"),
        )
        .reset_index()
        .sort_values("year")
    )
    by_year["year"] = by_year["year"].astype(int)

    elite = win[win["rank_class"].isin([1, 2])]
    summary = pd.DataFrame(
        [
            {"metric": "raw_rows", "value": len(df)},
            {"metric": "unique_person_id", "value": df["PersonID"].nunique()},
            {"metric": "rows_1521_1619", "value": len(win)},
            {"metric": "unique_person_1521_1619", "value": win["PersonID"].nunique()},
            {"metric": "rank_1", "value": int((win["rank_class"] == 1).sum())},
            {"metric": "rank_2", "value": int((win["rank_class"] == 2).sum())},
            {"metric": "rank_3", "value": int((win["rank_class"] == 3).sum())},
            {"metric": "elite_1_2", "value": len(elite)},
            {"metric": "elite_with_coordinates", "value": int(elite[["X", "Y"]].notna().all(axis=1).sum())},
            {"metric": "elite_arabic_coded", "value": int(elite["arabic"].sum())},
            {"metric": "elite_chinese_coded", "value": int(elite["chinese"].sum())},
            {"metric": "published_911_rows", "value": 911},
        ]
    )

    OUT.mkdir(parents=True, exist_ok=True)
    by_year.to_csv(OUT / "jinshi_by_year_1521_1619.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "jinshi_rank_summary.csv", index=False, encoding="utf-8-sig")
    print(f"wrote {OUT / 'jinshi_by_year_1521_1619.csv'} ({len(by_year)} years)")
    print(f"wrote {OUT / 'jinshi_rank_summary.csv'} ({len(summary)} metrics)")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
