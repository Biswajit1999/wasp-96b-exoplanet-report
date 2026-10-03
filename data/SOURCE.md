# Data provenance

The 12 CSV files in `transmission_products/` are copied without numeric
modification from `WASP-96b_Zenodo.zip`, Zenodo record
[17065171](https://doi.org/10.5281/zenodo.17065171), version 1. The archive was
published 2026-02-21 with MD5 `c98b29919fd81681dd510e08655b98a4`.

The subset contains:

- NIRISS/SOSS symmetric spectra at R=50, R=100, R=300, and two-pixel sampling;
- NIRSpec/G395H NRS1 and NRS2 symmetric spectra at R=100, R=300, and native
  pixel sampling;
- NIRISS and NIRSpec R=50 asymmetric `catwoman` morning/evening fits.

The symmetric products contain wavelength, bin half-width, transit depth in
ppm, uncertainty, and—where relevant—SOSS order. Missing detector-edge bins
are preserved as blank values. The asymmetric products contain the archived
morning/evening hemisphere parameters and marginal uncertainties.

`source_manifest.json` records the archive MD5 and a newline-canonical SHA-256
digest over every filename and text record in this 12-file subset. Verify it with
`python scripts/validate_sources.py`.
