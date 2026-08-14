# WASP-96 b — Exoplanet Atmosphere Report

<img src="images/thumbnail.png" alt="Artist's concept of WASP-96 b" width="360">

*AI-generated artist's concept — not a real photograph. See the report for actual JWST NIRISS SOSS and NIRSpec G395H data.*

The planet behind JWST's first published exoplanet spectrum (12 July 2022) —
a hot Saturn with a clear water-vapor signature. This repo works from
that reduced data, plus a morning/evening terminator asymmetry check
from a later study, and states plainly what each measurement can and
can't establish on its own.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## Data sources

- **System parameters** — from the NASA Exoplanet Archive TAP
  service (`pscomppars` table).
- **Two JWST spectra** — NIRISS SOSS transmission spectrum and NIRSpec
  G395H morning/evening limb Rp/R*, both released publicly on Zenodo
  ([10.5281/zenodo.17065171](https://doi.org/10.5281/zenodo.17065171)). See
  `data/` for the CSVs exactly as downloaded, headers included.
- **Analysis** — `scripts/analyze_spectrum.py` computes the weighted mean
  transit depth and peak-to-trough amplitude of the SOSS spectrum, and the
  statistical significance of any evening-minus-morning terminator
  difference in the NIRSpec data. Run it yourself:

  ```bash
  pip install -r requirements.txt
  python scripts/analyze_spectrum.py
  ```

## Repository structure

```text
index.html              the report webpage
data/                    reduced JWST NIRISS SOSS + NIRSpec G395H CSVs (Zenodo)
scripts/analyze_spectrum.py   analysis producing the figure + statistics
figures/                 generated plot + summary_statistics.csv
tests/                   unit tests + a regression check against the real data
```

## Tests

`tests/test_analysis.py` checks the weighted-mean formula against
hand-computed cases and reruns the full pipeline on the real
downloaded spectrum, verifying it still reproduces the numbers this
README documents. Runs automatically on every push via GitHub Actions;
run locally with:

```bash
pytest tests/ -v
```

## What the numbers show

- NIRISS SOSS: 79 wavelength bins, weighted mean depth 14156 ppm,
  peak-to-trough amplitude 1267 ppm, with a clear water-band rise near 1.4
  microns — the same feature announced in 2022.
- NIRSpec G395H: the evening-minus-morning terminator Rp/R* difference
  in this dataset is consistent with zero at the precision achieved here,
  matching the source study's own "tentative" framing rather than a
  confident asymmetry detection.

## Limitations

The morning and evening Rp/R* values come from the same observations
and fitting pipeline, so they can share stellar, instrumental, and
fitting covariance that a simple quadrature sum of their quoted per-bin
errors doesn't capture — this repo's asymmetry test is a first-order
diagnostic, not a full covariance-aware hypothesis test. The
peak-to-trough amplitude quoted for the transmission spectrum (1267
ppm) is also an extreme-value statistic with no uncertainty of its
own — the single largest gap between any two bins, more sensitive to
one noisy point than a proper feature measurement would be, reported
here descriptively rather than as a calibrated result.

## References

1. JWST Early Release Observations Team, 2022. Webb Reveals Steamy
   Atmosphere of Distant Planet in Detail. NASA press release, 12 July 2022.
2. Zenodo record
   [10.5281/zenodo.17065171](https://doi.org/10.5281/zenodo.17065171),
   "Super-Solar Metallicity and Tentative Evidence for Photochemistry on
   WASP-96 b from JWST and Ground-Based VLT Transmission Spectroscopy."
3. Hellier, C. et al., 2014. WASP-95b and WASP-96b: two new transiting
   close-in giant planets. *Monthly Notices of the Royal Astronomical
   Society*, 440(2), pp.1982-1992.
4. NASA Exoplanet Archive, <https://exoplanetarchive.ipac.caltech.edu/>.

## Author

Biswajit Jana — [Portfolio](https://biswajit1999.github.io/Biswajit_Jana.github.io/) · [GitHub](https://github.com/Biswajit1999) · [LinkedIn](https://www.linkedin.com/in/biswajit-jana-27011a151/) · [ORCID](https://orcid.org/0009-0002-2411-1891)
