"""A4: fixed-window / corrected main figure (replaces the 48/135 headline).

Draws the discovery counts from the real, pre-specified designs. The
max_lag=20 count is shown separately as a search diagnostic, not as a result.
Exports PNG (600 dpi), PDF and SVG.

Usage::

    python scripts/fig2_fixed_window.py

Reads data/derived/a3_main_results.csv.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "derived" / "a3_main_results.csv"
FIG = ROOT / "figures" / "fig2_fixed_window"


def main() -> None:
    if not SRC.exists():
        raise SystemExit("run scripts/a3_assemble_main_results.py first")
    df = pd.read_csv(SRC).set_index("metric")["value"]

    items = [
        ("Fixed 1–5 yr\njoint F test", "fixed_1_5_joint_FDR_grids", "main"),
        ("max_lag = 5\n(pre-specified)", "max_lag_5_FDR", "main"),
        ("Multiscale\n1–5 yr", "multiscale_1-5_FDR_grids", "main"),
        ("Multiscale\n5–10 yr", "multiscale_5-10_FDR_grids", "main"),
        ("Multiscale\n11–20 yr", "multiscale_11-20_FDR_grids", "main"),
        ("Within-grid\nBonferroni (20 lags)", "within_grid_Bonferroni_20", "diag"),
        ("max_lag = 20\n(search diagnostic)", "max_lag_20_FDR", "diag"),
    ]
    labels = [x[0] for x in items]
    values = [int(df[x[1]]) for x in items]
    colours = ["#0072B2" if x[2] == "main" else "#9E9E9E" for x in items]

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    bars = ax.bar(range(len(items)), values, color=colours, width=0.62)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.8, str(v),
                ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(range(len(items)))
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("FDR-significant grids (of 135)", fontsize=8)
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_title("Short-window famine→Jinshi discovery: fixed designs vs lag search",
                 fontsize=9.5, loc="left")
    ax.grid(alpha=0.25, lw=0.5, axis="y")
    ax.tick_params(labelsize=7)
    ax.text(0.99, 0.95,
            "Blue = pre-specified short-window designs\nGrey = lag-search diagnostics (not headlines)",
            transform=ax.transAxes, ha="right", va="top", fontsize=6.8,
            color="#444444")
    fig.tight_layout()
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(f"{FIG}.png", dpi=600)
    fig.savefig(f"{FIG}.pdf")
    fig.savefig(f"{FIG}.svg")
    plt.close(fig)
    print(f"wrote {FIG}.{{png,pdf,svg}}")
    print(dict(zip(labels, values)))


if __name__ == "__main__":
    main()
