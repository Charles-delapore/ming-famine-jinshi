"""Figure 5 — what the rank-encoding fix changes (and what it does not).

A  Exam-year composition, old 911 layer vs corrected 2,841 elite.
B  Grid-level discovery: Granger FDR and GWR significance, v0.2 vs v0.3.
C  GWR coefficient agreement on common grids.
D  Lag distribution of FDR-significant Granger grids, v0.2 vs v0.3.

This is an audit figure, not a new causal claim.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "style"))
import ming_style as ms  # noqa: E402
import figure_kit as fk  # noqa: E402

ms.apply_style()

ROOT = Path(__file__).resolve().parents[1]
V03 = Path(os.environ.get("MING_V03_OUT", ROOT / "output" / "v03"))
OLD_OUTPUT = Path(os.environ.get("MING_OUTPUT_OLD", r"data/private/v02_output"))
NEW_INPUT = V03 / "fig_input"

old_j = pd.read_excel(OLD_OUTPUT / "clustered_jinshi.xlsx")
new_j = pd.read_excel(NEW_INPUT / "clustered_jinshi.xlsx")
g2 = pd.read_excel(V03 / "gwr_v02.xlsx")
g3 = pd.read_excel(V03 / "gwr_v03.xlsx")
gc2 = pd.read_excel(V03 / "granger_v02.xlsx")
gc3 = pd.read_excel(V03 / "granger_v03.xlsx")

fig = plt.figure(figsize=(7.2, 6.2))
gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.30, left=0.075, right=0.98,
                      top=0.93, bottom=0.12)

# A — exam-year composition
axA = fig.add_subplot(gs[0, 0])
old_counts = old_j.groupby("EntryYear").size().sort_index()
new_counts = new_j.groupby("EntryYear").size().sort_index()
years = sorted(set(old_counts.index) | set(new_counts.index))
axA.plot(years, [old_counts.get(y, 0) for y in years], color=ms.GREY,
         lw=1.0, marker="o", ms=1.8, label="v0.2 (911, Arabic only)")
axA.plot(years, [new_counts.get(y, 0) for y in years], color=ms.BLUE,
         lw=1.2, marker="o", ms=1.8, label="v0.3 (2,841 normalized)")
axA.axvspan(1522.5, 1526.5, color=ms.VERMILION, alpha=0.10, lw=0)
axA.annotate("1523/1526 spike\nis an encoding artefact", xy=(1524.5, 130),
             xytext=(1545, 128), fontsize=6.2, color=ms.VERMILION,
             arrowprops=dict(arrowstyle="->", color=ms.VERMILION, lw=0.7))
axA.set_xlim(1520, 1620)
axA.set_xlabel("Exam year (CE)", fontsize=7)
axA.set_ylabel("Jinshi records", fontsize=7)
axA.set_title("Exam-year composition", loc="left", pad=4)
axA.legend(loc="upper right", fontsize=6)
ms.panel_label(axA, "A", x=-0.16)

# B — discovery counts
axB = fig.add_subplot(gs[0, 1])
labels = ["Granger\nFDR", "GWR\n|t| > 1.96"]
v02 = [int(gc2["gc_z_to_j_fdr_sig"].sum()), int(g2["gwr_sig"].sum())]
v03 = [int(gc3["gc_z_to_j_fdr_sig"].sum()), int(g3["gwr_sig"].sum())]
denoms = [len(gc2), len(g2)]
x = np.arange(len(labels))
axB.bar(x - 0.18, v02, width=0.34, color=ms.GREY, label="v0.2")
axB.bar(x + 0.18, v03, width=0.34, color=ms.BLUE, label="v0.3")
for i, (a, b) in enumerate(zip(v02, v03)):
    axB.text(i - 0.18, a + 2, f"{a}", ha="center", va="bottom", fontsize=6.2, color="#444444")
    axB.text(i + 0.18, b + 2, f"{b}", ha="center", va="bottom", fontsize=6.2, color=ms.BLUE)
axB.set_xticks(x)
axB.set_xticklabels([f"{l}\n(of {d})" for l, d in zip(labels, denoms)], fontsize=6.5)
axB.set_ylabel("Significant grids", fontsize=7)
axB.set_ylim(0, max(v02 + v03) * 1.22)
axB.set_title("Grid-level discovery", loc="left", pad=4)
axB.legend(loc="upper right", fontsize=6)
ms.panel_label(axB, "B", x=-0.16)

# C — GWR coefficient agreement
axC = fig.add_subplot(gs[1, 0])
common = g2.merge(g3, on=["grid_x", "grid_y"], suffixes=("_v02", "_v03"))
r = common["gwr_coef_v02"].corr(common["gwr_coef_v03"])
axC.scatter(common["gwr_coef_v02"], common["gwr_coef_v03"], s=6,
            color=ms.BLUE, alpha=0.55, edgecolor="none")
lim = [min(common["gwr_coef_v02"].min(), common["gwr_coef_v03"].min()) - 0.05,
       max(common["gwr_coef_v02"].max(), common["gwr_coef_v03"].max()) + 0.05]
axC.plot(lim, lim, color="#777777", lw=0.7, ls="--")
axC.set_xlim(lim)
axC.set_ylim(lim)
axC.set_xlabel("GWR coefficient, v0.2", fontsize=7)
axC.set_ylabel("GWR coefficient, v0.3", fontsize=7)
axC.set_title("Spatial-effect agreement", loc="left", pad=4)
axC.text(0.04, 0.95, f"n = {len(common)} grids\nPearson r = {r:.4f}",
         transform=axC.transAxes, ha="left", va="top", fontsize=6.2, color="#444444")
ms.panel_label(axC, "C", x=-0.16)

# D — lag distribution
axD = fig.add_subplot(gs[1, 1])
lags2 = gc2.loc[gc2["gc_z_to_j_fdr_sig"], "gc_z_to_j_lag"].astype(int)
lags3 = gc3.loc[gc3["gc_z_to_j_fdr_sig"], "gc_z_to_j_lag"].astype(int)
bins = np.arange(0.5, 21.5, 1)
axD.hist([lags2, lags3], bins=bins, color=[ms.GREY, ms.BLUE],
         label=[f"v0.2 (median {lags2.median():.0f} yr)", f"v0.3 (median {lags3.median():.1f} yr)"], rwidth=0.8)
axD.axvline(lags2.median(), color=ms.GREY, lw=1.0, ls="--")
axD.axvline(lags3.median(), color=ms.BLUE, lw=1.0, ls="--")
axD.set_xlabel("Best lag (years)", fontsize=7)
axD.set_ylabel("FDR-significant grids", fontsize=7)
axD.set_title("Lag distribution", loc="left", pad=4)
axD.legend(loc="upper center", ncol=2, fontsize=6)
ms.panel_label(axD, "D", x=-0.16)

note = ("Data: CBDB Jinshi export; Work_ming v5 famine series. v0.2 = Arabic-coded "
        "1甲/2甲 extension (911); v0.3 = normalized 1甲/2甲 elite (2,841). "
        "Grid models use the broad Jinshi series; see docs/corrected_robustness.md.")
fk.footer(fig, note, y=0.01, fontsize=6)

paths = ms.save(fig, "fig5_correction")
print("\n".join(str(p) for p in paths))


