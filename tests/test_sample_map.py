"""The synthetic sample map must not contain real fixed-window cells."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sample_map_has_no_real_fixed_layer():
    out = ROOT / "output" / "test_sample_map.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            [sys.executable, "scripts/make_interactive_map.py", "--sample",
             "--output", str(out)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        html = out.read_text(encoding="utf-8")
        assert "Fixed 1–5 yr joint test" not in html
        assert "Fixed 1–5 yr joint Granger" not in html
        assert "1° cell" in html
    finally:
        out.unlink(missing_ok=True)
