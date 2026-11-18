"""The figure manifest must point at files and scripts that exist."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "figures" / "figure_manifest.csv"


def test_manifest_files_and_scripts_exist():
    df = pd.read_csv(MANIFEST)
    assert {"id", "file", "script", "status"} <= set(df.columns)
    assert df["id"].is_unique
    for _, row in df.iterrows():
        assert (ROOT / row["file"]).exists(), f"missing figure: {row['file']}"
        assert (ROOT / row["script"]).exists(), f"missing script: {row['script']}"
        assert row["status"] in {"main", "supplementary", "audit", "retired"}
