# Interactive map

`interactive_map.html` is a standalone Folium map of the **aggregated 1° grid**,
not the individual historical records. It is safe to publish alongside the
static figures because every layer is a grid-level summary.

## Layers

| Layer | Meaning |
|---|---|
| Famine severity | mean severity per 1° cell (all years) |
| Jinshi records | summed Jinshi records per 1° cell |
| GWR coefficient | local famine→Jinshi coefficient (estimable cells) |
| Fixed 1–5 yr joint test | cells where the pre-specified joint test survives FDR (headline, 2 cells) |
| Granger FDR (20-lag search) | cells where the 20-lag max-F search survives FDR (diagnostic, not the headline) |

The map includes a layer control, a scale control, a legend, a north arrow, and
a static fallback link to `figures/fig1_patterns.png`.

## Rebuild

```bash
export MING_OUTPUT=/path/to/Work_ming/output
python scripts/make_interactive_map.py
# -> web/interactive_map.html
```

For the synthetic sample:

```bash
python scripts/make_interactive_map.py \
  --output web/sample/interactive_map.html   # or set MING_MAP_OUT
```

If tiles do not load offline, the page still shows the vector layers; the
static fallback is always available.
