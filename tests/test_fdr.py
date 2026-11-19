"""Tests for the FDR helper used across the grid models."""

import numpy as np

from src.analysis.grid_analysis import fdr_correction


def test_known_bh_decisions():
    p = np.array([0.001, 0.01, 0.02, 0.5])
    sig, q = fdr_correction(p, alpha=0.05)
    assert sig.tolist() == [True, True, True, False]
    assert np.all(q[:3] <= 0.05)
    assert q[3] > 0.05


def test_empty_input():
    sig, q = fdr_correction(np.array([]), alpha=0.05)
    assert len(sig) == 0
    assert len(q) == 0


def test_no_discoveries():
    p = np.array([0.9, 0.8, 0.7])
    sig, _ = fdr_correction(p, alpha=0.05)
    assert not sig.any()
