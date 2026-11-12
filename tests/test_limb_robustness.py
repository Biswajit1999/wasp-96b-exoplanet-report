"""Synthetic regression tests for conditional limb covariance."""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))
from limb_robustness import limb_difference_covariance, weighted_limb_shape

def test_difference_variance():
    assert np.allclose(limb_difference_covariance([2, 2], [3, 3], .5), [7, 7])

def test_linear_recovery():
    w = np.linspace(1, 2, 20)
    m = np.ones(20) * .1
    e = m + .003 + .002 * (w-w.mean())
    for rho in (-.3, 0, .7):
        out = weighted_limb_shape(w, m, e, np.ones(20)*.001, np.ones(20)*.002, rho)
        assert out["intercept"] == pytest.approx(.003, abs=1e-12)
        assert out["slope_per_micron"] == pytest.approx(.002, abs=1e-12)
        assert out["diagonal_chi2"] < 1e-20

def test_correlation_sensitivity():
    w = np.linspace(1, 2, 20)
    z = np.zeros(20)
    s = np.ones(20)*.01
    assert weighted_limb_shape(w, z, z, s, s, .8)["slope_error"] < weighted_limb_shape(w, z, z, s, s)["slope_error"]

def test_invalid():
    with pytest.raises(ValueError):
        limb_difference_covariance([1, 1], [1, 1], 1)
    with pytest.raises(ValueError):
        weighted_limb_shape([1, 1, 2], [0]*3, [0]*3, [1]*3, [1]*3)
