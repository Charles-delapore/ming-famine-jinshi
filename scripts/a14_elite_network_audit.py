"""A14: coverage audit for the elite social-network data (P1-7 prerequisite).

Roadmap §2 P1-7 requires a CBDB relationship-coverage audit BEFORE building
ego-networks or an elite funnel. This script performs that audit on the three
previously unused 社会关系网络查询结果 workbooks (~40k edges with both-end
coordinates). It is exploratory/descriptive: no network model, no causal claim.

Usage::

    python scripts/a14_elite_network_audit.py

Outputs::

    data/derived/a14_network_coverage.csv
    data/derived/a14_network_edges.csv
    docs/a14_elite_network_audit.md

Private inputs; aggregate outputs only.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NET_DIR = Path("data/private/ming_general")
FILES = ["001社会关系网络查询结果.xlsx", "002社会关系网络查询结果.xlsx",
         "003社会关系网络查询结果.xlsx"]
RAW_JINSHI = Path(r"data/private/明进士.xlsx")
DERIVED = ROOT / "data" / "derived"
OUT_COV = DERIVED / "a14_network_coverage.csv"
OUT_EDGES = DERIVED / "a14_network_edges.csv"
DOC = ROOT / "docs" / "a14_elite_network_audit.md"

# P1-7 Go/No-Go threshold declared here BEFORE computing coverage.
COVERAGE_GO = 0.30


def main() -> None:
    for p in FILES:
        if not (NET_DIR / p).exists():
            raise SystemExit(f"missing network table: {p}")
    frames = []
    for name in FILES:
        d = pd.read_excel(NET_DIR / name)
        d["source_file"] = name
        frames.append(d)
    all_edges = pd.concat(frames, ignore_index=True)

    # Keep a compact, normalized edge table.
    cols = ["PersonID", "NodeID", "Kin/Non", "联系", "X", "Y", "Node X", "Node Y",
            "Edge Dist.", "source_file"]
    have = [c for c in cols if c in all_edges.columns]
    edges = all_edges[have].copy()
    for c in ("X", "Y", "Node X", "Node Y", "Edge Dist."):
        if c in edges.columns:
            edges[c] = pd.to_numeric(edges[c], errors="coerce")
    edges = edges.drop_duplicates(subset=[c for c in ("PersonID", "NodeID", "联系")
                                          if c in edges.columns])
    edges.to_csv(OUT_EDGES, index=False)

    persons = pd.to_numeric(edges.get("PersonID"), errors="coerce").dropna().astype(int)
    nodes = pd.to_numeric(edges.get("NodeID"), errors="coerce").dropna().astype(int)
    all_ids = set(persons) | set(nodes)

    raw = pd.read_excel(RAW_JINSHI, usecols=["PersonID"])
    jinshi_ids = set(pd.to_numeric(raw["PersonID"], errors="coerce")
                     .dropna().astype(int))
    overlap = all_ids & jinshi_ids
    coverage = len(overlap) / len(jinshi_ids) if jinshi_ids else 0.0

    kin = (edges["Kin/Non"].value_counts(dropna=False).to_dict()
           if "Kin/Non" in edges.columns else {})
    rel = (edges["联系"].value_counts().head(12).to_dict()
           if "联系" in edges.columns else {})
    dist = (edges["Edge Dist."].dropna() if "Edge Dist." in edges.columns
            else pd.Series(dtype=float))
    coords_ok = (edges[["X", "Y", "Node X", "Node Y"]].notna().all(axis=1)
                 if all(c in edges.columns for c in ("X", "Y", "Node X", "Node Y"))
                 else pd.Series(dtype=bool))

    rows = [
        {"metric": "edge_rows_raw", "value": len(all_edges)},
        {"metric": "edge_rows_deduplicated", "value": len(edges)},
        {"metric": "unique_person_ids", "value": len(set(persons))},
        {"metric": "unique_node_ids", "value": len(set(nodes))},
        {"metric": "unique_actors_total", "value": len(all_ids)},
        {"metric": "jinshi_ids_in_export", "value": len(jinshi_ids)},
        {"metric": "jinshi_ids_with_any_network_edge", "value": len(overlap)},
        {"metric": "jinshi_network_coverage", "value": round(coverage, 4)},
        {"metric": "edges_with_both_coordinates", "value": int(coords_ok.sum())},
        {"metric": "median_edge_distance",
         "value": round(float(dist.median()), 3) if len(dist) else np.nan},
        {"metric": "share_edges_within_1_degree",
         "value": round(float((dist < 1).mean()), 4) if len(dist) else np.nan},
        {"metric": "coverage_go_threshold", "value": COVERAGE_GO},
    ]
    cov = pd.DataFrame(rows)
    cov.to_csv(OUT_COV, index=False)

    go = coverage >= COVERAGE_GO
    lines = [
        "# A14 — elite social-network coverage audit (2026-11-14)",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python scripts/a14_elite_network_audit.py`",
        "- Scope: P1-7 **prerequisite** (CBDB relationship-coverage audit). "
        "Exploratory and descriptive only — no ego-network, no funnel model, "
        "no causal claim.",
        "- Source: three `ming_general/*社会关系网络查询结果.xlsx` workbooks, "
        "previously unused by the project.",
        "",
        "| Metric | Value |",
        "|---|---:|",
        *[f"| `{r['metric']}` | {r['value']} |" for r in rows],
        "",
        f"## Go / No-Go: **{'GO' if go else 'NO-GO'}**",
        "",
        f"Declared before computation: ≥{COVERAGE_GO*100:.0f}% of Jinshi "
        f"PersonIDs must appear in at least one network edge. Observed: "
        f"**{coverage*100:.1f}%**.",
        "",
    ]
    if go:
        lines += [
            "Coverage passes. A follow-up **new dated pre-registration** may "
            "define an ego-network / three-stage funnel (roadmap §2 P1-7). "
            "No such model is run in this audit.",
        ]
    else:
        lines += [
            "Coverage is below the declared threshold. Per roadmap §2 P1-7 the "
            "correct output is a **method note only**: do not build ego-networks "
            "or a funnel on a biased subset of elites. The relationship tables "
            "may still support descriptive network statistics (reported below), "
            "but not an inferential elite-reproduction model.",
        ]
    lines += [
        "",
        "## Descriptive network statistics (not inferential)",
        "",
        f"- Kin / Non distribution: `{kin}`",
        f"- Top relation types: `{rel}`",
        f"- Edge-distance median: {float(dist.median()):.3f} "
        f"(n = {len(dist):,})" if len(dist) else "- Edge distance: unavailable",
        "",
        "## Limits",
        "",
        "- The three workbooks are **query results**, not the full CBDB graph; "
        "CBDB `KIN_DATA` (565,276 rows) / `ASSOC_DATA` (190,164 rows) are larger "
        "but were not used here.",
        "- Duplicate edges were removed on (PersonID, NodeID, relation type); "
        "different relation types between the same pair are kept.",
        "- `Edge Dist.` units are **undocumented** in the source workbooks: "
        "the observed median is 1.0 and no value is below 1, so it is not "
        "interpreted as a geographic distance. It may be a categorical or "
        "binned code; the distance statistics above are reported as-is only.",
        "- Coverage is measured against the `明进士.xlsx` export (28,761 rows), "
        "which includes non-Jinshi/wuju rows; this is a conservative denominator.",
        "",
        "## When this would fail",
        "",
        "- Network workbooks replaced without re-running the audit.",
        "- The coverage threshold changed after seeing the number (declared above).",
        "- Descriptive statistics quoted as evidence about elite reproduction.",
        "",
        "## Outputs",
        "",
        "| Output | Path |",
        "|---|---|",
        "| coverage table | `data/derived/a14_network_coverage.csv` |",
        "| normalized edges | `<local private; not distributed>` |",
        "",
        "Private inputs; aggregate outputs only.",
        "",
    ]
    DOC.write_text("\n".join(lines), encoding="utf-8")
    print(cov.to_string(index=False))
    print("GO" if go else "NO-GO", f"coverage={coverage*100:.1f}%")
    print(f"wrote {OUT_COV}, {OUT_EDGES}, {DOC}")


if __name__ == "__main__":
    main()
