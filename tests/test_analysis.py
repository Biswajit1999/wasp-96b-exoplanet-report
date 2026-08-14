"""Executable checks on the weighted-mean statistic and a regression
guard that the pipeline still reproduces the documented headline
numbers when run on the real downloaded data."""

import csv

import numpy as np
import analyze_spectrum as spec


def test_weighted_mean_matches_hand_computed_case():
    values = np.array([1.0, 2.0])
    errors = np.array([1.0, 0.5])  # weights 1 and 4
    mean, err = spec.weighted_mean(values, errors)
    assert np.isclose(mean, 1.8, rtol=1e-10)
    assert np.isclose(err, np.sqrt(1.0 / 5.0), rtol=1e-10)


def test_weighted_mean_reduces_to_plain_mean_for_equal_errors():
    values = np.array([2.0, 4.0, 6.0])
    errors = np.full(3, 0.5)
    mean, _ = spec.weighted_mean(values, errors)
    assert np.isclose(mean, values.mean())


def test_pipeline_reproduces_documented_headline_numbers():
    spec.FIG_DIR.mkdir(exist_ok=True)
    spec.main()
    rows = {}
    with (spec.FIG_DIR / "summary_statistics.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["quantity"]] = row["value"]
    assert int(rows["soss_n_wavelength_bins"]) == 79
    assert abs(float(rows["soss_weighted_mean_depth"]) - 14155.92) < 0.1
    assert abs(float(rows["limb_diff_significance"]) - 0.04) < 0.01
