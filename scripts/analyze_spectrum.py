"""Analyze real JWST data for WASP-96 b: a transmission spectrum (NIRISS SOSS)
and a morning/evening terminator (limb) asymmetry measurement (NIRSpec G395H).

Data source: Zenodo record 10.5281/zenodo.17065171, "Supplementary
Information for Super-Solar Metallicity and Tentative Evidence for
Photochemistry on WASP-96 b from JWST and Ground-Based VLT Transmission
Spectroscopy", files under Transmission_Spectra/. Retrieved directly from
Zenodo; both CSVs are reproduced unmodified in data/.

This script performs two independent, real analyses:
1. The NIRISS SOSS transmission spectrum: weighted mean transit depth and
   scatter, same diagnostic as any single-visit transmission spectrum.
2. The NIRSpec G395H morning-vs-evening (limb) asymmetry: whether the
   planet's leading and trailing terminators show a statistically
   significant difference in Rp/R*, which would indicate real day-to-night
   atmospheric circulation effects rather than a spherically symmetric
   atmosphere.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIG_DIR = Path(__file__).resolve().parents[1] / "figures"


def load_csv(path: Path) -> list[dict[str, float]]:
    rows = []
    with path.open() as handle:
        reader = csv.reader(line for line in handle if not line.startswith("#"))
        header = next(reader)
        for line in reader:
            if not line:
                continue
            rows.append({key: float(value) for key, value in zip(header, line)})
    return rows


def weighted_mean(values: np.ndarray, errors: np.ndarray) -> tuple[float, float]:
    weights = 1.0 / errors**2
    mean = np.sum(values * weights) / np.sum(weights)
    mean_error = np.sqrt(1.0 / np.sum(weights))
    return mean, mean_error


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)

    soss_rows = load_csv(DATA_DIR / "niriss_soss_transmission_spectrum_R50.csv")
    wave = np.array([r["wave"] for r in soss_rows])
    dppm = np.array([r["dppm"] for r in soss_rows])
    dppm_err = np.array([r["dppm_err"] for r in soss_rows])
    order = np.argsort(wave)
    wave, dppm, dppm_err = wave[order], dppm[order], dppm_err[order]
    mean_depth, mean_depth_error = weighted_mean(dppm, dppm_err)
    amplitude = dppm.max() - dppm.min()
    amplitude_wavelength = wave[dppm.argmax()]

    limb_rows = load_csv(DATA_DIR / "nirspec_g395h_transmission_spectrum_R50.csv")
    lwave = np.array([r["wave"] for r in limb_rows])
    morning = np.array([r["rprs_morning"] for r in limb_rows])
    morning_err = np.array([r["rprs_err_morning"] for r in limb_rows])
    evening = np.array([r["rprs_evening"] for r in limb_rows])
    evening_err = np.array([r["rprs_err_evening"] for r in limb_rows])
    order2 = np.argsort(lwave)
    lwave, morning, morning_err = lwave[order2], morning[order2], morning_err[order2]
    evening, evening_err = evening[order2], evening_err[order2]

    diff = evening - morning
    diff_err = np.sqrt(evening_err**2 + morning_err**2)
    mean_diff, mean_diff_error = weighted_mean(diff, diff_err)
    diff_significance_sigma = abs(mean_diff) / mean_diff_error

    summary_path = FIG_DIR / "summary_statistics.csv"
    with summary_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["soss_n_wavelength_bins", len(wave), "count"])
        writer.writerow(["soss_weighted_mean_depth", f"{mean_depth:.2f}", "ppm"])
        writer.writerow(["soss_weighted_mean_depth_error", f"{mean_depth_error:.2f}", "ppm"])
        writer.writerow(["soss_peak_to_trough_amplitude", f"{amplitude:.1f}", "ppm"])
        writer.writerow(["soss_amplitude_wavelength", f"{amplitude_wavelength:.3f}", "micron"])
        writer.writerow(["limb_n_wavelength_bins", len(lwave), "count"])
        writer.writerow(["limb_mean_evening_minus_morning_rprs", f"{mean_diff:.6f}", "Rp/R*"])
        writer.writerow(["limb_mean_diff_error", f"{mean_diff_error:.6f}", "Rp/R*"])
        writer.writerow(["limb_diff_significance", f"{diff_significance_sigma:.2f}", "sigma"])

    fig, (ax_spec, ax_limb) = plt.subplots(1, 2, figsize=(12, 5))

    colors = {2: "#1f6f5c", 1: "#c0562a"}
    for ord_id, color in colors.items():
        mask = np.array([r["order"] == ord_id for r in sorted(soss_rows, key=lambda r: r["wave"])])
        ax_spec.errorbar(
            wave[mask], dppm[mask], yerr=dppm_err[mask],
            fmt="o", ms=3.5, color=color, ecolor=color, alpha=0.85, elinewidth=1,
            label=f"SOSS order {ord_id}",
        )
    ax_spec.axhline(mean_depth, color="#555555", lw=1, ls="--", label="weighted mean")
    ax_spec.set_xlabel("Wavelength [micron]")
    ax_spec.set_ylabel("Transit depth (Rp/R*)^2 [ppm]")
    ax_spec.set_title("WASP-96 b transmission spectrum\n(JWST NIRISS SOSS, real reduced data)")
    ax_spec.legend(fontsize=8, frameon=False)
    ax_spec.grid(alpha=0.25)

    ax_limb.errorbar(lwave, morning, yerr=morning_err, fmt="o", ms=4, color="#2c5f8a", label="morning limb")
    ax_limb.errorbar(lwave, evening, yerr=evening_err, fmt="o", ms=4, color="#c0562a", label="evening limb")
    ax_limb.set_xlabel("Wavelength [micron]")
    ax_limb.set_ylabel("Rp/R*")
    ax_limb.set_title(
        f"Morning vs. evening terminator (JWST NIRSpec G395H)\n"
        f"mean evening-morning diff = {diff_significance_sigma:.1f} sigma"
    )
    ax_limb.legend(fontsize=8, frameon=False)
    ax_limb.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "wasp96b_spectrum_and_limb_asymmetry.png", dpi=200)
    print(f"Wrote {summary_path}")
    print(f"Wrote {FIG_DIR / 'wasp96b_spectrum_and_limb_asymmetry.png'}")
    print(
        f"SOSS: n={len(wave)}, mean depth={mean_depth:.1f}+/-{mean_depth_error:.1f} ppm, "
        f"amplitude={amplitude:.0f} ppm"
    )
    print(
        f"Limb asymmetry: mean evening-morning Rp/R* diff = {mean_diff:.5f} +/- "
        f"{mean_diff_error:.5f} ({diff_significance_sigma:.1f} sigma)"
    )


if __name__ == "__main__":
    main()
