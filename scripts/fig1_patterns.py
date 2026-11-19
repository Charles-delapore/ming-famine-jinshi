"""Figure 1 — spatial pattern and temporal context of Ming famines and Jinshi.

Core claim: famine events form broad river-basin belts while Jinshi are
concentrated in the southeast; the two distributions overlap only partially.
The GWR panel shows that the famine–Jinshi association is spatially
heterogeneous, which motivates the grid-level causal analysis.

All panels read raw result tables; no values are invented or smoothed beyond
the explicitly labelled 5-year moving average.
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
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "style"))
import figure_kit as fk  # noqa: E402
import ming_style as ms  # noqa: E402

ms.apply_style()

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
z = pd.read_excel(ms.OUTPUT / "clustered_levels.xlsx")
j = pd.read_excel(ms.OUTPUT / "clustered_jinshi.xlsx")
gwr = pd.read_excel(ms.OUTPUT / "gwr_coefficients.xlsx")
prov = ms.load_provinces()

z = z.dropna(subset=["x", "y", "year", "level"]).copy()
z["year"] = z["year"].astype(int)
j = j.dropna(subset=["X", "Y", "EntryYear"]).copy()
j["EntryYear"] = j["EntryYear"].astype(int)

# Project to Web Mercator for correct shapes at these latitudes.
z_pts = gpd.GeoSeries(gpd.points_from_xy(z["x"], z["y"]), crs=4326).to_crs(3857)
j_pts = gpd.GeoSeries(gpd.points_from_xy(j["X"], j["Y"]), crs=4326).to_crs(3857)
gwr_pts = gpd.GeoSeries(
    gpd.points_from_xy(gwr["grid_x"], gwr["grid_y"]), crs=4326
).to_crs(3857)

zx, zy = z_pts.x.values, z_pts.y.values
jx, jy = j_pts.x.values, j_pts.y.values
gx, gy = gwr_pts.x.values, gwr_pts.y.values

pad = 180_000
extent = (zx.min() - pad, zx.max() + pad, zy.min() - pad, zy.max() + pad)

# ---------------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------------
years = np.arange(1522, 1620)
famine = z.groupby("year").agg(count=("level", "size"), severity=("level", "sum"))
famine = famine.reindex(years, fill_value=0)
jinshi = j.groupby("EntryYear").size().reindex(years, fill_value=0)
exam_years = jinshi[jinshi > 0].index.values
exam_counts = jinshi[jinshi > 0].values

f_ma = famine["severity"].rolling(5, center=True, min_periods=2).mean()

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(7.2, 8.4))
gs = GridSpec(
    2,
    2,
    figure=fig,
    height_ratios=[1.08, 1.0],
    width_ratios=[1.0, 1.0],
    hspace=0.16,
    wspace=0.08,
)

# --- A: famine events ------------------------------------------------------
axA = fig.add_subplot(gs[0, 0])
ms.style_map(axA, prov, extent)
axA.set_xlabel(""); axA.set_ylabel("")
levels = np.arange(0.5, 6.5, 1)
norm = BoundaryNorm(levels, ms.FAMINE_CMAP.N)
sc = axA.scatter(
    zx,
    zy,
    c=z["level"],
    s=6,
    cmap=ms.FAMINE_CMAP,
    norm=norm,
    alpha=0.55,
    linewidths=0,
    rasterized=True,
    zorder=3,
)
handles = [
    Line2D(
        [],
        [],
        marker="o",
        ls="",
        markersize=4,
        markerfacecolor=ms.FAMINE_CMAP(norm(v)),
        markeredgecolor="none",
        label=str(v),
    )
    for v in range(1, 6)
]
leg = axA.legend(
    handles=handles,
    title="Severity",
    loc="lower right",
    ncol=1,
    handletextpad=0.3,
    borderpad=0.25,
    labelspacing=0.18,
    fontsize=6,
    title_fontsize=6,
)
leg.get_frame().set_linewidth(0)
axA.set_title("Famine events, 1522–1619", loc="left", pad=4)
axA.text(
    0.01,
    0.01,
    f"n = {len(z):,} events",
    transform=axA.transAxes,
    fontsize=6.5,
    color="#555555",
    ha="left",
    va="bottom",
)
for lon, lat, txt in [
    (116.5, 37.2, "North China Plain"),
    (119.8, 31.2, "Jiangnan"),
    (112.0, 30.3, "Yangtze"),
    (113.5, 34.8, "Yellow River"),
]:
    pt = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(3857).iloc[0]
    ms.map_annotation(axA, pt.x, pt.y, txt)
ms.panel_label(axA, "A")
fk.add_scale_north(axA)

# --- B: Jinshi -------------------------------------------------------------
axB = fig.add_subplot(gs[0, 1])
ms.style_map(axB, prov, extent)
axB.set_xlabel(""); axB.set_ylabel("")
axB.scatter(
    jx,
    jy,
    s=8,
    c=ms.BLUE,
    alpha=0.55,
    linewidths=0,
    rasterized=True,
    zorder=3,
)
axB.set_title("Jinshi (metropolitan graduates), 1521–1619", loc="left", pad=4)
axB.text(
    0.01,
    0.01,
    f"n = {len(j):,} graduates",
    transform=axB.transAxes,
    fontsize=6.5,
    color="#555555",
    ha="left",
    va="bottom",
)
for lon, lat, txt in [
    (120.2, 31.0, "Jiangnan core"),
    (116.8, 36.8, "North China"),
    (113.0, 28.0, "Middle Yangtze"),
]:
    pt = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(3857).iloc[0]
    ms.map_annotation(axB, pt.x, pt.y, txt, color="#1F4E79")
ms.panel_label(axB, "B")
fk.add_scale_north(axB)

# --- C: aligned time series ------------------------------------------------
sub = gs[1, 0].subgridspec(2, 1, height_ratios=[1, 1], hspace=0.08)
axC1 = fig.add_subplot(sub[0, 0])
axC2 = fig.add_subplot(sub[1, 0], sharex=axC1)

axC1.bar(
    years,
    famine["severity"],
    color="#F4A582",
    edgecolor="none",
    alpha=0.55,
    width=0.85,
    label="Annual severity sum",
)
axC1.plot(years, f_ma, color="#B2182B", lw=1.4, label="5-year moving average")
axC1.set_ylabel("Famine severity\n(sum of levels)", fontsize=7)
axC1.legend(loc="upper left", ncol=1, handlelength=1.0)
axC1.tick_params(labelbottom=False)
axC1.set_title("Temporal context", loc="left", pad=4)
axC1.text(
    0.99,
    0.92,
    f"mean {famine['count'].mean():.1f} events yr$^{{-1}}$",
    transform=axC1.transAxes,
    ha="right",
    va="top",
    fontsize=6.5,
    color="#555555",
)

axC2.vlines(
    exam_years,
    0,
    exam_counts,
    color="#92C5DE",
    lw=1.1,
    alpha=0.85,
    label="Jinshi per exam year",
)
axC2.scatter(exam_years, exam_counts, s=9, color="#2166AC", zorder=3)
axC2.set_ylabel("Jinshi count\n(graduates per exam)", fontsize=7)
axC2.set_xlabel("Year (CE)", fontsize=7)
axC2.legend(loc="upper left", handlelength=1.0)
axC2.set_xlim(1520, 1620)
axC2.set_xticks(np.arange(1520, 1621, 20))
axC2.text(
    0.99,
    0.92,
    f"exam years only; n = {len(j):,}",
    transform=axC2.transAxes,
    ha="right",
    va="top",
    fontsize=6.5,
    color="#555555",
)
ms.panel_label(axC1, "C")

# --- D: GWR coefficients ---------------------------------------------------
axD = fig.add_subplot(gs[1, 1])
ms.style_map(axD, prov, extent)
axD.set_xlabel(""); axD.set_ylabel("")
coef = gwr["gwr_coef"].astype(float)
coef_norm = TwoSlopeNorm(vmin=min(float(coef.min()), -0.05),
                         vcenter=0.0,
                         vmax=max(float(coef.max()), 0.05))
sig = gwr["gwr_sig"].astype(bool).values
axD.scatter(
    gx[~sig],
    gy[~sig],
    c=gwr.loc[~sig, "gwr_coef"],
    cmap=ms.DIVERGING,
    norm=coef_norm,
    s=20,
    marker="s",
    alpha=0.20,
    linewidths=0,
    rasterized=True,
    zorder=3,
)
sc2 = axD.scatter(
    gx[sig],
    gy[sig],
    c=gwr.loc[sig, "gwr_coef"],
    cmap=ms.DIVERGING,
    norm=coef_norm,
    s=24,
    marker="s",
    alpha=0.95,
    linewidths=0,
    rasterized=True,
    zorder=4,
)
cb2 = fig.colorbar(sc2, ax=axD, fraction=0.040, pad=0.015, shrink=0.78)
cb2.set_label("GWR coefficient\n(famine → Jinshi)", fontsize=7)
cb2.ax.tick_params(labelsize=6)
cb2.outline.set_linewidth(0.3)
axD.set_title("Spatial heterogeneity (GWR)", loc="left", pad=4)
axD.text(
    0.01,
    0.01,
    f"{int(sig.sum())}/{len(gwr)} grids significant (p < 0.05)",
    transform=axD.transAxes,
    fontsize=6.5,
    color="#555555",
    ha="left",
    va="bottom",
)
handles = [
    Line2D([], [], marker="s", ls="", color="#B2182B", label="significant"),
    Line2D([], [], marker="s", ls="", color="#DDDDDD", label="not significant"),
]
axD.legend(
    handles=handles, loc="upper right", fontsize=6, handletextpad=0.4, borderpad=0.2
)
ms.panel_label(axD, "D")
fk.scale_bar(axD)
fk.north_arrow(axD, location=(0.93, 0.80))

# ---------------------------------------------------------------------------
# Provenance note
# ---------------------------------------------------------------------------
if os.environ.get("MING_SAMPLE") == "1":
    note = ("Synthetic sample data for code verification — not historical records. "
            "Basemap: Natural Earth 1:110m (public domain).")
else:
    n_j = len(j)
    layer = ("normalized 1甲/2甲 elite, v0.3" if n_j > 1500
             else "Arabic-coded 1甲/2甲 subset, v0.2")
    note = (f"Data: CHGIS v6; {len(z):,} famine records; CBDB Jinshi export "
            f"(n={n_j:,}; {layer}; see docs/jinshi_provenance.md). "
            "Projection: Web Mercator. Moving average: 5-year centred window. "
            "Scale bars approximate at map-centre latitude.")
fig.text(0.01, 0.005, note, fontsize=6, color="#777777")

paths = ms.save(fig, "fig1_patterns")
print("\n".join(str(p) for p in paths))








