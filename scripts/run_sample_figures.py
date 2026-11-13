"""Run the three figure scripts against the synthetic sample data.

The real figures in `figures/` use the private Work_ming tables. This runner
sets the sample paths and writes a separate gallery to `figures/sample/`, so
anyone can verify that the code and layout work without the raw data.

Usage:
    python scripts/run_sample_figures.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"
OUT = ROOT / "figures" / "sample"

REQUIRED = [
    "clustered_levels.xlsx",
    "clustered_jinshi.xlsx",
    "gwr_coefficients.xlsx",
    "grid_granger_causality.xlsx",
    "grid_data_enriched.csv",
    "multiscale_causal_short_term.xlsx",
    "multiscale_causal_medium_term.xlsx",
    "multiscale_causal_long_term.xlsx",
    "geodetector_results.xlsx",
    "basemap_china.geojson",
]


def main() -> int:
    missing = [name for name in REQUIRED if not (SAMPLE / name).exists()]
    if missing:
        print("Missing sample files:", ", ".join(missing))
        print("Run: python scripts/make_sample_data.py")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "MING_OUTPUT": str(SAMPLE),
            "MING_BASEMAP": str(SAMPLE / "basemap_china.geojson"),
            "MING_FIG_DIR": str(OUT),
            "MING_SAMPLE": "1",
        }
    )
    for script in ("fig1_patterns.py", "fig2_mechanism.py", "fig3_framework.py"):
        print(f"== {script}")
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=ROOT,
            env=env,
            check=True,
        )
    print(f"sample figures written to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

