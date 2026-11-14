"""Assemble the v0.3 figure inputs from the corrected grid panel.

Outputs land in output/v03/fig_input with the filenames the figure scripts
expect. This script does not publish anything; it only builds local inputs.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V03 = Path(os.environ.get("MING_V03_OUT", ROOT / "output" / "v03"))
FIG = V03 / "fig_input"
OLD_OUTPUT = Path(os.environ.get("MING_OUTPUT_OLD", r"data/private/v02_output"))
RAW = Path(os.environ.get("MING_JINSHI_RAW", ROOT / "data" / "raw" / "明进士.xlsx"))

sys.path.insert(0, str(ROOT))
from src.algorithms.ss_dbscan import SSDBSCAN  # noqa: E402
from src.data_processing.jinshi_rank import rank_level  # noqa: E402
from src.analysis.grid_analysis import (  # noqa: E402
    MultiScaleCausalModel,
    compute_grid_derived_features,
)
from src.analysis.sensitivity_analysis import run_geodetector  # noqa: E402


def build_corrected_jinshi() -> pd.DataFrame:
    raw = pd.read_excel(RAW)
    raw["year"] = pd.to_numeric(raw.get("EntryYear"), errors="coerce")
    raw["level"] = raw.get("EntryRank").map(rank_level)
    elite = raw[raw["level"].isin([1, 2]) & raw["year"].between(1521, 1619)]
    elite = elite.dropna(subset=["X", "Y"]).drop_duplicates("PersonID").copy()
    elite["EntryYear"] = elite["year"].astype(int)

    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    scaled = scaler.fit_transform(elite[["X", "Y", "EntryYear"]])
    features = np.hstack((scaled, elite[["level"]].values))
    model = SSDBSCAN(
        eps=0.7,
        min_samples=3,
        weights=[1.0, 1.0, 0.3, 0.1],
        max_cluster_size=None,
        important_levels=[1, 2],
    ).fit(features)
    elite["cluster"] = model.labels_
    print(f"corrected elite: {len(elite)} rows, {model.n_clusters_} clusters")
    return elite


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)

    panel = pd.read_csv(V03 / "panel_v03.csv.gz")
    enriched = compute_grid_derived_features(panel)
    enriched.to_csv(FIG / "grid_data_enriched.csv", index=False)

    ms = MultiScaleCausalModel(
        significance=0.05,
        use_ridge_when_collinear=True,
        vif_threshold=10.0,
        use_lasso_filter=True,
        use_bic_selection=True,
    )
    results = ms.fit_stratified_model(enriched)
    for scale, frame in results.items():
        frame.to_excel(FIG / f"multiscale_causal_{scale}.xlsx", index=False, engine="openpyxl")
        print(f"{scale}: {len(frame)} grids, {int(frame['fdr_significant'].sum())} FDR-significant")

    # run_geodetector writes geodetector_results.xlsx into MING_OUTPUT.
    os.environ["MING_OUTPUT"] = str(FIG)
    import src.analysis.sensitivity_analysis as sa

    sa.OUTPUT_DIR = FIG
    run_geodetector(panel)

    shutil.copy2(V03 / "gwr_v03.xlsx", FIG / "gwr_coefficients.xlsx")
    shutil.copy2(V03 / "granger_v03.xlsx", FIG / "grid_granger_causality.xlsx")
    shutil.copy2(OLD_OUTPUT / "clustered_levels.xlsx", FIG / "clustered_levels.xlsx")

    jinshi = build_corrected_jinshi()
    cols = [
        "NameChn", "IndexYear", "EntryChn", "EntryYear", "EntryRank",
        "AddrName", "AddrChn", "X", "Y", "xy_count", "level", "cluster",
    ]
    jinshi[[c for c in cols if c in jinshi.columns]].to_excel(
        FIG / "clustered_jinshi.xlsx", index=False, engine="openpyxl"
    )
    print(f"wrote figure inputs to {FIG}")


if __name__ == "__main__":
    main()
