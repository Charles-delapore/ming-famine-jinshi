"""Shared visual system for the Ming famine / Jinshi portfolio figures.

Design rules
------------
* Colour-blind safe palette (Okabe-Ito) for categories.
* Sequential / diverging maps follow data semantics; no rainbow for ordered data.
* Every panel has: unit-bearing axis labels, N, and an explicit panel letter.
* Export vector (PDF/SVG) plus 600 dpi PNG; fonts embedded in PDF.
* Chinese place names fall back to Microsoft YaHei; Latin text uses Arial.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

# ---------------------------------------------------------------------------
# Palette (Okabe-Ito, colour-blind safe)
# ---------------------------------------------------------------------------
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILION = "#D55E00"
SKY = "#56B4E9"
PURPLE = "#CC79A7"
YELLOW = "#F0E442"
GREY = "#7F7F7F"
LIGHT_GREY = "#D9D9D9"

CATEGORICAL = [BLUE, ORANGE, GREEN, VERMILION, SKY, PURPLE, YELLOW, GREY]

FAMINE_CMAP = LinearSegmentedColormap.from_list(
    "famine_severity", ["#FFF3C4", "#FEC44F", "#FE9929", "#D95F0E", "#7F2704"]
)
JINSHI_CMAP = LinearSegmentedColormap.from_list(
    "jinshi_density", ["#EFF3FF", "#9ECAE1", "#4292C6", "#08519C", "#08306B"]
)
DIVERGING = "RdBu_r"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ.get("MING_ROOT", PROJECT_ROOT))
OUTPUT = Path(os.environ.get("MING_OUTPUT", ROOT / "output"))
DATA = Path(os.environ.get("MING_DATA", ROOT / "data" / "raw"))
PROVINCE_SHP = Path(os.environ.get("MING_BASEMAP", DATA / "province.shp"))
SAMPLE_BASEMAP = PROJECT_ROOT / "data" / "sample" / "basemap_china.geojson"

FIG_DIR = Path(os.environ.get("MING_FIG_DIR", PROJECT_ROOT / "figures"))
FIG_DIR.mkdir(parents=True, exist_ok=True)


def apply_style() -> None:
    """Apply the shared rcParams once per process."""
    mpl.rcParams.update(
        {
            "figure.facecolor": "white",
            "figure.dpi": 120,
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            "font.family": ["Arial", "Microsoft YaHei", "DejaVu Sans"],
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.titleweight": "bold",
            "axes.labelsize": 8,
            "axes.labelcolor": "#222222",
            "axes.edgecolor": "#444444",
            "axes.linewidth": 0.7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": "#E6E6E6",
            "grid.linewidth": 0.5,
            "grid.alpha": 0.9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "xtick.color": "#333333",
            "ytick.color": "#333333",
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "legend.fontsize": 7,
            "legend.frameon": False,
            "legend.handlelength": 1.2,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.unicode_minus": False,
        }
    )


def panel_label(ax, letter: str, x: float = -0.015, y: float = 1.015) -> None:
    ax.text(
        x,
        y,
        letter,
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        fontweight="bold",
        color="#111111",
        zorder=20,
    )


def save(fig, name: str, formats=("pdf", "png", "svg"), dpi: int = 600) -> list[Path]:
    """Write PDF + PNG + SVG; return written paths."""
    paths = []
    for fmt in formats:
        p = FIG_DIR / f"{name}.{fmt}"
        fig.savefig(p, format=fmt, dpi=dpi, bbox_inches="tight", pad_inches=0.02)
        paths.append(p)
    return paths


def load_provinces():
    """Load a basemap from MING_BASEMAP, DATA/province.shp, or the sample.

    Returns None when no basemap is available; style_map then draws the data on
    a clean background. This keeps the figure scripts runnable with the
    synthetic sample data and without redistributing the CHGIS basemap.
    """
    import geopandas as gpd

    candidates = [Path(os.environ["MING_BASEMAP"]) if os.environ.get("MING_BASEMAP") else None,
                  PROVINCE_SHP, SAMPLE_BASEMAP]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return gpd.read_file(candidate).to_crs(3857)
    return None


def style_map(ax, provinces, extent=None, add_ticks=False):
    if provinces is not None:
        provinces.plot(
            ax=ax, facecolor="#FBFBFB", edgecolor="#D0D0D0", linewidth=0.35, zorder=1
        )
    if extent is not None:
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
    ax.set_aspect("equal")
    ax.grid(False)
    if not add_ticks:
        ax.set_xticks([])
        ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    if not add_ticks:
        ax.set_axis_off()


def map_annotation(ax, x, y, text, **kw):
    color = kw.pop("color", "#555555")
    ax.annotate(
        text,
        xy=(x, y),
        xycoords="data",
        fontsize=6.5,
        color=color,
        ha="center",
        va="center",
        style="italic",
        **kw,
    )



