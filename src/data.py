"""Public NASA POWER retrieval; no synthetic fallback on failure."""
from datetime import datetime, timezone
import hashlib
import json

import numpy as np
import pandas as pd
import requests

ENDPOINT = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_LABEL = "NASA POWER / MERRA-2 reanalysis"
DEMO_LABEL = "Illustrative synthetic data—not NASA observations"
DOCS = "https://power.larc.nasa.gov/docs/services/api/temporal/daily/"


class DataError(ValueError):
    """An unavailable or invalid source must not produce scientific results."""


def parse_power(payload, start, end, parameter="T2M"):
    try:
        values = payload["properties"]["parameter"][parameter]
        units = payload["parameters"][parameter]["units"]
        fill = float(payload["header"]["fill_value"])
        allowed = {"MM/DAY"} if parameter == "PRECTOTCORR" else {"C", "°C", "DEG C"}
        if units.upper() not in allowed:
            raise DataError(f"Unexpected NASA temperature units: {units}")
        series = pd.Series(values, dtype="float64")
        series.index = pd.to_datetime(series.index, format="%Y%m%d", errors="raise")
        series = series.mask((series == fill) | ~np.isfinite(series))
        dates = pd.date_range(start, end, freq="D")
        series = series.reindex(dates)
        if not series.notna().any():
            raise DataError("NASA returned no valid T2M values for the requested period.")
        return pd.DataFrame({"date": dates, "temperature_c": series.to_numpy()})
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, DataError):
            raise
        raise DataError(f"NASA response could not be validated: {exc}") from exc


def retrieve(latitude, longitude, start, end, parameter="T2M"):
    if parameter not in {"T2M", "TS", "PRECTOTCORR"}:
        raise DataError("Unsupported POWER parameter.")
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise DataError("Coordinates are outside valid latitude/longitude bounds.")
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start > end or start < pd.Timestamp("1981-01-01"):
        raise DataError("Choose ordered dates on or after 1981-01-01.")
    params = dict(parameters=parameter, community="AG", latitude=latitude,
                  longitude=longitude, start=start.strftime("%Y%m%d"),
                  end=end.strftime("%Y%m%d"), format="JSON", **{"time-standard": "UTC"})
    try:
        response = requests.get(ENDPOINT, params=params, timeout=(10, 90))
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise DataError(f"NASA POWER is unavailable or rejected this request. Retry later. Details: {exc}") from exc
    daily = parse_power(payload, start, end, parameter)
    provenance = {
        "source": NASA_LABEL, "variable": parameter + ": " + payload["parameters"][parameter]["longname"],
        "units": payload["parameters"][parameter]["units"], "request_url": response.url,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "response_sha256": hashlib.sha256(response.content).hexdigest(),
        "latitude": latitude, "longitude": longitude,
        "spatial_resolution": "MERRA-2 native 0.5° latitude × 0.625° longitude; grid-scale, not street-scale",
        "temporal_resolution": "Daily, UTC; aggregated locally to calendar-year means",
        "coverage": "Global; POWER daily meteorology from 1981 to near real time; recent values may be revised",
        "documentation": DOCS, "header": payload.get("header", {}),
        "parameter_metadata": payload.get("parameters", {}).get(parameter, {}),
        "geometry_returned_by_api": payload.get("geometry", {}),
    }
    return daily, provenance, payload


def synthetic(start, end):
    dates = pd.date_range(start, end, freq="D")
    rng = np.random.default_rng(42)
    values = 25 + 5 * np.sin(2 * np.pi * dates.dayofyear.to_numpy() / 365.25)
    values += 0.03 * (dates.year.to_numpy() - 2001) + rng.normal(0, 1.5, len(dates))
    values[rng.random(len(dates)) < .01] = np.nan
    return pd.DataFrame({"date": dates, "temperature_c": values}), {
        "source": DEMO_LABEL, "units": "°C", "generator": "Fixed seed 42; seasonal sinusoid + imposed trend + noise",
        "spatial_resolution": "None: synthetic series is not location-specific",
        "temporal_resolution": "Daily synthetic values",
    }, None


def json_bytes(value):
    return json.dumps(value, indent=2, ensure_ascii=False, default=str).encode("utf-8")
