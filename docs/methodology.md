# Trend method, version 1.0

## Preprocessing

1. Validate the NASA JSON schema and Celsius unit. Convert the response's own fill value, nonfinite values and missing dates to missing values. Reindex to every requested UTC day. No interpolation, imputation, extrapolation, or invented observations.
2. Compute daily completeness over the entire requested interval (including partial endpoint years).
3. For each calendar year, retain its mean only for trend fitting if the full year was requested, at least 90% of its 365/366 days are valid, and every month has at least 80% valid days. These thresholds are conservative project choices, not NASA-prescribed quality flags. All annual rows, counts and exclusion reasons remain visible and downloadable. No additional product-level quality flags are applied.
4. Take the arithmetic mean of valid daily temperatures, weighting days equally. Annual aggregation reduces seasonal-cycle confounding; the month screen avoids a nearly complete year missing an entire season. It does not eliminate missingness bias, detect seasonal trends, or preserve heat/rainfall extremes.
5. Require at least 10 accepted years for inference. This is an application guardrail, not a guarantee of statistical power; warn below 20. Actual calendar-year spacing is used, so missing years are not compressed.

## Mann–Kendall

For ordered annual means, S = sum over i<j of sign(y_j - y_i).
Under the null, tie-adjusted Var(S) = [n(n-1)(2n+5) - sum t(t-1)(2t+5)] / 18, where each t is a tied-value group size.
Use continuity correction Z = (S-sign(S))/sqrt(Var(S)); for S=0 or zero variance use Z=0. Two-sided p = 2 normal_survival(abs(Z)). Alpha is 0.05. This is the classical asymptotic test, not an exact small-sample, seasonal or modified Mann–Kendall test.

Reference: [USGS, Statistical Methods in Water Resources, chapter on trends](https://pubs.usgs.gov/tm/04/a03/tm4a3.pdf).

## Theil–Sen

Use `scipy.stats.theilslopes(y, actual_year, alpha=0.95)`: median of pairwise slopes, default separate median-based intercept, and rank-based 95% slope confidence limits. Report °C/year and °C/decade. The interval covers slope, not future temperature or flood probability.

Reference: [SciPy theilslopes](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html).

## Inference limitations

- Both p-values and slope intervals assume independence; **no serial-correlation correction or block bootstrap is implemented**. Detrend with the fitted Theil–Sen line and display lag-1 Pearson correlation using only adjacent calendar-year residual pairs. Undefined correlations (constant residuals or too few pairs) are reported as undefined. This is a descriptive diagnostic, not a passed independence test. Results always carry an exploratory-inference notice.
- Only one series is tested per analysis. Searching repeatedly across places or dates still produces multiple comparisons. No family-wise or false-discovery-rate correction is applied. Do not select only significant results or claim a validated significance map.
- Annual averaging hides seasonal changes and extremes; monotonic methods may miss reversals and abrupt changes. The selected period affects results. Reanalysis uncertainty and structural changes in the observing system are not propagated into the slope interval.
- Statistical association/significance is not causal attribution. A temperature trend cannot establish the cause of waterlogging or predict a particular flood.
- There is no trained hazard model. No current conditions, issue-time forecast archive, event labels or calibrated probabilities are available in this release.

## Reproducibility

Retain the daily and annual CSVs, original NASA JSON and analysis/provenance JSON. Records include requested location/time range, accepted/excluded annual values, completeness, source metadata and processing version. In synthetic mode every export identifies the synthetic source. Fixed seed 42 makes the demonstration reproducible, but synthetic outputs are not scientific findings.
