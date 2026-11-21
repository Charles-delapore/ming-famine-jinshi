"""Tests for ``src.data_processing.grid_integrator.integrate_grid_data``.

The function reads two CSV tables whose columns are fixed by the pipeline:
``EntryYear``/``X``/``Y`` for the jinshi table and ``year``/``X``/``Y``/
``level`` for the merged table.  A tiny 2x2 grid keeps the run well under a
second.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data_processing.grid_integrator import integrate_grid_data

PARAMS = {
    "x_min": 0.0,
    "x_max": 2.0,
    "y_min": 0.0,
    "y_max": 2.0,
    "grid_size": 1.0,
    "year_start": 1500,
    "year_end": 1502,
}


def _write_csv(tmp_path, name, df):
    path = tmp_path / name
    df.to_csv(path, index=False)
    return path


def _general():
    return pd.DataFrame(
        {
            "EntryYear": [1500, 1500, 1501],
            "X": [0.2, 1.2, 0.4],
            "Y": [0.3, 1.4, 0.6],
        }
    )


def _merged():
    return pd.DataFrame(
        {
            "year": [1500, 1500, 1501],
            "X": [0.2, 1.2, 0.4],
            "Y": [0.3, 1.4, 0.6],
            "level": [3, 5, 2],
        }
    )


def test_integrate_grid_data_builds_full_grid(tmp_path):
    general_path = _write_csv(tmp_path, "general.csv", _general())
    merged_path = _write_csv(tmp_path, "merged.csv", _merged())

    result = integrate_grid_data(general_path, merged_path, params=PARAMS)

    # 2 years x 2 x-cells x 2 y-cells.
    assert len(result) == 8
    assert list(result.columns) == ["Year", "Center_X", "Center_Y", "LevelG", "LevelD"]
    assert set(result["Year"]) == {1500, 1501}
    assert sorted(set(result["Center_X"])) == [0.5, 1.5]
    assert sorted(set(result["Center_Y"])) == [0.5, 1.5]


def test_integrate_grid_data_counts_and_max_level_per_cell(tmp_path):
    general_path = _write_csv(tmp_path, "general.csv", _general())
    merged_path = _write_csv(tmp_path, "merged.csv", _merged())

    result = integrate_grid_data(general_path, merged_path, params=PARAMS)

    def cell(year, x, y):
        row = result[
            (result["Year"] == year)
            & (result["Center_X"] == x)
            & (result["Center_Y"] == y)
        ]
        assert len(row) == 1
        return row.iloc[0]

    # (0.2, 0.3) falls in the lower-left cell.
    assert cell(1500, 0.5, 0.5)["LevelG"] == 1
    assert cell(1500, 0.5, 0.5)["LevelD"] == 3
    # (1.2, 1.4) falls in the upper-right cell.
    assert cell(1500, 1.5, 1.5)["LevelG"] == 1
    assert cell(1500, 1.5, 1.5)["LevelD"] == 5
    # Empty cells report zero events and zero severity.
    assert cell(1500, 0.5, 1.5)["LevelG"] == 0
    assert cell(1500, 0.5, 1.5)["LevelD"] == 0
    assert cell(1501, 0.5, 0.5)["LevelG"] == 1
    assert cell(1501, 0.5, 0.5)["LevelD"] == 2


def test_integrate_grid_data_uses_half_open_cells(tmp_path):
    general = pd.DataFrame({"EntryYear": [1500], "X": [1.0], "Y": [0.0]})
    merged = pd.DataFrame(
        {"year": [1500], "X": [1.0], "Y": [0.0], "level": [4]}
    )
    general_path = _write_csv(tmp_path, "general_boundary.csv", general)
    merged_path = _write_csv(tmp_path, "merged_boundary.csv", merged)

    result = integrate_grid_data(general_path, merged_path, params=PARAMS)

    # X == x_min + grid_size belongs to the next cell, not the first one.
    lower_left = result[(result["Center_X"] == 0.5) & (result["Center_Y"] == 0.5)]
    lower_right = result[(result["Center_X"] == 1.5) & (result["Center_Y"] == 0.5)]
    assert lower_left.iloc[0]["LevelG"] == 0
    assert lower_left.iloc[0]["LevelD"] == 0
    assert lower_right.iloc[0]["LevelG"] == 1
    assert lower_right.iloc[0]["LevelD"] == 4


def test_integrate_grid_data_missing_input_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        integrate_grid_data(
            tmp_path / "missing_general.csv",
            tmp_path / "missing_merged.csv",
            params=PARAMS,
        )
