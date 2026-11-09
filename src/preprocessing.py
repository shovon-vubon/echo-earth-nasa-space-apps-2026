"""Calendar-aware completeness screening; no imputation."""
import calendar
import numpy as np
import pandas as pd


def annualize(daily, start, end):
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start > end:
        raise ValueError("Start date must precede end date.")
    data = daily.copy().set_index("date")
    data.index = pd.to_datetime(data.index)
    if data.index.has_duplicates:
        raise ValueError("Duplicate daily dates are not supported.")
    data = data.reindex(pd.date_range(start, end, freq="D"))
    data["temperature_c"] = pd.to_numeric(data["temperature_c"], errors="coerce")
    data.loc[~np.isfinite(data.temperature_c), "temperature_c"] = np.nan
    rows = []
    for year in range(start.year, end.year + 1):
        expected = 366 if calendar.isleap(year) else 365
        full = start <= pd.Timestamp(year, 1, 1) and end >= pd.Timestamp(year, 12, 31)
        values = data.loc[data.index.year == year, "temperature_c"]
        count = int(values.count())
        month_coverage = [int(values.loc[values.index.month == m].count()) / calendar.monthrange(year, m)[1]
                          for m in range(1, 13)]
        reason = "included"
        if not full:
            reason = "partial calendar year"
        elif count / expected < .90:
            reason = "less than 90% of daily values valid"
        elif min(month_coverage) < .80:
            reason = "at least one month below 80% completeness"
        rows.append(dict(year=year, mean_temperature_c=values.mean(), valid_days=count,
                         expected_days=expected, completeness=count / expected,
                         minimum_month_completeness=min(month_coverage),
                         included=reason == "included", reason=reason))
    return pd.DataFrame(rows)
