"""Validation and regression tests for the WASP-96 b evidence audit."""

import json

import analyze_spectrum as analysis
import numpy as np
import pytest


def test_weighted_mean_and_error_validation():
    mean, error = analysis.weighted_mean(np.array([1.0, 2.0]), np.array([1.0, 0.5]))
    assert mean == pytest.approx(1.8)
    assert error == pytest.approx(np.sqrt(0.2))
    with pytest.raises(ValueError, match="positive"):
        analysis.weighted_mean(np.array([1.0, 2.0]), np.array([0.1, 0.0]))


def test_archive_inventory_is_complete():
    inventory = analysis.resolution_inventory()
    assert len(inventory) == 12
    assert sum(row["kind"] == "asymmetric" for row in inventory) == 2
    assert sum(row["kind"] == "symmetric" for row in inventory) == 10


def test_limb_diagnostics_reproduce_archived_tables():
    niriss = analysis.load_csv(analysis.PRODUCT_DIR / analysis.NIRISS_LIMBS)
    nirspec = analysis.load_csv(analysis.PRODUCT_DIR / analysis.NIRSPEC_LIMBS)
    result_iss = analysis.limb_diagnostics(niriss)
    result_spec = analysis.limb_diagnostics(nirspec)
    assert result_iss["n_bins"] == 77
    assert result_iss["diagonal_mean_ratio"] == pytest.approx(-3.4017, abs=0.0002)
    assert result_spec["n_bins"] == 29
    assert result_spec["diagonal_mean_ratio"] == pytest.approx(0.03687, abs=0.00002)


def test_water_band_exposes_covariance_limit():
    niriss = analysis.load_csv(analysis.PRODUCT_DIR / analysis.NIRISS_LIMBS)
    result = analysis.band_amplitude(niriss, (1.35, 1.50), (0.90, 1.30))
    assert result["in_band_n"] == 5
    assert result["out_band_n"] == 18
    assert result["diagonal_delta_ratio"] == pytest.approx(0.78054, abs=0.00002)
    assert result["published_injection_recovery_significance_sigma"] == 2.6


def test_main_writes_structured_products():
    analysis.main()
    summary = json.loads((analysis.FIG_DIR / "analysis_summary.json").read_text(encoding="utf-8"))
    assert summary["archive_product_count"] == 12
    assert (analysis.FIG_DIR / "limb_differences.csv").is_file()
    assert (analysis.FIG_DIR / "resolution_inventory.csv").is_file()
