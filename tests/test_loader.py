"""Tests for the public load/merge helpers in ``src.data_processing.loader``.

The loader reads Excel workbooks (the private raw tables are ``.xlsx``), so the
fixtures below are small synthetic workbooks written to ``tmp_path``.  Functions
that only resolve fixed external paths are not exercised here.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.data_processing import loader


def _write_xlsx(tmp_path, name, df):
    path = tmp_path / name
    df.to_excel(path, index=False)
    return path


def _cities():
    # The duplicate code is intentional: loaders de-duplicate city rows.
    return pd.DataFrame(
        {
            "code": [1, 2, 2],
            "x": [110.0, 120.0, 120.0],
            "y": [30.0, 40.0, 40.0],
        }
    )


def _levels():
    return pd.DataFrame(
        {
            "year": [1500.0, 1501.0, 1501.0],
            "code": [1, 2, 1],
            "level": [3, 5, 4],
        }
    )


def _general():
    return pd.DataFrame(
        {
            "EntryRank": ["第一甲第一名", "第2甲第3名", None, "第三甲第7名",
                          "第一甲第二名"],
            "EntryYear": [1500, 1501, 1502, 1503, None],
            "X": [110.0, 120.0, 111.0, 121.0, 112.0],
            "Y": [30.0, 40.0, 31.0, 41.0, 32.0],
        }
    )


def test_load_zaihuang_data_merges_city_coordinates(tmp_path):
    city_path = _write_xlsx(tmp_path, "cities.xlsx", _cities())
    level_path = _write_xlsx(tmp_path, "levels.xlsx", _levels())

    merged = loader.load_zaihuang_data(city_path, level_path)

    assert list(merged.columns) == ["year", "code", "level", "x", "y"]
    assert len(merged) == 3
    assert merged["year"].dtype.kind == "i"
    # A duplicated city code must not duplicate the level rows.
    assert len(merged[merged["code"] == 1]) == 2
    assert merged.loc[merged["code"] == 2, "x"].iloc[0] == 120.0


def test_load_zaihuang_data_full_keeps_unmatched_rows_and_drops_unnamed(tmp_path):
    cities = _cities()
    levels = _levels()
    # Replace the matched code 2 with code 3, which exists only in the level table.
    levels.loc[levels["code"] == 2, "code"] = 3
    levels["Unnamed: 3"] = ["a", "b", "c"]
    city_path = _write_xlsx(tmp_path, "cities_full.xlsx", cities)
    level_path = _write_xlsx(tmp_path, "levels_full.xlsx", levels)

    merged = loader.load_zaihuang_data_full(city_path, level_path)

    # Two level rows for code 1, one level-only row (code 3), one city-only row (code 2).
    assert len(merged) == 4
    assert {1, 2, 3} <= set(merged["code"])
    assert not any("Unnamed" in str(col) for col in merged.columns)
    # City-only row (code 2) keeps its coordinates but has no level.
    assert pd.isna(merged.loc[merged["code"] == 2, "level"]).all()
    # Level-only row (code 3) has no city coordinates.
    assert pd.isna(merged.loc[merged["code"] == 3, "x"]).all()


def test_load_jinshi_data_drops_missing_rank(tmp_path):
    general_path = _write_xlsx(tmp_path, "jinshi.xlsx", _general())

    data = loader.load_jinshi_data(general_path)

    assert len(data) == 4
    assert data["EntryRank"].notna().all()


def test_load_jinshi_important_keeps_first_and_second_class(tmp_path):
    general_path = _write_xlsx(tmp_path, "jinshi.xlsx", _general())

    important = loader.load_jinshi_important(general_path)

    assert len(important) == 2
    assert important["level"].tolist() == [1, 2]
    assert important["EntryYear"].notna().all()


def test_merge_level_city_selects_expected_columns(tmp_path):
    levels = pd.DataFrame(
        {"year": [1500, 1501], "code": [1, 2], "level": [2, 3], "extra": ["x", "y"]}
    )
    cities = pd.DataFrame(
        {"code": [1, 2], "x": [110.0, 120.0], "y": [30.0, 40.0], "name": ["a", "b"]}
    )
    level_path = _write_xlsx(tmp_path, "levels_select.xlsx", levels)
    city_path = _write_xlsx(tmp_path, "cities_select.xlsx", cities)

    result = loader.merge_level_city(level_path, city_path)

    assert list(result.columns) == ["year", "code", "level", "x", "y"]
    assert result["code"].tolist() == [1, 2]


def test_load_extended_zaihuang_inner_joins_and_renames(tmp_path):
    city_path = _write_xlsx(tmp_path, "cities_ext.xlsx", _cities())
    ext = pd.DataFrame(
        {"year": [1500.0, 1500.0, 1501.0], "code": [1, 3, 2], "level": [2, 4, 5]}
    )
    ext_path = _write_xlsx(tmp_path, "ext_zaihuang.xlsx", ext)

    merged = loader.load_extended_zaihuang(city_path, ext_path)

    assert len(merged) == 2  # code 3 has no city coordinates
    assert {"year", "code", "level", "X", "Y"} <= set(merged.columns)
    assert "x" not in merged.columns and "y" not in merged.columns
    assert merged["year"].dtype.kind == "i"
    assert merged["X"].tolist() == [110.0, 120.0]


def test_load_extended_jinshi_filters_and_casts(tmp_path):
    ext_path = _write_xlsx(tmp_path, "ext_jinshi.xlsx", _general())

    result = loader.load_extended_jinshi(ext_path)

    assert list(result.columns) == ["EntryYear", "X", "Y", "level", "EntryRank"]
    assert len(result) == 2
    assert result["level"].tolist() == [1, 2]
    assert result["EntryYear"].dtype.kind == "i"


def test_save_processed_writes_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(loader, "DATA_PROCESSED_DIR", tmp_path)
    data = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    path = loader.save_processed(data, "sample.csv")

    assert path == str(tmp_path / "sample.csv")
    written = pd.read_csv(path)
    pd.testing.assert_frame_equal(written, data)


def test_missing_workbook_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        loader.load_jinshi_data(tmp_path / "does-not-exist.xlsx")
