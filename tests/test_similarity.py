"""Tests for the cluster-similarity helpers."""

import numpy as np
import pandas as pd

from src.analysis.similarity import space_iou, time_similarity, temporal_overlap_ratio


def test_time_similarity_overlap_and_disjoint():
    assert time_similarity(1500, 1510, 1505, 1515) == 6 / 11
    assert time_similarity(1500, 1504, 1510, 1514) == 0.0
    assert time_similarity(1500, 1500, 1500, 1500) == 1.0


def test_space_iou_cases():
    assert space_iou(0, 2, 0, 2, 0, 2, 0, 2) == 1.0
    assert space_iou(0, 1, 0, 1, 2, 3, 2, 3) == 0.0
    # two 2x2 boxes offset by one unit: intersection 1, union 7
    assert space_iou(0, 2, 0, 2, 1, 3, 1, 3) == 1 / 7


def test_temporal_overlap_ratio_dataframes():
    a = pd.DataFrame({"EntryYear": [1500, 1505, 1510]})
    b = pd.DataFrame({"year": [1505, 1506, 1507, 1511]})
    # overlap 1505-1510 = 6 years; max duration = 11
    assert temporal_overlap_ratio(a, b) == 6 / 11


def test_temporal_overlap_ratio_no_overlap():
    a = pd.DataFrame({"EntryYear": [1500, 1501]})
    b = pd.DataFrame({"year": [1600, 1601]})
    assert temporal_overlap_ratio(a, b) == 0.0


