"""Variable definitions, common annual series, and no-code CSV validation."""
import hashlib
import io
import calendar
from datetime import date, timedelta
import numpy as np
import pandas as pd
from src.data import DataError

VARIABLES = {
    "Surface temperature": dict(code="TS", units="°C", minimum=-100, maximum=100,
        note="Earth skin temperature from MERRA-2 reanalysis. Over land this describes the surface, not air at 2 m. Coarse coastal cells may mix land and water; not a satellite thermal image."),
    "Rainfall / precipitation": dict(code="PRECTOTCORR", units="mm/day", minimum=0, maximum=3000,
        note="Corrected total precipitation, including liquid and frozen precipitation. Annual mean daily rate, not annual accumulation or a rainfall-extremes metric."),
    "Vegetation": dict(code="NDVI", units="NDVI", minimum=-.2, maximum=1,
        note="MODIS MOD13Q1 vegetation greenness index. NDVI is not a direct measure of forest cover, crop yield or biodiversity."),
    "Air temperature": dict(code="T2M", units="°C", minimum=-100, maximum=100,
        note="Air temperature at 2 metres, distinct from surface temperature."),
}


def read_csv(content):
    if len(content) > 10 * 1024 * 1024:
        raise DataError("CSV exceeds 10 MB. Upload one location and variable at a time.")
    try:
        frame = pd.read_csv(io.BytesIO(content))
    except (ValueError, UnicodeError) as exc:
        raise DataError(f"Cannot read CSV. Use a UTF-8, comma-separated file: {exc}") from exc
    if frame.empty or len(frame) > 100000:
        raise DataError("CSV must contain 1–100,000 rows.")
    return frame


def prepare_upload(frame, date_column, value_column, frequency, variable, units, missing, date_format):
    supported_units = {"Celsius", "Kelvin"} if VARIABLES[variable]["code"] in {"TS", "T2M"} else {VARIABLES[variable]["units"]}
    if units not in supported_units:
        raise DataError("Input units do not match the selected variable.")
    if date_column == value_column:
        raise DataError("Choose different date and value columns.")
    try:
        dates = pd.to_datetime(frame[date_column], format=date_format, errors="coerce")
    except (ValueError, TypeError) as exc:
        raise DataError("Dates could not be parsed using that format.") from exc
    if dates.isna().any():
        raise DataError(f"{dates.isna().sum()} date values are invalid. Fix them or select the matching format.")
    if frequency == "Daily":
        dates = dates.dt.normalize()
    elif frequency == "Monthly":
        dates = dates.dt.to_period("M").dt.to_timestamp()
    else:
        dates = dates.dt.to_period("Y").dt.to_timestamp()
    if dates.duplicated().any():
        raise DataError("Duplicate time periods found. Filter to one location and aggregate duplicate periods before uploading.")
    values = pd.to_numeric(frame[value_column], errors="coerce")
    if missing.strip():
        try:
            values = values.mask(values == float(missing))
        except ValueError as exc:
            raise DataError("Missing-value marker must be a number or blank.") from exc
    values = values.where(np.isfinite(values))
    if units == "Kelvin":
        values = values - 273.15
    spec = VARIABLES[variable]
    invalid = values.notna() & ((values < spec["minimum"]) | (values > spec["maximum"]))
    if invalid.any():
        raise DataError(f"{invalid.sum()} values outside the supported physical range. Check units, scale factors and missing-value marker.")
    if not values.notna().any():
        raise DataError("No valid numeric observations remain.")
    return pd.DataFrame({"date": dates, "value": values}).sort_values("date").reset_index(drop=True)


def aggregate(frame, start, end, frequency="Daily"):
    """Annual means; explicit expected cadence. Composite cadence is MODIS 16 days."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start > end:
        raise DataError("Start date must be on or before end date.")
    if frequency == "Daily":
        expected = pd.date_range(start, end, freq="D")
    elif frequency == "Monthly":
        expected = pd.date_range(start.replace(day=1), end, freq="MS")
    elif frequency == "Annual":
        expected = pd.date_range(f"{start.year}-01-01", f"{end.year}-01-01", freq="YS")
    else:
        expected = pd.DatetimeIndex([date(y, 1, 1) + timedelta(days=d)
                                    for y in range(start.year, end.year + 1) for d in range(0, 365, 16)])
        expected = expected[(expected >= start) & (expected <= end)]
    data = frame.set_index("date")["value"].reindex(expected)
    rows = []
    for year in range(start.year, end.year + 1):
        v = data[data.index.year == year]
        full = start <= pd.Timestamp(year, 1, 1) and end >= pd.Timestamp(year, 12, 31)
        n_expected = (366 if calendar.isleap(year) else 365) if frequency == "Daily" else 12 if frequency == "Monthly" else 1 if frequency == "Annual" else 23
        count = int(v.count())
        reason = "included"
        if not full:
            reason = "partial calendar year requested"
        elif frequency == "Daily" and (count / n_expected < .9 or any(v[v.index.month == m].count() / calendar.monthrange(year, m)[1] < .8 for m in range(1, 13))):
            reason = "daily coverage below 90% annually or 80% in a month"
        elif frequency in {"Monthly", "Annual"} and count != n_expected:
            reason = "missing required monthly or annual values"
        elif frequency == "16-day" and (count < 18 or any(v[v.index.quarter == q].count() < 3 for q in range(1, 5))):
            reason = "fewer than 18 good composites or fewer than 3 in a quarter"
        rows.append(dict(year=year, annual_mean=v.mean(), valid_observations=count,
                         expected_observations=n_expected, completeness=count / n_expected,
                         included=reason == "included", reason=reason))
    return pd.DataFrame(rows), data.rename("value").rename_axis("date").reset_index()


def upload_provenance(content, filename, source, location, frequency, mapping):
    return dict(source="User-provided data (provenance not independently verified)", filename=filename,
                sha256=hashlib.sha256(content).hexdigest(), declared_source=source,
                location=location, frequency=frequency, mapping=mapping,
                spatial_resolution="User supplied; not independently verified")
