"""Figure for the long-tail memo."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LAG = ROOT / "data" / "derived" / "long_tail_lag_window.csv"
NULL = ROOT / "data" / "derived" / "long_tail_null_permutation.csv"
BLOCK = ROOT / "data" / "derived" / "long_tail_block_null.csv"
GRANGER = ROOT / "output" / "v03" / "granger_v03.xlsx"
OUT = ROOT / "figures" / "long_tail_diagnostics.png"
OUT_PDF = ROOT / "figures" / "long_tail_diagnostics.pdf"

BLUE, ORANGE, GREEN = "#0072B2", "#D55E00", "#009E73"


def main() -> None:
    lag = pd.read_csv(LAG)
    granger = pd.read_excel(GRANGER)
    sig = granger[granger["gc_z_to_j_fdr_sig"].astype(bool)]
    null = pd.read_csv(NULL) if NULL.exists() else pd.DataFrame()
    block = pd.read_csv(BLOCK) if BLOCK.exists() else pd.DataFrame()

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))

    ax = axes[0]
    ax.plot(lag.max_lag, lag.fdr_sig, "o-", color=BLUE, ms=4, lw=1.3, label="FDR grids")
    ax.plot(lag.max_lag, lag.fdr_sig_bonferroni, "s--", color=ORANGE, ms=4, lw=1.2,
            label="within-grid Bonferroni")
    ax.set_xlabel("max lag searched (years)")
    ax.set_ylabel("FDR-significant grids")
    ax.set_xticks(lag.max_lag)
    ax.legend(fontsize=6, frameon=False)
    ax.set_title("Discovery depends on the search window", fontsize=7.5, loc="left")

    ax = axes[1]
    bins = {"1–5": 0, "6–10": 0, "11–14": 0, "15–20": 0}
    for v in sig["gc_z_to_j_lag"]:
        if v <= 5:
            bins["1–5"] += 1
        elif v <= 10:
            bins["6–10"] += 1
        elif v <= 14:
            bins["11–14"] += 1
        else:
            bins["15–20"] += 1
    colors = [GREEN, GREEN, ORANGE, ORANGE]
    ax.bar(list(bins), list(bins.values()), color=colors, width=0.65)
    ax.set_ylabel("FDR grids")
    ax.set_title("Lag distribution is bimodal (n = 48)", fontsize=7.5, loc="left")
    ax.tick_params(axis="x", labelsize=7)

    ax = axes[2]
    if len(null):
        ax.hist(null.fdr_sig, bins=np.arange(-0.5, 31.5, 1), color=BLUE, alpha=0.55,
                label="iid permutation")
    if len(block):
        ax.hist(block.fdr_sig, bins=np.arange(-0.5, 31.5, 1), color=ORANGE, alpha=0.55,
                label="block permutation")
    ax.axvline(48, color="black", ls="--", lw=1.0, label="observed 48")
    ax.set_xlabel("FDR grids under the null")
    ax.set_ylabel("replicates")
    ax.legend(fontsize=5.5, frameon=False, loc="upper right")
    ax.set_title("Null distributions", fontsize=7.5, loc="left")

    for ax in axes:
        ax.grid(alpha=0.2, lw=0.4)
        ax.tick_params(labelsize=6.5)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT, dpi=300)
    fig.savefig(OUT_PDF)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
