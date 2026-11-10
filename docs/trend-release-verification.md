# Trend-focused release verification

2026-11-10, Asia/Dhaka.

## Offline and interaction checks

15 automated tests pass. Scientific cases cover known slopes, flat series, tied values, missing years and dates, missing-value markers, completeness thresholds and MODIS QA/scaling. Upload cases cover Kelvin conversion, duplicate dates, out-of-range NDVI, monthly screening and maximum size. Streamlit AppTest covers variable switching, stale-result invalidation, source failure, unsupported questions, globe-button navigation and a CSV upload through mapping to a result.

## Real source checks

NASA POWER TS and PRECTOTCORR were retrieved for Mirpur/Dhaka, 2010-2024, each with 5,479/5,479 valid daily values and 15 accepted years. Both real responses were replayed through the revised UI successfully. Results are local verification evidence, not bundled default data:

| Variable | Slope | 95% slope interval | Unadjusted p |
|---|---|---|---|
| TS | -0.04387445 Celsius/year | -0.09218921 to +0.01377962 | 0.11328721 |
| PRECTOTCORR | +0.24806262 (mm/day)/year | +0.11047717 to +0.44097979 | 0.00753317 |

These p-values do not correct serial correlation or repeated comparisons. The precipitation residual lag-1 correlation was about 0.306. These are not causal findings or forecasts; dependence can affect inference.

MODIS `/bands`, `/dates`, `/products` and small real `/subset` responses were checked. A real 2015 ten-composite batch returned eight accepted pixels under the documented reliability 0/1 filter. A long-record request encountered a NASA 504 gateway timeout; the retry run also progressed slowly. **A complete multi-year NDVI trend retrieval has not been verified.** The app exposes the adapter with progress, bounded retries, 24-hour public-batch cache, explicit errors, and a CSV alternative. It never produces a trend unless ten annual aggregates pass quality screening. This source-availability limitation is visible in the interface.

The resumed long-record MODIS verification reached 35% (eight ten-date batches) before DNS resolution failed. The canonical host returned in NASA metadata also failed DNS resolution. Successful public responses remain cached. The adapter now limits each invocation with a 120-second request budget checked between attempts; users can repeat Analyze to reuse those batches. No partial long-record trend is returned on failure.

The local Streamlit health endpoint responds `ok`. Browser/native-app inspection was unavailable (no connected browser and native computer-use pipe unavailable), so globe animation, map rendering and pointer interactions have not been manually verified. Their navigation fallback is covered by AppTest; no pixel-perfect browser QA is claimed.

Public-response verification files live under ignored `data/cache/`. The original proposal, first-release README and first-release app source are preserved under `docs/`. No uploaded private file or credential is committed.
