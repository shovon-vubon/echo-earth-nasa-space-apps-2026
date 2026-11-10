# Landing page and grounded chat update

Verified 2026-11-10, Asia/Dhaka.

- 26 automated tests pass, covering the landing/workspace separation, navigation in both directions, variable and chat-state invalidation, uploads, source errors, dataset mapping, statistical cases, chat comparisons, uncertainty, missing records, excluded years, and unsupported causes/forecasts/locations/variables.
- The generated globe client passed JavaScript syntax checking. D3's orthographic projection places Bangladesh correctly at the viewport centre when focused. Its geometry and libraries are bundled locally; version URLs/hashes and licenses are in `assets/maps/`.
- The actual previously retrieved NASA POWER TS response for Sylhet, 2001–2024, was replayed through the new dashboard and chat interface. Both produce the same Mann–Kendall p-value, 0.5351853194. Chat endpoint comparisons and accumulated messages also completed without application exceptions. This verifies computation consistency, not universal dataset accuracy or causal validity.
- Daily aggregation now rejects duplicate timestamps and unsupported cadences and converts nonfinite values to missing. Existing seasonality, serial-correlation, multiple-comparison and reanalysis-uncertainty limitations remain explicit.
- There was no connected browser/native desktop for manual visual QA. Pointer interactions were not manually verified; navigation, chat and results were checked with Streamlit AppTest, plus globe client syntax/projection checks. No manual browser verification is claimed.

The current MODIS long-record service limitation remains unchanged; see `trend-release-verification.md`. The local server must be launched with permission for network access, otherwise Windows sandbox error 10013 blocks NASA requests.
