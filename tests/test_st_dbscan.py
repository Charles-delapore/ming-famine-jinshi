"""Tests for the spatio-temporal DBSCAN wrapper in ``src.algorithms.st_dbscan``."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.algorithms.st_dbscan import STDBSCANExtended, cluster_zaihuang_st


def _points():
    """Columns are (time, x, y, level), as expected by ``fit``."""
    return np.array(
        [
            [1500, 0.0, 0.0, 1],
            [1500, 0.2, 0.1, 1],
            [1500, 10.0, 10.0, 1],
            [1500, 10.2, 10.1, 1],
            [1501, 0.1, 0.0, 2],
            [1502, 20.0, 20.0, 5],
        ],
        dtype=float,
    )


PARAMS = {
    "eps1": 1.0,
    "eps2": 2,
    "eps3": 1,
    "min_samples": 2,
}


def test_constructor_stores_parameters():
    model = STDBSCANExtended(eps1=0.3, eps2=2, eps3=1, min_samples=3, n_jobs=1)

    assert model.eps1 == 0.3
    assert model.eps2 == 2
    assert model.eps3 == 1
    assert model.min_samples == 3
    assert model.n_jobs == 1


def test_fit_smoke_test_and_label_shape():
    model = STDBSCANExtended(**PARAMS)

    returned = model.fit(_points())

    assert returned is model
    assert model.labels_.shape == (len(_points()),)
    assert model.labels_.dtype.kind == "i"
    assert model.labels_.max() < len(_points())
    # The two nearby points in the first cell share a cluster.
    assert model.labels_[0] == model.labels_[1]
    assert model.labels_[0] != -1
    # The isolated point is noise.
    assert model.labels_[-1] == -1


def test_fit_is_deterministic():
    first = STDBSCANExtended(**PARAMS).fit(_points()).labels_
    second = STDBSCANExtended(**PARAMS).fit(_points()).labels_

    np.testing.assert_array_equal(first, second)


def test_cluster_zaihuang_st_adds_cluster_column():
    data = pd.DataFrame(
        {
            "year": _points()[:, 0],
            "x": _points()[:, 1],
            "y": _points()[:, 2],
            "level": _points()[:, 3],
        }
    )

    clustered, model = cluster_zaihuang_st(data.copy(), PARAMS)

    assert "cluster" in clustered.columns
    assert len(clustered) == len(data)
    np.testing.assert_array_equal(clustered["cluster"].values, model.labels_)
