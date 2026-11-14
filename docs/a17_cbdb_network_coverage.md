# A17 — CBDB full-graph network coverage audit (2026-11-14)

- Generated: 2026-11-14 18:08
- Command: `python scripts/a17_cbdb_network_coverage.py`
- Repeats A14's audit on the **full CBDB relationship tables**, using the **same pre-declared 30% gate** (no threshold change).
- A14 (three query workbooks): 15.4% -> NO-GO.

| Source | unique person IDs | Jinshi overlap | coverage |
|---|---:|---:|---:|
| `KIN_DATA` | 288,981 | 15,089 | 54.4% |
| `ASSOC_DATA` | 44,834 | 4,585 | 16.6% |
| `ENTRY_DATA` | 221,605 | 27,501 | 99.2% |
| `KIN_UNION_ASSOC` | 313,115 | 15,616 | 56.4% |
| `ALL_THREE` | 483,629 | 27,501 | 99.2% |

## Verdict: **GO**

KIN ∪ ASSOC coverage = **56.4%** vs the 30% gate.

The three query workbooks were a **biased / incomplete export**; the full CBDB graph clears the gate. P1-7's prerequisite is now met, so an ego-network study may be defined — but only via a new dated pre-registration (`docs/a18_ego_network_preregistration.md`). This audit itself builds no network and makes no inferential claim.

Important nuance: coverage is measured against **all 27,711 PersonIDs in the Jinshi export** (including 武舉 and rows without a parsed rank). It is a conservative denominator, not a claim that every covered person has a rich ego-network.

## Limits

- `ENTRY_DATA` coverage (99.2%) is **not** a social-network measure: it records exam entries, so it is reported separately and excluded from the primary KIN ∪ ASSOC verdict.
- `KIN_DATA` includes kinship edges of all CBDB persons, not only Ming Jinshi; overlap is restricted to our PersonID set.
- Degree/edge quality (duplicate, auto-generated kinship) is not audited here; that belongs to the pre-registered ego-network study.
- CBDB build 2026-11-07 vs the older 入仕查询结果 export leaves a small unmatched share (documented in `docs/data_boundary_audit.md`).

## When this would fail

- CBDB replaced without re-running this audit.
- The gate changed after seeing the number (it is fixed above).
- Coverage quoted as evidence about elite reproduction rather than as a data-availability check.

Machine-readable: `data/derived/a17_cbdb_network_coverage.csv`.

Private inputs; aggregate outputs only.
