"""Figure 4 — statistical companion to the maps (S6).

Maps show where; this figure shows the distributions behind the claims:
A  GWR coefficient distribution (direction and spread),
B  famine severity composition,
C  Jinshi records by exam year (the 1523/1526 concentration is visible).

No inferential claim is made from these descriptive distributions.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "style"))
import ming_style as ms  # noqa: E402
import figure_kit as fk  # noqa: E402

ms.apply_style()

z = pd.read_excel(ms.OUTPUT / "clustered_levels.xlsx")
j = pd.read_excel(ms.OUTPUT / "clustered_jinshi.xlsx")
gwr = pd.read_excel(ms.OUTPUT / "gwr_coefficients.xlsx")

z = z.dropna(subset=["level"])
j = j.dropna(subset=["EntryYear"])
coef = gwr["gwr_coef"].astype(float).values

fig = plt.figure(figsize=(7.2, 2.9))
gs = fig.add_gridspec(1, 3, wspace=0.32, left=0.07, right=0.98, top=0.83, bottom=0.17)

# A — GWR coefficient distribution
axA = fig.add_subplot(gs[0, 0])
axA.hist(coef, bins=24, color=ms.BLUE, alpha=0.75, edgecolor="white", linewidth=0.4)
axA.axvline(0, color="#333333", lw=0.8, ls="--")
axA.axvline(np.median(coef), color=ms.VERMILION, lw=1.0, label="median")
axA.set_xlabel("GWR coefficient (famine → Jinshi)", fontsize=7)
axA.set_ylabel("Grid cells", fontsize=7)
axA.set_title("Spatial effect sizes", loc="left", pad=4)
axA.legend(loc="upper left", fontsize=6)
fk.distribution_annotation(axA, coef)
ms.panel_label(axA, "A")

# B — famine severity composition
axB = fig.add_subplot(gs[0, 1])
sev = z["level"].value_counts().sort_index()
levels = [int(x) for x in sev.index]
norm = Normalize(vmin=1, vmax=5)
colors = [ms.FAMINE_CMAP(norm(v)) for v in levels]
bars = axB.bar(levels, sev.values, color=colors, edgecolor="white", linewidth=0.4)
for b, v in zip(bars, sev.values):
    axB.text(b.get_x() + b.get_width() / 2, v + max(sev.values) * 0.02, f"{int(v):,}",
             ha="center", va="bottom", fontsize=6, color="#333333")
axB.set_xticks([1, 2, 3, 4, 5])
axB.set_xlabel("Famine severity level", fontsize=7)
axB.set_ylabel("Events", fontsize=7)
axB.set_title("Famine composition", loc="left", pad=4)
axB.set_ylim(0, max(sev.values) * 1.15)
ms.panel_label(axB, "B")

# C — Jinshi records by exam year
axC = fig.add_subplot(gs[0, 2])
year_counts = j.groupby("EntryYear").size().sort_index()
corrected = len(j) > 1500
if corrected:
    colors = [ms.BLUE] * len(year_counts)
    axC.text(0.98, 0.95, f"n = {len(j):,}\nnormalized 1甲/2甲",
             transform=axC.transAxes, ha="right", va="top", fontsize=6,
             color="#555555")
    axC.set_title("Exam-year composition", loc="left", pad=4)
else:
    colors = [ms.VERMILION if y in (1523, 1526) else "#B9C4CC" for y in year_counts.index]
    share = (year_counts.get(1523, 0) + year_counts.get(1526, 0)) / len(j) * 100
    axC.text(0.98, 0.95, f"1523 + 1526 = {int(year_counts.get(1523, 0) + year_counts.get(1526, 0))}\n"
             f"({share:.1f}% of records)\nArabic-only rank filter",
             transform=axC.transAxes, ha="right", va="top", fontsize=6,
             color="#555555")
    axC.set_title("Exam-year composition (artefact)", loc="left", pad=4)
axC.bar(year_counts.index, year_counts.values, color=colors, width=0.85,
        edgecolor="none")
axC.set_xlabel("Exam year (CE)", fontsize=7)
axC.set_ylabel("Jinshi records", fontsize=7)
axC.set_xlim(1520, 1620)
axC.set_xticks(np.arange(1520, 1621, 20))
ms.panel_label(axC, "C")

if os.environ.get("MING_SAMPLE") == "1":
    note = "Synthetic sample data for code verification — not historical records."
else:
    n_j = len(j)
    layer = ("normalized 1甲/2甲 elite, v0.3" if corrected
             else "Arabic-coded 1甲/2甲 subset, v0.2")
    note = (f"Data: Work_ming v5 result tables. GWR n={len(gwr)}; famine n=5,736; "
            f"Jinshi n={n_j:,} ({layer}; see docs/jinshi_provenance.md). "
            "Descriptive distributions only.")
fk.footer(fig, note, y=0.01, fontsize=6)

paths = ms.save(fig, "fig4_distribution")
print("\n".join(str(p) for p in paths))
