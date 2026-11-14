"""Reusable journal-figure furniture: scale bar, north arrow, footer.

The functions work in axes coordinates and assume the map axes are in Web
Mercator metres (as in the Ming figures). The scale bar length is corrected for
the mean latitude of the axis; the label says "approx." because a projected map
always has local distortion.
"""

from __future__ import annotations

import numpy as np

R_EARTH = 6_378_137.0


def _lat_from_y(y: float) -> float:
    return float(np.degrees(np.arctan(np.sinh(y / R_EARTH))))


def scale_bar(
    ax,
    km: float = 500,
    location: tuple[float, float] = (0.06, 0.06),
    height: float = 0.012,
    color: str = "#333333",
    fontsize: float = 6,
) -> None:
    """Draw a two-segment scale bar in axes coordinates."""
    x0, y0 = location
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    mean_lat = _lat_from_y((ylim[0] + ylim[1]) / 2)
    # Web Mercator inflates distance by 1/cos(lat); convert ground km to map m.
    half_map_m = (km * 500.0) / max(np.cos(np.radians(mean_lat)), 1e-6)
    frac = half_map_m / (xlim[1] - xlim[0])
    h = height

    # two alternating segments
    ax.plot([x0, x0 + frac], [y0, y0], transform=ax.transAxes,
            color=color, lw=1.2, solid_capstyle="butt", zorder=20)
    ax.plot([x0 + frac, x0 + 2 * frac], [y0, y0], transform=ax.transAxes,
            color=color, lw=1.2, solid_capstyle="butt", zorder=20)
    for xx in (x0 + frac, x0 + 2 * frac):
        ax.plot([xx, xx], [y0 - h / 2, y0 + h / 2], transform=ax.transAxes,
                color=color, lw=0.9, zorder=20)

    ax.text(x0, y0 + h * 1.2, "0", transform=ax.transAxes,
            fontsize=fontsize, color=color, ha="center", va="bottom")
    ax.text(x0 + 2 * frac, y0 + h * 1.2, f"{km:g} km*", transform=ax.transAxes,
            fontsize=fontsize, color=color, ha="center", va="bottom")


def north_arrow(
    ax,
    location: tuple[float, float] = (0.93, 0.91),
    size: float = 0.045,
    color: str = "#333333",
    fontsize: float = 7,
) -> None:
    """Draw a simple north arrow in axes coordinates."""
    x, y = location
    ax.annotate(
        "",
        xy=(x, y + size),
        xytext=(x, y - size),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.0,
                        mutation_scale=9, shrinkA=0, shrinkB=0),
        zorder=21,
    )
    ax.text(x, y + size + 0.012, "N", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=fontsize, color=color,
            fontweight="bold", zorder=21)


def add_scale_north(ax, km: float = 500, **kw) -> None:
    """Convenience wrapper for map panels."""
    scale_bar(ax, km=km, **kw)
    north_arrow(ax)


def footer(fig, text: str, y: float = 0.005, fontsize: float = 6) -> None:
    fig.text(0.01, y, text, fontsize=fontsize, color="#777777", ha="left", va="bottom")


def distribution_annotation(ax, values, x: float = 0.98, y: float = 0.95) -> None:
    arr = np.asarray(values, dtype=float)
    ax.text(
        x, y,
        f"n = {len(arr)}\nmedian = {np.median(arr):.2f}",
        transform=ax.transAxes, ha="right", va="top", fontsize=6.5,
        color="#555555",
    )

