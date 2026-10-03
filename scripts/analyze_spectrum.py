"""Audit the public WASP-96 b JWST transmission-spectrum hierarchy.

The archive contains symmetric spectra at multiple resolutions and separate
catwoman morning/evening fits.  The latter have strongly coupled parameters;
the released marginal errors do not encode their covariance.  Accordingly,
all diagonal-error calculations here are diagnostics, while the source paper's
injection/recovery experiment remains the appropriate asymmetry result.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2 as chi2_dist

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PRODUCT_DIR = DATA_DIR / "transmission_products"
FIG_DIR = ROOT / "figures"

NIRISS_R50 = "WASP-96b_NIRISS_SOSS_transmission_spectrum_PriorLD_Slope_R50.csv"
NIRISS_LIMBS = "WASP-96b_NIRISS_SOSS_transmission_spectrum_FixLD_FixT0_Asymmetric_R50.csv"
NIRSPEC_LIMBS = "WASP-96b_NIRSpec_G395H_transmission_spectrum_FixLD_FixT0_Asymmetric_R50.csv"


def load_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(line for line in handle if not line.startswith("#"))
        rows = list(reader)
    if not rows or reader.fieldnames is None:
        raise ValueError(f"No tabular data in {path}")
    result = {
        key: np.asarray([float(row[key]) if row[key].strip() else np.nan for row in rows])
        for key in reader.fieldnames
    }
    if not np.all(np.isfinite(result["wave"])):
        raise ValueError(f"Non-finite wavelength in {path}")
    return result


def weighted_mean(values: np.ndarray, errors: np.ndarray) -> tuple[float, float]:
    if values.shape != errors.shape or values.size == 0:
        raise ValueError("values and errors must be non-empty and aligned")
    if np.any(~np.isfinite(values)) or np.any(~np.isfinite(errors)) or np.any(errors <= 0):
        raise ValueError("values must be finite and errors finite and positive")
    weights = errors**-2
    return float(np.sum(values * weights) / np.sum(weights)), float(np.sum(weights) ** -0.5)


def limb_diagnostics(table: dict[str, np.ndarray]) -> dict[str, float | int]:
    difference = table["rprs_evening"] - table["rprs_morning"]
    # This independence assumption is intentionally explicit and is not a
    # substitute for the unreleased joint morning/evening covariance.
    error = np.hypot(table["rprs_err_evening"], table["rprs_err_morning"])
    offset, offset_error = weighted_mean(difference, error)
    centered_chi2 = float(np.sum(((difference - offset) / error) ** 2))
    dof = difference.size - 1
    return {
        "n_bins": int(difference.size),
        "diagonal_mean_evening_minus_morning_rprs": offset,
        "diagonal_mean_error_rprs": offset_error,
        "diagonal_mean_ratio": offset / offset_error,
        "centered_shape_chi2": centered_chi2,
        "centered_shape_dof": dof,
        "centered_shape_reduced_chi2": centered_chi2 / dof,
        "centered_shape_p_value": float(chi2_dist.sf(centered_chi2, dof)),
        "difference_rms_rprs": float(np.sqrt(np.mean(difference**2))),
    }


def band_amplitude(table: dict[str, np.ndarray], in_band: tuple[float, float],
                   out_band: tuple[float, float]) -> dict[str, float | int]:
    wave = table["wave"]
    inside = (wave >= in_band[0]) & (wave <= in_band[1])
    outside = (wave >= out_band[0]) & (wave <= out_band[1])
    values: dict[str, float | int] = {
        "in_band_n": int(np.count_nonzero(inside)), "out_band_n": int(np.count_nonzero(outside))
    }
    amplitudes = {}
    for limb in ("morning", "evening"):
        depth = table[f"rprs_{limb}"]
        error = table[f"rprs_err_{limb}"]
        in_mean, in_error = weighted_mean(depth[inside], error[inside])
        out_mean, out_error = weighted_mean(depth[outside], error[outside])
        amplitudes[limb] = (in_mean - out_mean, float(np.hypot(in_error, out_error)))
        values[f"{limb}_amplitude_rprs"] = amplitudes[limb][0]
        values[f"{limb}_amplitude_error_rprs"] = amplitudes[limb][1]
    delta = amplitudes["evening"][0] - amplitudes["morning"][0]
    delta_error = float(np.hypot(amplitudes["evening"][1], amplitudes["morning"][1]))
    values.update({
        "diagonal_delta_amplitude_rprs": delta,
        "diagonal_delta_error_rprs": delta_error,
        "diagonal_delta_ratio": delta / delta_error,
        "published_delta_scale_heights": 2.13,
        "published_marginal_error_scale_heights": 0.31,
        "published_injection_recovery_significance_sigma": 2.6,
        "published_null_width_scale_heights": 0.72,
    })
    return values


def resolution_inventory() -> list[dict[str, object]]:
    rows = []
    for path in sorted(PRODUCT_DIR.glob("*.csv")):
        table = load_csv(path)
        kind = "asymmetric" if "rprs_morning" in table else "symmetric"
        row: dict[str, object] = {"file": path.name, "kind": kind, "n_bins": len(table["wave"]),
                                 "wave_min": float(table["wave"].min()),
                                 "wave_max": float(table["wave"].max())}
        if kind == "symmetric":
            valid = np.isfinite(table["dppm"]) & np.isfinite(table["dppm_err"])
            mean, error = weighted_mean(table["dppm"][valid], table["dppm_err"][valid])
            row.update({"n_valid_bins": int(np.count_nonzero(valid)),
                        "weighted_mean_dppm": mean, "weighted_mean_error_dppm": error})
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    inventory = resolution_inventory()
    if len(inventory) != 12:
        raise ValueError(f"Expected 12 transmission products, found {len(inventory)}")
    niriss = load_csv(PRODUCT_DIR / NIRISS_LIMBS)
    nirspec = load_csv(PRODUCT_DIR / NIRSPEC_LIMBS)
    niriss_diag = limb_diagnostics(niriss)
    nirspec_diag = limb_diagnostics(nirspec)
    water = band_amplitude(niriss, (1.35, 1.50), (0.90, 1.30))

    summary = {
        "source": "https://doi.org/10.5281/zenodo.17065171",
        "archive_product_count": 12,
        "niriss_limb_diagnostic": niriss_diag,
        "nirspec_limb_diagnostic": nirspec_diag,
        "niriss_water_band": water,
        "critical_limit": "released marginal limb errors omit joint covariance; diagonal ratios do not reproduce the source injection/recovery test",
        "published_interpretation": "2.6-sigma water-band asymmetry candidate; no conclusive limb-asymmetry evidence",
        "resolution_inventory": inventory,
    }
    (FIG_DIR / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_csv(FIG_DIR / "resolution_inventory.csv", inventory)

    limb_rows = []
    for instrument, table in (("NIRISS", niriss), ("NIRSpec", nirspec)):
        difference = table["rprs_evening"] - table["rprs_morning"]
        error = np.hypot(table["rprs_err_evening"], table["rprs_err_morning"])
        for wave, diff, uncertainty in zip(table["wave"], difference, error, strict=True):
            limb_rows.append({"instrument": instrument, "wavelength_micron": wave,
                              "evening_minus_morning_rprs": diff,
                              "diagonal_uncertainty_rprs": uncertainty})
    write_csv(FIG_DIR / "limb_differences.csv", limb_rows)

    with (FIG_DIR / "summary_statistics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["source_product_count", 12, "count"])
        writer.writerow(["niriss_diagonal_mean_difference", niriss_diag["diagonal_mean_evening_minus_morning_rprs"], "Rp/Rstar"])
        writer.writerow(["niriss_diagonal_mean_ratio", niriss_diag["diagonal_mean_ratio"], "sigma-like ratio"])
        writer.writerow(["nirspec_diagonal_mean_ratio", nirspec_diag["diagonal_mean_ratio"], "sigma-like ratio"])
        writer.writerow(["water_diagonal_delta_amplitude", water["diagonal_delta_amplitude_rprs"], "Rp/Rstar"])
        writer.writerow(["water_diagonal_delta_ratio", water["diagonal_delta_ratio"], "sigma-like ratio"])
        writer.writerow(["water_published_injection_recovery_significance", 2.6, "sigma"])

    soss = load_csv(PRODUCT_DIR / NIRISS_R50)
    nrs1 = load_csv(PRODUCT_DIR / "WASP-96b_NIRSpec_G395H_NRS1_transmission_spectrum_PriorLD_Slope_R100.csv")
    nrs2 = load_csv(PRODUCT_DIR / "WASP-96b_NIRSpec_G395H_NRS2_transmission_spectrum_PriorLD_Slope_R100.csv")
    plt.rcParams.update({"font.size": 9, "axes.titleweight": "bold", "figure.facecolor": "white"})
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.8), constrained_layout=True)
    ax = axes[0, 0]
    ax.errorbar(soss["wave"], soss["dppm"], yerr=soss["dppm_err"], fmt="o", ms=3,
                color="#0f766e", alpha=0.75, label="NIRISS/SOSS R=50")
    for table, label, color in ((nrs1, "NIRSpec NRS1 R=100", "#1d4ed8"),
                                (nrs2, "NIRSpec NRS2 R=100", "#7c3aed")):
        valid = np.isfinite(table["dppm"]) & np.isfinite(table["dppm_err"])
        ax.errorbar(table["wave"][valid], table["dppm"][valid], yerr=table["dppm_err"][valid], fmt="o", ms=3,
                    color=color, alpha=0.75, label=label)
    ax.set(title="A · Released 0.6–5.2 µm transmission spectrum",
           xlabel="Wavelength [µm]", ylabel="Transit depth [ppm]")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.18)

    for ax, table, title in ((axes[0, 1], niriss, "B · NIRISS morning/evening parameters"),
                             (axes[1, 0], nirspec, "C · NIRSpec morning/evening parameters")):
        ax.errorbar(table["wave"], table["rprs_morning"], yerr=table["rprs_err_morning"],
                    fmt="o", ms=3, color="#1d4ed8", alpha=0.65, label="Morning")
        ax.errorbar(table["wave"], table["rprs_evening"], yerr=table["rprs_err_evening"],
                    fmt="o", ms=3, color="#dc2626", alpha=0.55, label="Evening")
        ax.set(title=title, xlabel="Wavelength [µm]", ylabel="Archived hemisphere Rp/Rstar")
        ax.legend(fontsize=7.5)
        ax.grid(alpha=0.18)
    axes[0, 1].axvspan(1.35, 1.50, color="#38bdf8", alpha=0.14, label="H₂O in-band")
    axes[0, 1].axvspan(0.90, 1.30, color="#94a3b8", alpha=0.12, label="out-of-band")
    axes[0, 1].legend(fontsize=7.5, ncol=2)

    ax = axes[1, 1]
    for instrument, table, diagnostic, color in (("NIRISS", niriss, niriss_diag, "#0f766e"),
                                                  ("NIRSpec", nirspec, nirspec_diag, "#7c3aed")):
        diff = table["rprs_evening"] - table["rprs_morning"]
        err = np.hypot(table["rprs_err_evening"], table["rprs_err_morning"])
        centered = diff - float(diagnostic["diagonal_mean_evening_minus_morning_rprs"])
        ax.errorbar(table["wave"], centered, yerr=err, fmt="o", ms=3, color=color,
                    alpha=0.7, label=f"{instrument}; constant offset removed")
    ax.axhline(0, color="#64748b", ls=":")
    ax.set(title="D · Wavelength-dependent limb difference",
           xlabel="Wavelength [µm]", ylabel="Centered evening − morning Rp/Rstar")
    ax.legend(fontsize=7.5)
    ax.grid(alpha=0.18)
    fig.suptitle("WASP-96 b · spectrum hierarchy and limb-asymmetry audit", fontsize=15, fontweight="bold")
    fig.savefig(FIG_DIR / "wasp96b_spectrum_and_limb_asymmetry.png", dpi=220)
    plt.close(fig)

    print(f"Audited {len(inventory)} archive spectra")
    print(f"NIRISS constant limb offset diagonal ratio: {niriss_diag['diagonal_mean_ratio']:.2f}")
    print(f"NIRISS water-band diagonal ratio: {water['diagonal_delta_ratio']:.2f}; published injection/recovery: 2.6 sigma")
    print(f"NIRSpec constant limb offset diagonal ratio: {nirspec_diag['diagonal_mean_ratio']:.2f}")


if __name__ == "__main__":
    main()
