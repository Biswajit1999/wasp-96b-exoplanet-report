# WASP-96 b — Exoplanet Atmosphere Report

The planet behind JWST's first published exoplanet spectrum (12 July 2022) —
a hot Saturn with a clear, unambiguous water-vapor signature. This repo
re-derives that historic result from the real reduced data, plus a real
morning/evening terminator asymmetry measurement from a later study.

**[Open the full report](index.html)** (open locally in a browser, or serve
with `python -m http.server` from this directory).

## What's real here

- **System parameters** — queried live from the NASA Exoplanet Archive TAP
  service (`pscomppars` table).
- **Two real JWST spectra** — NIRISS SOSS transmission spectrum and NIRSpec
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
data/                    real reduced JWST NIRISS SOSS + NIRSpec G395H CSVs (Zenodo)
scripts/analyze_spectrum.py   real analysis producing the figure + statistics
figures/                 generated plot + summary_statistics.csv
```

## Key findings this repo shows directly

- NIRISS SOSS: 79 real wavelength bins, weighted mean depth 14156 ppm,
  peak-to-trough amplitude 1267 ppm, with a clear water-band rise near 1.4
  microns — the same feature announced in 2022.
- NIRSpec G395H: the real evening-minus-morning terminator Rp/R* difference
  in this dataset is consistent with zero at the precision achieved here — a
  genuine null result, reported honestly rather than omitted, and consistent
  with the source study's own "tentative" framing.

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
