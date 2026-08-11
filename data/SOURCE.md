# Data source

Both CSVs are downloaded, unmodified except for filename, from Zenodo
record **10.5281/zenodo.17065171** ("Supplementary Information for
Super-Solar Metallicity and Tentative Evidence for Photochemistry on
WASP-96 b from JWST and Ground-Based VLT Transmission Spectroscopy"),
`Transmission_Spectra/` folder:

- `niriss_soss_transmission_spectrum_R50.csv` ← `WASP-96b_NIRISS_SOSS_transmission_spectrum_PriorLD_Slope_R50.csv`
- `nirspec_g395h_transmission_spectrum_R50.csv` ← `WASP-96b_NIRSpec_G395H_transmission_spectrum_FixLD_FixT0_Asymmetric_R50.csv`

Retrieved: 2026-08-11, via `https://zenodo.org/api/records/17065171`.

Each file retains its original header (commented lines starting with `#`)
describing the pipeline (exoTEDRF), light-curve fitting code (exoUPRF),
orbital fit parameters used, and column definitions.
