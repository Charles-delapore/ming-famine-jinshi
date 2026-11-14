#!/usr/bin/env python3
"""Colourblind simulation check (standard 2).

Applies the Machado et al. (2009) simulation matrices for protanopia and
deuteranopia to a PNG figure. Pure numpy + Pillow, no extra dependency.
Adapted from the 2026-11-14 geography research bundle (08 prototype).\nUsage: python tools/colorblind_check.py figures/fig1_patterns.png
Outputs: <name>_protanopia.png, <name>_deuteranopia.png next to the input.
"""
import sys
import numpy as np
from PIL import Image

# Machado et al. 2009, "A model for simulation of colour blindness" (severity 1.0)
MATRICES = {
    "protanopia": np.array([
        [0.567, 0.433, 0.0],
        [0.558, 0.442, 0.0],
        [0.0, 0.242, 0.758],
    ]),
    "deuteranopia": np.array([
        [0.625, 0.375, 0.0],
        [0.7, 0.3, 0.0],
        [0.0, 0.3, 0.7],
    ]),
}


def simulate(path: str) -> None:
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img, dtype=np.float64) / 255.0
    for name, m in MATRICES.items():
        sim = np.clip(arr @ m.T, 0, 1)
        out = path.rsplit(".", 1)[0] + f"_{name}.png"
        Image.fromarray((sim * 255).astype(np.uint8)).save(out)
        print("saved", out)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        simulate(p)

