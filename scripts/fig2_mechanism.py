"""Figure 2 — grid-level evidence for the famine–Jinshi relationship.

Panels separate three different questions:
A  How well does the local model fit? (GWR local R²)
B  Where is the famine→Jinshi Granger signal FDR-significant?
C  How many grids survive FDR across methods and horizons?
D  How much variance do the candidate factors explain? (GeoDetector q)

No panel treats a p-value as an effect size; counts and q values are labelled.
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "style"))
import ming_style as ms  # noqa: E402

ms.apply_style()

gwr = pd.read_excel(ms.OUTPUT / "gwr_coefficients.xlsx")
gg = pd.read_excel(ms.OUTPUT / "grid_granger_causality.xlsx")
gd = pd.read_excel(ms.OUTPUT / "geodetector_results.xlsx")
prov = ms.load_provinces()

horizons = {
    "Short (1–5 yr)": len(
        pd.read_excel(ms.OUTPUT / "multiscale_causal_short_term.xlsx").query(
            "fdr_significant == True"
        )
    ),
    "Medium (6–10 yr)": len(
        pd.read_excel(ms.OUTPUT / "multiscale_causal_medium_term.xlsx").query(
            "fdr_significant == True"
        )
    ),
    "Long (11–20 yr)": len(
        pd.read_excel(ms.OUTPUT / "multiscale_causal_long_term.xlsx").query(
            "fdr_significant == True"
        )
    ),
}
granger_sig = int(gg["gc_z_to_j_fdr_sig"].sum())

gwr_pts = gpd.GeoSeries(
    gpd.points_from_xy(gwr["grid_x"], gwr["grid_y"]), crs=4326
).to_crs(3857)
gg_pts = gpd.GeoSeries(
    gpd.points_from_xy(gg["grid_x"], gg["grid_y"]), crs=4326
).to_crs(3857)

gx, gy = gwr_pts.x.values, gwr_pts.y.values
ggx, ggy = gg_pts.x.values, gg_pts.y.values

pad = 150_000
extent = (gx.min() - pad, gx.max() + pad, gy.min() - pad, gy.max() + pad)

fig = plt.figure(figsize=(7.2, 6.4))
gs = GridSpec(2, 2, figure=fig, height_ratios=[1.12, 0.88], hspace=0.28, wspace=0.22)

# --- A: local R² -----------------------------------------------------------
axA = fig.add_subplot(gs[0, 0])
ms.style_map(axA, prov, extent)
r2_norm = TwoSlopeNorm(vmin=-0.50, vcenter=0.0, vmax=0.85)
sc = axA.scatter(
    gx,
    gy,
    c=gwr["gwr_local_r2"],
    cmap=ms.DIVERGING,
    norm=r2_norm,
    s=26,
    marker="s",
    linewidths=0,
    rasterized=True,
    zorder=3,
)
cb = fig.colorbar(sc, ax=axA, fraction=0.045, pad=0.02, shrink=0.82)
cb.set_label("Local $R^2$", fontsize=7)
cb.ax.tick_params(labelsize=6)
cb.outline.set_linewidth(0.3)
axA.set_title("Local model fit (GWR)", loc="left", pad=4)
axA.text(
    0.01,
    0.96,
    f"n = {len(gwr)} grids; median $R^2$ = {gwr['gwr_local_r2'].median():.2f}",
    transform=axA.transAxes,
    fontsize=6.3,
    color="#555555",
    ha="left",
    va="top",
)
ms.panel_label(axA, "A")

# --- B: Granger FDR --------------------------------------------------------
axB = fig.add_subplot(gs[0, 1])
ms.style_map(axB, prov, extent)
sig = gg["gc_z_to_j_fdr_sig"].astype(bool).values
axB.scatter(
    ggx[~sig],
    ggy[~sig],
    s=20,
    marker="s",
    c="#D9D9D9",
    linewidths=0,
    alpha=0.75,
    rasterized=True,
    zorder=3,
)
axB.scatter(
    ggx[sig],
    ggy[sig],
    s=24,
    marker="s",
    c=ms.VERMILION,
    linewidths=0,
    alpha=0.95,
    rasterized=True,
    zorder=4,
)
axB.set_title("Famine → Jinshi Granger signal", loc="left", pad=4)
axB.text(
    0.01,
    0.96,
    f"{granger_sig}/{len(gg)} grids FDR-significant",
    transform=axB.transAxes,
    fontsize=6.3,
    color="#555555",
    ha="left",
    va="top",
)
handles = [
    Line2D([], [], marker="s", ls="", color=ms.VERMILION, label="FDR-significant"),
    Line2D([], [], marker="s", ls="", color="#D9D9D9", label="not significant"),
]
axB.legend(
    handles=handles,
    loc="lower right",
    fontsize=6,
    handletextpad=0.4,
    borderpad=0.2,
)
ms.panel_label(axB, "B")

# --- C: discovery counts ---------------------------------------------------
axC = fig.add_subplot(gs[1, 0])
labels = ["Granger\n(any lag)"] + list(horizons.keys())
values = [granger_sig] + list(horizons.values())
colors = [ms.VERMILION, ms.BLUE, ms.SKY, "#BDBDBD"]
bars = axC.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.62)
for b, v in zip(bars, values[::-1]):
    axC.text(
        v + 1.0,
        b.get_y() + b.get_height() / 2,
        str(v),
        va="center",
        fontsize=7,
        color="#333333",
    )
axC.set_xlim(0, max(values) * 1.25)
axC.set_xlabel("FDR-significant grids (count)", fontsize=7)
axC.set_title("Signal discovery across horizons", loc="left", pad=4)
axC.grid(axis="y", visible=False)
axC.text(
    0.99,
    0.04,
    "denominator = 135 grids",
    transform=axC.transAxes,
    ha="right",
    va="bottom",
    fontsize=6.3,
    color="#666666",
)
ms.panel_label(axC, "C")

# --- D: GeoDetector q ------------------------------------------------------
axD = fig.add_subplot(gs[1, 1])
q_labels = ["Famine severity", "Longitude", "Latitude"]
q_vals = [
    float(gd.loc[0, "q_zaihuang_severity"]),
    float(gd.loc[0, "q_longitude"]),
    float(gd.loc[0, "q_latitude"]),
]
order = np.argsort(q_vals)
bars = axD.barh(
    [q_labels[i] for i in order],
    [q_vals[i] for i in order],
    color=[ms.ORANGE, ms.SKY, ms.BLUE],
    height=0.55,
)
for b, i in zip(bars, order):
    axD.text(
        q_vals[i] + 0.008,
        b.get_y() + b.get_height() / 2,
        f"{q_vals[i]:.3f}",
        va="center",
        fontsize=7,
        color="#333333",
    )
axD.set_xlim(0, 0.42)
axD.set_xlabel("GeoDetector q (variance explained)", fontsize=7)
axD.set_title("Factor explanatory power", loc="left", pad=4)
axD.grid(axis="y", visible=False)
axD.text(
    0.99,
    0.04,
    f"n = {int(gd.loc[0, 'n_cells'])} grids",
    transform=axD.transAxes,
    ha="right",
    va="bottom",
    fontsize=6.3,
    color="#666666",
)
ms.panel_label(axD, "D")

fig.text(
    0.01,
    0.005,
    "Data: Work_ming v5 outputs (GWR, grid Granger, multiscale LASSO models, GeoDetector). "
    "FDR = Benjamini–Hochberg across grids within each method.",
    fontsize=6,
    color="#777777",
)

paths = ms.save(fig, "fig2_mechanism")
print("\n".join(str(p) for p in paths))

