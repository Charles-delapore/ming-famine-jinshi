"""Figure 3 — graphical abstract: from sparse historical records to
spatially explicit causal evidence.

This is the portfolio hero: it uses the real data objects (event points,
1-degree grid, GWR coefficient surface) rather than generic boxes-and-arrows.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, TwoSlopeNorm
from matplotlib.patches import FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "style"))
import ming_style as ms  # noqa: E402

ms.apply_style()

z = pd.read_excel(ms.OUTPUT / "clustered_levels.xlsx")
j = pd.read_excel(ms.OUTPUT / "clustered_jinshi.xlsx")
grid = pd.read_csv(ms.OUTPUT / "grid_data_enriched.csv")
gwr = pd.read_excel(ms.OUTPUT / "gwr_coefficients.xlsx")
gg = pd.read_excel(ms.OUTPUT / "grid_granger_causality.xlsx")
prov = ms.load_provinces()

z = z.dropna(subset=["x", "y", "level"])
j = j.dropna(subset=["X", "Y"])

zpts = gpd.GeoSeries(gpd.points_from_xy(z["x"], z["y"]), crs=4326).to_crs(3857)
jpts = gpd.GeoSeries(gpd.points_from_xy(j["X"], j["Y"]), crs=4326).to_crs(3857)
gwrpts = gpd.GeoSeries(
    gpd.points_from_xy(gwr["grid_x"], gwr["grid_y"]), crs=4326
).to_crs(3857)

pad = 160_000
extent = (
    zpts.x.min() - pad,
    zpts.x.max() + pad,
    zpts.y.min() - pad,
    zpts.y.max() + pad,
)

# Aggregate grid cells over the full panel for the middle panel
cell = (
    grid.groupby(["grid_x", "grid_y"])
    .agg(
        severity=("zaihuang_severity", "mean"),
        jinshi=("jinshi_count", "sum"),
    )
    .reset_index()
)
cell_pts = gpd.GeoSeries(
    gpd.points_from_xy(cell["grid_x"], cell["grid_y"]), crs=4326
).to_crs(3857)

fig = plt.figure(figsize=(7.4, 3.15))
gs = fig.add_gridspec(1, 3, wspace=0.06, left=0.01, right=0.99, top=0.83, bottom=0.06)

titles = [
    "1 · Fuse",
    "2 · Aggregate",
    "3 · Infer & explain",
]
subtitles = [
    "synthetic event tables · sample basemap"
    if os.environ.get("MING_SAMPLE") == "1"
    else "CHGIS · famine records · paleoclimate",
    f"1° grid × 114 years · {len(cell)} cells",
    "Granger · GWR · GeoDetector",
]

axes = []
for k in range(3):
    ax = fig.add_subplot(gs[0, k])
    ms.style_map(ax, prov, extent)
    axes.append(ax)

# --- 1: raw points ---------------------------------------------------------
axA = axes[0]
axA.scatter(
    zpts.x,
    zpts.y,
    c=z["level"],
    s=4,
    cmap=ms.FAMINE_CMAP,
    alpha=0.55,
    linewidths=0,
    rasterized=True,
    zorder=3,
)
axA.scatter(
    jpts.x,
    jpts.y,
    s=4,
    c=ms.BLUE,
    alpha=0.50,
    linewidths=0,
    rasterized=True,
    zorder=3,
)
axA.set_title(titles[0], loc="left", pad=3, fontsize=9)
axA.text(
    0.01,
    0.97,
    subtitles[0],
    transform=axA.transAxes,
    fontsize=5.8,
    color="#555555",
    ha="left",
    va="top",
)

# --- 2: grid ---------------------------------------------------------------
axB = axes[1]
vmax = np.nanpercentile(cell["severity"], 98)
sc = axB.scatter(
    cell_pts.x,
    cell_pts.y,
    c=cell["severity"],
    cmap=ms.FAMINE_CMAP,
    s=8,
    marker="s",
    linewidths=0,
    vmin=0,
    vmax=vmax,
    rasterized=True,
    zorder=3,
)
axB.set_title(titles[1], loc="left", pad=3, fontsize=9)
axB.text(
    0.01,
    0.97,
    subtitles[1],
    transform=axB.transAxes,
    fontsize=5.8,
    color="#555555",
    ha="left",
    va="top",
)
# highlight one cell and its 114-year panel
ex, ey = 118.5, 31.5
p = gpd.GeoSeries([gpd.points_from_xy([ex], [ey])[0]], crs=4326).to_crs(3857).iloc[0]
axB.add_patch(
    plt.Rectangle(
        (p.x - 55_000, p.y - 55_000),
        110_000,
        110_000,
        fill=False,
        edgecolor="#111111",
        lw=0.9,
        zorder=6,
    )
)
axB.annotate(
    "one cell =\n114-year panel",
    xy=(p.x + 55_000, p.y + 55_000),
    xytext=(p.x + 420_000, p.y + 240_000),
    fontsize=5.5,
    color="#333333",
    arrowprops=dict(arrowstyle="-", lw=0.5, color="#555555"),
)

# --- 3: GWR coefficient surface -------------------------------------------
axC = axes[2]
coef = gwr["gwr_coef"].astype(float)
coef_norm = TwoSlopeNorm(vmin=min(float(coef.min()), -0.05),
                         vcenter=0.0,
                         vmax=max(float(coef.max()), 0.05))
sig = gwr["gwr_sig"].astype(bool).values
axC.scatter(
    gwrpts.x[~sig],
    gwrpts.y[~sig],
    c=gwr.loc[~sig, "gwr_coef"],
    cmap=ms.DIVERGING,
    norm=coef_norm,
    s=13,
    marker="s",
    linewidths=0,
    alpha=0.25,
    rasterized=True,
    zorder=3,
)
sc2 = axC.scatter(
    gwrpts.x[sig],
    gwrpts.y[sig],
    c=gwr.loc[sig, "gwr_coef"],
    cmap=ms.DIVERGING,
    norm=coef_norm,
    s=17,
    marker="s",
    linewidths=0,
    alpha=0.95,
    rasterized=True,
    zorder=4,
)
axC.set_title(titles[2], loc="left", pad=3, fontsize=9)
axC.text(
    0.01,
    0.97,
    subtitles[2],
    transform=axC.transAxes,
    fontsize=5.8,
    color="#555555",
    ha="left",
    va="top",
)
axC.text(
    0.01,
    0.03,
    f"{int(gwr['gwr_sig'].sum())}/{len(gwr)} GWR grids significant\n{int(gg['gc_z_to_j_fdr_sig'].sum())}/{len(gg)} Granger grids FDR-significant",
    transform=axC.transAxes,
    fontsize=5.4,
    color="#333333",
    ha="left",
    va="bottom",
)

# Shared colorbar under panel 3
cb = fig.colorbar(
    sc2,
    ax=axC,
    orientation="horizontal",
    fraction=0.05,
    pad=0.05,
    shrink=0.85,
    aspect=30,
)
cb.set_label("Famine → Jinshi GWR coefficient", fontsize=6)
cb.ax.tick_params(labelsize=5.5)
cb.outline.set_linewidth(0.3)

# arrows between panels
for k in (0, 1):
    x0 = axes[k].get_position().x1 + 0.005
    x1 = axes[k + 1].get_position().x0 - 0.005
    y = (axes[k].get_position().y0 + axes[k].get_position().y1) / 2
    fig.add_artist(
        FancyArrowPatch(
            (x0, y),
            (x1, y),
            transform=fig.transFigure,
            arrowstyle="-|>",
            mutation_scale=9,
            lw=0.8,
            color="#666666",
        )
    )

fig.text(
    0.5,
    0.93,
    "From sparse historical records to spatially explicit causal evidence",
    ha="center",
    va="center",
    fontsize=10,
    fontweight="bold",
    color="#111111",
)
subtitle = (
    "Synthetic sample data — for code verification only"
    if os.environ.get("MING_SAMPLE") == "1"
    else f"Ming dynasty famines and Jinshi, 1521–1619  ·  {len(z):,} events  ·  {len(j):,} graduates  ·  {len(cell)} grid cells"
)
fig.text(
    0.5,
    0.885,
    subtitle,
    ha="center",
    va="center",
    fontsize=6.2,
    color="#666666",
)

paths = ms.save(fig, "fig3_framework")
print("\n".join(str(p) for p in paths))




