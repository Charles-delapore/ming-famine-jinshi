"""A17: re-audit P1-7 network coverage with the FULL CBDB relationship tables.

A14 used three query-result workbooks and found 15.4% coverage -> NO-GO.
These are exports, not the full graph. This script repeats the SAME audit
(same pre-declared 30% gate) on CBDB KIN_DATA / ASSOC_DATA / ENTRY_DATA.

Usage::

    python scripts/a17_cbdb_network_coverage.py

Outputs::

    data/derived/a17_cbdb_network_coverage.csv
    docs/a17_cbdb_network_coverage.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CBDB = Path(r"data/private/cbdb_20261107.sqlite3")
RAW = Path(r"data/private/明进士.xlsx")
OUT = ROOT / "data" / "derived" / "a17_cbdb_network_coverage.csv"
DOC = ROOT / "docs" / "a17_cbdb_network_coverage.md"

# SAME gate declared in A14, reused unchanged (no post-hoc tuning).
COVERAGE_GO = 0.30
A14_COVERAGE = 0.1543


def main() -> None:
    if not CBDB.exists() or not RAW.exists():
        raise SystemExit("missing input")
    raw = pd.read_excel(RAW, usecols=["PersonID"])
    jinshi = set(pd.to_numeric(raw.PersonID, errors="coerce").dropna().astype(int))
    con = sqlite3.connect(str(CBDB))

    tables = {}
    for t in ("KIN_DATA", "ASSOC_DATA", "ENTRY_DATA"):
        d = pd.read_sql_query(f"select c_personid from {t}", con)
        ids = set(pd.to_numeric(d.c_personid, errors="coerce").dropna().astype(int))
        tables[t] = ids
    kin_assoc = tables["KIN_DATA"] | tables["ASSOC_DATA"]
    tables["KIN_UNION_ASSOC"] = kin_assoc
    tables["ALL_THREE"] = kin_assoc | tables["ENTRY_DATA"]
    con.close()

    rows = []
    for name, ids in tables.items():
        ov = ids & jinshi
        rows.append({
            "source": name,
            "unique_person_ids": len(ids),
            "jinshi_overlap": len(ov),
            "coverage": round(len(ov) / len(jinshi), 4),
        })
    main_cov = next(r["coverage"] for r in rows if r["source"] == "KIN_UNION_ASSOC")
    go = main_cov >= COVERAGE_GO

    pd.DataFrame(rows).to_csv(OUT, index=False)
    lines = [
        "# A17 — CBDB full-graph network coverage audit (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a17_cbdb_network_coverage.py`",
        "- Repeats A14's audit on the **full CBDB relationship tables**, using "
        "the **same pre-declared 30% gate** (no threshold change).",
        f"- A14 (three query workbooks): {A14_COVERAGE*100:.1f}% -> NO-GO.",
        "",
        "| Source | unique person IDs | Jinshi overlap | coverage |",
        "|---|---:|---:|---:|",
        *[f"| `{r['source']}` | {r['unique_person_ids']:,} | "
          f"{r['jinshi_overlap']:,} | {r['coverage']*100:.1f}% |" for r in rows],
        "",
        f"## Verdict: **{'GO' if go else 'NO-GO'}**",
        "",
        f"KIN ∪ ASSOC coverage = **{main_cov*100:.1f}%** vs the "
        f"{COVERAGE_GO*100:.0f}% gate.",
        "",
    ]
    if go:
        lines += [
            "The three query workbooks were a **biased / incomplete export**; "
            "the full CBDB graph clears the gate. P1-7's prerequisite is now "
            "met, so an ego-network study may be defined — but only via a new "
            "dated pre-registration (`docs/a18_ego_network_preregistration.md`). "
            "This audit itself builds no network and makes no inferential claim.",
            "",
            "Important nuance: coverage is measured against **all 27,711 "
            "PersonIDs in the Jinshi export** (including 武舉 and rows without "
            "a parsed rank). It is a conservative denominator, not a claim "
            "that every covered person has a rich ego-network.",
        ]
    else:
        lines += [
            "Still below the gate; P1-7 remains NO-GO and the method-note-only "
            "rule stands.",
        ]
    lines += [
        "",
        "## Limits",
        "",
        "- `ENTRY_DATA` coverage (99.2%) is **not** a social-network measure: "
        "it records exam entries, so it is reported separately and excluded "
        "from the primary KIN ∪ ASSOC verdict.",
        "- `KIN_DATA` includes kinship edges of all CBDB persons, not only "
        "Ming Jinshi; overlap is restricted to our PersonID set.",
        "- Degree/edge quality (duplicate, auto-generated kinship) is not "
        "audited here; that belongs to the pre-registered ego-network study.",
        "- CBDB build 2026-11-07 vs the older 入仕查询结果 export leaves a "
        "small unmatched share (documented in `docs/data_boundary_audit.md`).",
        "",
        "## When this would fail",
        "",
        "- CBDB replaced without re-running this audit.",
        "- The gate changed after seeing the number (it is fixed above).",
        "- Coverage quoted as evidence about elite reproduction rather than "
        "as a data-availability check.",
        "",
        "Machine-readable: `data/derived/a17_cbdb_network_coverage.csv`.",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(pd.DataFrame(rows).to_string(index=False))
    print("GO" if go else "NO-GO", f"{main_cov*100:.1f}%")
    print(f"wrote {OUT}, {DOC}")


if __name__ == "__main__":
    main()
