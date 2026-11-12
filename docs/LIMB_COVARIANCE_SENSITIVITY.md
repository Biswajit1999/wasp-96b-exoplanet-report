# Limb-asymmetry covariance sensitivity

Two diagnostics extend the retained WASP-96 b archive audit.

1. **Assumed inter-limb correlation sweep.** For each wavelength bin, the variance of evening-minus-morning radius ratio is sigma_evening² + sigma_morning² − 2 rho sigma_evening sigma_morning. The joint morning/evening covariance is not released; rho is an illustrative sensitivity parameter, not a measured correlation.
2. **Wavelength-dependent shape fit.** Fit an intercept and linear slope of evening-minus-morning radius ratio, using diagonal errors derived from the assumed rho. The slope separates a first-order spectral shape from a constant timing-related offset, but is not a molecular feature retrieval.

Run `pytest -q tests/test_limb_robustness.py`. These are synthetic numerical tests, not new measurements. Existing observational figures and published injection/recovery significance are not replaced. Inter-bin covariance, time-domain fitting, reduction systematics, and the joint posterior remain unavailable. AI-assisted coding was used; Biswajit Jana is the requested Git author.
