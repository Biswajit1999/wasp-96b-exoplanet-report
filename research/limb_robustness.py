"""Conditional wavelength-dependent limb-asymmetry diagnostics."""
import numpy as np

def limb_difference_covariance(morning_error, evening_error, correlation=0.0):
    """Per-bin evening-minus-morning variance for assumed cross-limb correlation."""
    m, e = np.asarray(morning_error, float), np.asarray(evening_error, float)
    if m.ndim != 1 or m.shape != e.shape or m.size < 2:
        raise ValueError("aligned uncertainty vectors required")
    if not np.all(np.isfinite(m)) or not np.all(np.isfinite(e)) or np.any(m <= 0) or np.any(e <= 0):
        raise ValueError("finite positive errors required")
    if not np.isfinite(correlation) or not -1 < correlation < 1:
        raise ValueError("correlation must lie between -1 and 1")
    return m*m + e*e - 2*correlation*m*e

def weighted_limb_shape(wavelength, morning, evening, morning_error, evening_error,
                        correlation=0.0):
    """Diagonal-bin GLS intercept and wavelength slope of evening-minus-morning."""
    w, m, e = (np.asarray(a, float) for a in (wavelength, morning, evening))
    variance = limb_difference_covariance(morning_error, evening_error, correlation)
    if any(a.shape != w.shape for a in (m, e, variance)) or w.size < 3:
        raise ValueError("at least three aligned bins required")
    if not all(np.all(np.isfinite(a)) for a in (w, m, e)) or np.any(np.diff(w) <= 0):
        raise ValueError("finite increasing wavelengths required")
    pivot = np.mean(w)
    x = np.column_stack((np.ones(w.size), w-pivot))
    a = x / np.sqrt(variance)[:, None]
    y = (e-m) / np.sqrt(variance)
    normal = a.T @ a
    if np.linalg.cond(normal) > 1e12:
        raise ValueError("ill-conditioned wavelength baseline")
    beta = np.linalg.solve(normal, a.T @ y)
    covariance = np.linalg.inv(normal)
    residual = y-a @ beta
    return {"pivot_micron": float(pivot), "intercept": float(beta[0]),
            "slope_per_micron": float(beta[1]),
            "intercept_error": float(np.sqrt(covariance[0, 0])),
            "slope_error": float(np.sqrt(covariance[1, 1])),
            "diagonal_chi2": float(residual @ residual), "dof": int(w.size-2)}
