"""Normalise CBDB Jinshi rank strings.

CBDB writes the same rank with Arabic or Chinese numerals:

    第1甲第3名   /   第一甲第三名
    第2甲第26名  /   第二甲第二十六名

The literal filter ``第1甲|第2甲`` therefore keeps only the Arabic-coded
subset. Use :func:`rank_level` before any filtering or grouping.
"""

from __future__ import annotations

import re

import pandas as pd

RANK_RE = re.compile(r"^\s*(?:第)?\s*([一二三123])\s*甲")
_NUM = {"一": 1, "二": 2, "三": 3, "1": 1, "2": 2, "3": 3}


def rank_class(value: object) -> int | None:
    """Return 1/2/3 for a 1甲/2甲/3甲 string, otherwise None."""
    if pd.isna(value):
        return None
    match = RANK_RE.match(str(value))
    return _NUM[match.group(1)] if match else None


def rank_level(value: object) -> int | None:
    """Alias used by the clustering code (1甲=1, 2甲=2, 3甲=3)."""
    return rank_class(value)


def normalize_rank(data: pd.DataFrame, column: str = "EntryRank") -> pd.DataFrame:
    """Add ``rank_class`` and ``level`` columns without dropping rows."""
    out = data.copy()
    out["rank_class"] = out[column].map(rank_class)
    out["level"] = out["rank_class"]
    return out
