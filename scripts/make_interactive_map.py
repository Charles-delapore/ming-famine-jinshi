"""Build a standalone interactive map from aggregated 1-degree layers.

The map deliberately uses **aggregated grid cells**, not individual historical
records, so the public repository does not redistribute the private event table.

Layers
  1. Mean famine severity per 1-degree cell
  2. Jinshi records aggregated to the same cells
  3. GWR coefficient per estimable cell
  4. Famine->Jinshi Granger cells that survive FDR

Usage
  MING_OUTPUT=/path/to/output python scripts/make_interactive_map.py
  MING_OUTPUT=./data/sample MING_SAMPLE=1 python scripts/make_interactive_map.py
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import branca.colormap as cm
import folium
import numpy as np
import pandas as pd
from folium import Element

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=None)
parser.add_argument("--sample", action="store_true")
args = parser.parse_args()
OUTPUT = Path(os.environ.get("MING_OUTPUT", ROOT / "output"))
OUT = args.output or Path(os.environ.get("MING_MAP_OUT", ROOT / "web" / "interactive_map.html"))
SAMPLE = args.sample or os.environ.get("MING_SAMPLE") == "1"

OUT.parent.mkdir(parents=True, exist_ok=True)

grid = pd.read_csv(OUTPUT / "grid_data_enriched.csv")
gwr = pd.read_excel(OUTPUT / "gwr_coefficients.xlsx")
gg = pd.read_excel(OUTPUT / "grid_granger_causality.xlsx")

cells = (
    grid.groupby(["grid_x", "grid_y"])
    .agg(
        severity=("zaihuang_severity", "mean"),
        jinshi=("jinshi_count", "sum"),
        years=("year", "nunique"),
    )
    .reset_index()
)
cells = cells.merge(
    gwr[["grid_x", "grid_y", "gwr_coef", "gwr_sig", "gwr_local_r2"]],
    on=["grid_x", "grid_y"],
    how="left",
).merge(
    gg[["grid_x", "grid_y", "gc_z_to_j_qval", "gc_z_to_j_fdr_sig"]],
    on=["grid_x", "grid_y"],
    how="left",
)

sev_max = float(np.nanmax(cells["severity"])) or 1.0
sev_cmap = cm.LinearColormap(
    ["#FFF3C4", "#FEC44F", "#FE9929", "#D95F0E", "#7F2704"],
    vmin=0.0,
    vmax=sev_max,
    caption="Mean famine severity (1-degree cell)",
)
coef_vals = cells["gwr_coef"].dropna()
coef_abs = float(max(abs(coef_vals.min()), abs(coef_vals.max()))) if len(coef_vals) else 1.0
coef_cmap = cm.LinearColormap(
    ["#2166AC", "#F7F7F7", "#B2182B"],
    vmin=-coef_abs,
    vmax=coef_abs,
    caption="GWR coefficient (famine -> Jinshi)",
)
jinshi_max = float(np.nanmax(cells["jinshi"])) or 1.0

m = folium.Map(
    location=[33.0, 112.0],
    zoom_start=4,
    min_zoom=3,
    max_zoom=8,
    tiles="OpenStreetMap",
    attr="© OpenStreetMap contributors | 1-degree aggregates; no individual records",
    control_scale=True,
)

severity_layer = folium.FeatureGroup(name="Famine severity (1° mean)", show=True)
jinshi_layer = folium.FeatureGroup(name="Jinshi records (1° sum)", show=False)
gwr_layer = folium.FeatureGroup(name="GWR coefficient (famine → Jinshi)", show=False)
granger_layer = folium.FeatureGroup(name="Granger FDR-significant cells", show=False)

for _, row in cells.iterrows():
    x, y = float(row["grid_x"]), float(row["grid_y"])
    bounds = [[y - 0.5, x - 0.5], [y + 0.5, x + 0.5]]
    sev = float(row["severity"])
    folium.Rectangle(
        bounds=bounds,
        color=None,
        fill=True,
        fill_color=sev_cmap(sev),
        fill_opacity=0.55,
        weight=0,
        tooltip=folium.Tooltip(
            f"<b>1° cell</b><br>lon {x:.1f}, lat {y:.1f}<br>"
            f"mean famine severity: {sev:.2f}<br>years observed: {int(row['years'])}"
        ),
    ).add_to(severity_layer)

    jinshi = float(row["jinshi"])
    if jinshi > 0:
        folium.CircleMarker(
            location=[y, x],
            radius=2.5 + 5.0 * np.sqrt(jinshi / jinshi_max),
            color="#08519C",
            fill=True,
            fill_color="#4292C6",
            fill_opacity=0.55,
            weight=0.5,
            tooltip=folium.Tooltip(f"Jinshi records (sum): {int(jinshi)}"),
        ).add_to(jinshi_layer)

    coef = row["gwr_coef"]
    if pd.notna(coef):
        folium.Rectangle(
            bounds=bounds,
            color=None,
            fill=True,
            fill_color=coef_cmap(float(coef)),
            fill_opacity=0.65,
            weight=0,
            tooltip=folium.Tooltip(
                f"GWR coefficient: {float(coef):.2f}<br>"
                f"local R²: {float(row['gwr_local_r2']):.2f}<br>"
                f"significant: {bool(row['gwr_sig'])}"
            ),
        ).add_to(gwr_layer)

    if pd.notna(row.get("gc_z_to_j_fdr_sig", False)) and bool(row.get("gc_z_to_j_fdr_sig")):
        folium.CircleMarker(
            location=[y, x],
            radius=5,
            color="#FFFFFF",
            weight=0.8,
            fill=True,
            fill_color="#D55E00",
            fill_opacity=0.9,
            tooltip=folium.Tooltip(
                f"Famine→Jinshi Granger FDR-significant<br>q = {float(row['gc_z_to_j_qval']):.3f}"
            ),
        ).add_to(granger_layer)

severity_layer.add_to(m)
jinshi_layer.add_to(m)
gwr_layer.add_to(m)
granger_layer.add_to(m)
folium.LayerControl(collapsed=False, position="topright").add_to(m)

# Legend + north arrow + title/abstract as fixed overlays.
fallback_href = Path(os.path.relpath(ROOT / "figures" / "fig1_patterns.png", OUT.parent)).as_posix()
readme_href = Path(os.path.relpath(ROOT / "README.md", OUT.parent)).as_posix()
legend = f"""
<div style="position:fixed;left:18px;bottom:62px;z-index:9999;background:rgba(255,255,255,.94);
            border:1px solid #d7dde3;border-radius:10px;padding:10px 12px;
            font:12px/1.5 Arial,'Microsoft YaHei',sans-serif;color:#222;max-width:290px">
  <b>Legend</b><br>
  <span style="display:inline-block;width:12px;height:12px;background:#FEC44F;border-radius:2px"></span>
  Famine severity (1° mean)<br>
  <span style="display:inline-block;width:12px;height:12px;background:#4292C6;border-radius:50%"></span>
  Jinshi records (1° sum)<br>
  <span style="display:inline-block;width:12px;height:12px;background:#B2182B;border-radius:2px"></span>
  GWR coefficient (diverging)<br>
  <span style="display:inline-block;width:12px;height:12px;background:#D55E00;border-radius:50%;border:1px solid #fff"></span>
  Granger FDR-significant cell<br>
  <span style="color:#666">1° aggregates; no individual records.</span>
</div>
<div style="position:fixed;left:18px;top:86px;z-index:9999;background:rgba(255,255,255,.94);
            border:1px solid #d7dde3;border-radius:10px;padding:10px 12px;
            font:12px/1.5 Arial,'Microsoft YaHei',sans-serif;color:#222;max-width:310px">
  <b>Ming famines &amp; Jinshi, 1521–1619</b><br>
  Grid-level FDR, GWR and severity. Aggregated to 1° cells; not individual records.<br>
  <a href="{fallback_href}">Static fallback (Fig. 1)</a> ·
  <a href="{readme_href}">Methods</a>
</div>
<div style="position:fixed;right:26px;top:150px;z-index:9999;text-align:center;
            font:700 16px Arial,sans-serif;color:#222;text-shadow:0 0 3px #fff">
  N<br><span style="font-size:26px;line-height:18px">↑</span>
</div>
"""
m.get_root().html.add_child(Element(legend))

note = (
    "Synthetic sample data — for code verification only."
    if SAMPLE
    else "Data: Work_ming v5 1° aggregates. Raw historical tables are not redistributed."
)
m.get_root().html.add_child(
    Element(
        f'<div style="position:fixed;left:18px;top:18px;z-index:9999;'
        f'background:rgba(255,255,255,.94);border:1px solid #d7dde3;border-radius:10px;'
        f'padding:8px 12px;font:11px/1.5 Arial,sans-serif;color:#555;max-width:360px">'
        f"<b>Interactive 1° grid</b><br>{note}</div>"
    )
)

m.save(str(OUT))
print(f"wrote {OUT} ({OUT.stat().st_size/1024:.1f} KB)")
print(f"cells={len(cells)} granger_sig={int(cells['gc_z_to_j_fdr_sig'].fillna(False).sum())}")






