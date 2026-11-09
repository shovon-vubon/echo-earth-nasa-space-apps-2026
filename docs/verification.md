# First-release verification

Verified 2026-11-10 (Asia/Dhaka).

- `python -m pytest -q`: **9 passed**. Covers known positive/negative/constant trends, tied values, excluded years, actual-year gaps, leap years, incomplete months/years, NASA fill values and unit/schema checks, unsupported questions, demo interaction, selection invalidation, short/reversed periods, and source failure with no synthetic fallback.
- `python scripts/smoke_nasa.py`: successful live NASA POWER request for Mirpur/Dhaka (23.8223 N, 90.3654 E), 2001-01-01 through 2024-12-31. 8,766/8,766 valid daily values; 24 accepted annual means.
- Replayed that retrieved NASA response through Streamlit AppTest: no exceptions; metrics, result text, chart and download controls generated. No manual browser visual inspection was performed.
- `git diff --check`: passed.

Retrieved at `2026-11-09T18:06:06.879106+00:00`. API header identifies POWER Daily API v2.10.3, source `MERRA2`, time standard UTC and T2M units `C`.
Original HTTP response SHA-256: `b61d4d457e9efe1bd0fb7e441cd34332ef70b9daac2d961cf60dd743b702678d`.

Observed smoke-test result (not a bundled default or fabricated example): slope +0.00385246 °C/year, 95% slope interval −0.01477017 to +0.02446825 °C/year; unadjusted two-sided Mann–Kendall p=0.63743818. This interval and test do not establish a statistically significant monotonic trend. Serial dependence and multiple testing are not corrected; see methodology.md. Future NASA revisions or different selections may change the result.

The development host blocks Arrow's native DLL under Windows Application Control, including outside the command sandbox. The app therefore provides an escaped HTML-table fallback, without changing security settings. Both the synthetic UI test and NASA replay passed using this fallback. Real retrieval requires network access; the command sandbox's network restriction was handled with an approved external request.
