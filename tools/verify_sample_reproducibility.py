"""P0-1 acceptance check: deterministic sample generation.

Runs ``scripts/make_sample_data.py`` twice in fresh processes and checks:

1. every one of the 14 sample tables is identical between the two runs,
   cell-by-cell (exact values) and in row order;
2. the generated output also matches the committed (HEAD) versions of those
   tables in values and row order, so re-running the generator is a no-op for
   the repository's published sample data.

Usage::

    python tools/verify_sample_reproducibility.py

Output::

    docs/p0_1_sample_reproducibility.md   -- acceptance tables

The script reads and writes files under this repository and reads git objects
from the local repository; it does not contact a remote.
"""

from __future__ import annotations

import hashlib
import io
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "scripts" / "make_sample_data.py"
SAMPLE = ROOT / "data" / "sample"
OUT = ROOT / "docs" / "p0_1_sample_reproducibility.md"

# The 14 tables produced by make_sample_data.py (13 xlsx + 1 csv).
# basemap_china.geojson and README.md are not tables and are excluded.
TABLES = [
    "clustered_levels.xlsx",
    "clustered_jinshi.xlsx",
    "gwr_coefficients.xlsx",
    "grid_granger_causality.xlsx",
    "grid_data_enriched.csv",
    "multiscale_causal_short_term.xlsx",
    "multiscale_causal_medium_term.xlsx",
    "multiscale_causal_long_term.xlsx",
    "geodetector_results.xlsx",
    "lagged_similarity_results.xlsx",
    "stl_decomposition_results.xlsx",
    "paleoclimate_partial_correlation.xlsx",
    "ccm_summary.xlsx",
    "cluster_characteristics_enhanced.xlsx",
]


def run_generator() -> str:
    """Run the generator once in a fresh interpreter; return its stdout."""
    proc = subprocess.run(
        [sys.executable, str(GEN)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def read_table(source, name: str) -> pd.DataFrame:
    if name.endswith(".csv"):
        return pd.read_csv(source)
    return pd.read_excel(source)


def snapshot() -> dict[str, tuple[pd.DataFrame, str]]:
    """Read every table into memory together with a short byte digest."""
    out: dict[str, tuple[pd.DataFrame, str]] = {}
    for name in TABLES:
        path = SAMPLE / name
        if not path.exists():
            raise FileNotFoundError(f"missing sample table: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        out[name] = (read_table(path, name), digest)
    return out


def head_snapshot() -> dict[str, pd.DataFrame] | None:
    """Read the committed (HEAD) version of each table from local git objects."""
    probe = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True
    )
    if probe.returncode != 0:
        return None
    out: dict[str, pd.DataFrame] = {}
    for name in TABLES:
        proc = subprocess.run(
            ["git", "show", f"HEAD:data/sample/{name}"],
            cwd=ROOT,
            capture_output=True,
        )
        if proc.returncode != 0:
            return None
        out[name] = read_table(io.BytesIO(proc.stdout), name)
    return out


def compare(
    first: tuple[pd.DataFrame, str], second: tuple[pd.DataFrame, str]
) -> tuple[bool, bool, bool, str]:
    """Return (values_equal, order_equal, bytes_equal, failure_detail)."""
    da, ha = first
    db, hb = second
    bytes_equal = ha == hb
    try:
        # check_exact: strict cell-by-cell equality, no float tolerance.
        # check_like=False (default): column order AND row order must match.
        pd.testing.assert_frame_equal(da, db, check_exact=True, check_like=False)
        return True, True, bytes_equal, ""
    except AssertionError as exc:
        detail = str(exc).splitlines()[0][:160] if str(exc) else "frames differ"
        return False, False, bytes_equal, detail


def frame_equal(a: pd.DataFrame, b: pd.DataFrame) -> tuple[bool, str]:
    try:
        pd.testing.assert_frame_equal(a, b, check_exact=True, check_like=False)
        return True, ""
    except AssertionError as exc:
        return False, (str(exc).splitlines()[0][:160] if str(exc) else "differ")


def main() -> int:
    log1 = run_generator()
    first = snapshot()
    log2 = run_generator()
    second = snapshot()
    head = head_snapshot()

    rows: list[str] = []
    head_rows: list[str] = []
    notes: list[str] = []
    n_pass = 0
    n_bytes = 0
    n_head = 0

    for name in TABLES:
        da = first[name][0]
        veq, oeq, beq, detail = compare(first[name], second[name])
        ok = veq and oeq
        n_pass += int(ok)
        n_bytes += int(beq)
        rows.append(
            f"| `{name}` | {len(da)} | {len(da.columns)} | "
            f"{'PASS' if veq else 'FAIL'} | {'PASS' if oeq else 'FAIL'} | "
            f"{'yes' if beq else 'no'} | {'PASS' if ok else 'FAIL'} |"
        )
        if detail:
            notes.append(f"- run1 vs run2, `{name}`: {detail}")

        if head is None:
            head_rows.append(f"| `{name}` | n/a (no git HEAD) |")
        else:
            heq, hdetail = frame_equal(second[name][0], head[name])
            n_head += int(heq)
            head_rows.append(f"| `{name}` | {'PASS' if heq else 'FAIL'} |")
            if hdetail:
                notes.append(f"- generated vs HEAD, `{name}`: {hdetail}")

    overall = "PASS" if n_pass == len(TABLES) else "FAIL"
    head_verdict = (
        "n/a" if head is None else ("PASS" if n_head == len(TABLES) else "FAIL")
    )

    lines = [
        "# P0-1 acceptance — sample generator reproducibility",
        "",
        f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- Command: `python tools/verify_sample_reproducibility.py`",
        "- Generator: `scripts/make_sample_data.py` (seed `20261113`), "
        "run twice in fresh interpreters.",
        "- Comparison: `pandas.testing.assert_frame_equal(..., "
        "check_exact=True, check_like=False)` — strict cell values, column "
        "order and row order.",
        "",
        f"**Run-to-run: {overall} ({n_pass}/{len(TABLES)} tables identical in "
        f"value and row order; {n_bytes}/{len(TABLES)} byte-identical).**",
        f"**Generated vs committed HEAD: {head_verdict} "
        f"({n_head}/{len(TABLES)} tables).**",
        "",
        "## 1. Two consecutive runs",
        "",
        "| Table | Rows | Cols | Values identical | Row order identical | "
        "Bytes identical | Verdict |",
        "|---|---:|---:|---|---|---|---|",
        *rows,
        "",
        "## 2. Generated output vs committed sample data (HEAD)",
        "",
        "| Table | Values + row order match HEAD |",
        "|---|---|",
        *head_rows,
        "",
        "Generator stdout, run 1 / run 2:",
        "",
        "```text",
        f"run 1: {log1}",
        f"run 2: {log2}",
        "```",
        "",
    ]
    if notes:
        lines += ["## Differences", "", *notes, ""]
    lines += [
        "## When this result would fail",
        "",
        "- The RNG seed in `make_sample_data.py` changes, or numpy/pandas "
        "change their random or sort implementations.",
        "- The stable full-key mergesort in the event tables is replaced by a "
        "single-key/unstable sort: tied rows can then reorder across runs.",
        "- dtype inference on read (Excel/CSV) differs between environments.",
        "- The generator is edited to write extra tables without updating the "
        "14-table checklist above.",
        "- Section 2 fails after a legitimate data/schema change is committed; "
        "re-generate and review the diff before publishing.",
        "",
        "## Scope note",
        "",
        "These are synthetic sample tables (no real historical record). The "
        "byte-digest column is informational only: Excel container metadata "
        "(zip member timestamps) varies between writes even when all cell "
        "values and row orders are identical. Section 2 is the check that "
        "justifies restoring `data/sample/` to HEAD after the two runs.",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"run-to-run {overall} ({n_pass}/{len(TABLES)}), "
        f"vs HEAD {head_verdict} ({n_head}/{len(TABLES)}) -> {OUT}"
    )
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
