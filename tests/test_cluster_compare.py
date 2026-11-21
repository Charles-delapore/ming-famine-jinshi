"""Tests for the pure helpers in ``src.analysis.cluster_compare``.

Only small deterministic helpers are exercised; the permutation tests are kept
at a handful of shuffles or short-circuited through their early-return paths.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.analysis import cluster_compare


def test_calculate_lagged_similarity_identical_ranges():
    # Float bounds keep the helper's internal arrays floating point (integer
    # bounds hit a NumPy 2 casting issue in the module's in-place divide).
    params = (1500.0, 1509.0, 0.0, 10.0, 0.0, 10.0)

    similarity, lag = cluster_compare.calculate_lagged_similarity(
        params, params, max_lag=2
    )

    assert similarity == pytest.approx(1.0)
    assert lag == 0


def test_calculate_lagged_similarity_disjoint_space():
    z_params = (1500.0, 1509.0, 0.0, 10.0, 0.0, 10.0)
    j_params = (1500.0, 1509.0, 20.0, 30.0, 20.0, 30.0)

    similarity, lag = cluster_compare.calculate_lagged_similarity(
        z_params, j_params, max_lag=2, time_weight=0.7, space_weight=0.3
    )

    # Time overlaps perfectly at lag 0, but the spatial ranges do not overlap.
    assert similarity == pytest.approx(0.7)
    assert lag == 0


def test_calculate_lagged_similarity_detects_shifted_overlap():
    z_params = (1500.0, 1509.0, 0.0, 10.0, 0.0, 10.0)
    j_params = (1505.0, 1514.0, 0.0, 10.0, 0.0, 10.0)

    similarity, lag = cluster_compare.calculate_lagged_similarity(
        z_params, j_params, max_lag=5
    )

    assert similarity == pytest.approx(1.0)
    assert lag == 5


def test_build_cluster_time_series_counts_rows_and_sums_values():
    cluster = pd.DataFrame({"year": [1500, 1500, 1502], "level": [1, 2, 4]})

    years, counts = cluster_compare._build_cluster_time_series(
        cluster, "year", "missing_column", (1500, 1503)
    )
    assert years.tolist() == [1500, 1501, 1502, 1503]
    assert counts.tolist() == [2, 0, 1, 0]

    years, levels = cluster_compare._build_cluster_time_series(
        cluster, "year", "level", (1500, 1503)
    )
    assert years.tolist() == [1500, 1501, 1502, 1503]
    assert levels.tolist() == [3, 0, 4, 0]


def test_cross_correlation_perfect_and_constant_series():
    series = np.array([0, 1, 2, 3, 4, 5, 4, 3, 2, 1], dtype=float)

    corr, lag = cluster_compare._cross_correlation(series, series, max_lag=2)
    assert corr == pytest.approx(1.0)
    assert lag == 0

    corr, lag = cluster_compare._cross_correlation(series, np.ones(10), max_lag=2)
    assert corr == 0.0
    assert lag == 0

    corr, lag = cluster_compare._cross_correlation(np.arange(3), np.arange(3), max_lag=2)
    assert corr == 0.0
    assert lag == 0


def test_toroidal_shift_wraps_around():
    values = np.array([0.5, 1.5])

    shifted = cluster_compare._toroidal_shift(values, 1.0, 0.0, 2.0)
    np.testing.assert_allclose(shifted, [1.5, 0.5])

    shifted = cluster_compare._toroidal_shift(np.array([0.5]), 3.0, 0.0, 2.0)
    np.testing.assert_allclose(shifted, [1.5])

    # A degenerate span leaves the values shifted but unwrapped.
    shifted = cluster_compare._toroidal_shift(np.array([0.5]), 3.0, 1.0, 1.0)
    np.testing.assert_allclose(shifted, [3.5])


def test_causal_relationship_test_short_groups():
    z_group = pd.DataFrame({"year": [1500, 1501, 1502], "x": [0, 1, 2], "y": [0, 1, 2]})
    j_group = pd.DataFrame(
        {"EntryYear": [1500, 1501, 1502], "X": [0, 1, 2], "Y": [0, 1, 2]}
    )

    result = cluster_compare.causal_relationship_test(
        j_group, z_group, n_permutations=5, max_lag=2
    )

    assert result == (0.0, 0, 1.0, 0.0, 1.0)


def test_grid_permutation_test_returns_empty_without_events():
    grid_data = pd.DataFrame(
        {
            "year": [1500, 1501],
            "grid_x": [0, 0],
            "grid_y": [0, 0],
            "zaihuang_level": [0, 0],
            "zaihuang_severity": [0.0, 0.0],
            "jinshi_count": [0, 0],
        }
    )

    result = cluster_compare.grid_permutation_test(grid_data, n_permutations=5)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_process_cluster_pair_short_groups_returns_neutral_result():
    j_group = pd.DataFrame(
        {"EntryYear": [1500, 1501, 1502], "X": [0, 1, 2], "Y": [0, 1, 2]}
    )
    z_group = pd.DataFrame({"year": [1500, 1501, 1502], "x": [0, 1, 2], "y": [0, 1, 2]})
    params = {
        "n_permutations": 5,
        "time_weight": 0.7,
        "space_weight": 0.3,
    }

    result = cluster_compare._process_cluster_pair(
        ("j1", j_group, "z1", z_group, params)
    )

    assert result["jinshi_cluster"] == "j1"
    assert result["zaihuang_cluster"] == "z1"
    assert result["max_similarity"] == 0.0
    assert result["p_value"] == 1.0
