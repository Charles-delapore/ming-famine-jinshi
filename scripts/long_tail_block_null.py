"""Block-permutation null for the Ming Granger result (local).

Circular block shuffle of the Jinshi series within each grid (block length 10),
preserving local autocorrelation while breaking the famine-Jinshi alignment.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r".")
sys.path.insert(0, str(ROOT))
from src.analysis.grid_analysis import GridGrangerCausality, fdr_correction  # noqa: E402

PANEL = ROOT / "output" / "v03" / "panel_v03.csv.gz"
OUT = ROOT / "data" / "derived" / "long_tail_block_null.csv"
REPS = 30
SEED = 20261115
BLOCK = 10


def block_shuffle(values: np.ndarray, rng: np.random.Generator, block: int) -> np.ndarray:
    n = len(values)
    n_blocks = int(np.ceil(n / block))
    blocks = [values[i * block:(i + 1) * block] for i in range(n_blocks)]
    order = rng.permutation(n_blocks)
    return np.concatenate([blocks[i] for i in order])[:n]


def main() -> None:
    panel = pd.read_csv(PANEL)
    groups = panel.groupby(["grid_x", "grid_y"], sort=False)
    analyzer = GridGrangerCausality(max_lag=20, significance=0.05, min_obs=30)
    rows = []
    for rep in range(REPS):
        rng = np.random.default_rng(SEED + rep)
        p = panel.copy()
        p["jinshi_count"] = groups["jinshi_count"].transform(
            lambda s: block_shuffle(s.values.astype(float), rng, BLOCK)
        )
        r = analyzer.analyze_grid_causality(p)
        sig, _ = fdr_correction(r["gc_z_to_j_pval"].values, alpha=0.05)
        lags = r.loc[sig, "gc_z_to_j_lag"]
        rows.append({
            "rep": rep,
            "fdr_sig": int(sig.sum()),
            "short_share": float((lags <= 5).mean()) if len(lags) else np.nan,
            "long15_share": float((lags >= 15).mean()) if len(lags) else np.nan,
        })
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print(rep, rows[-1], flush=True)


if __name__ == "__main__":
    main()
