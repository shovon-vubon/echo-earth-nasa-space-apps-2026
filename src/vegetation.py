"""NASA ORNL DAAC MODIS single-pixel NDVI with explicit QA and batch provenance."""
from datetime import datetime, timezone
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import requests
from src.data import DataError

BASE = "https://modis.ornl.gov/rst/api/v1"
NDVI = "250m_16_days_NDVI"
QUALITY = "250m_16_days_pixel_reliability"


def get_json(path, params=None):
    url = requests.Request("GET", BASE + path, params=params).prepare().url
    cache = Path(__file__).resolve().parents[1] / "data" / "cache" / "modis"
    key = hashlib.sha256(url.encode()).hexdigest()
    file = cache / (key + ".json")
    if file.exists() and time.time() - file.stat().st_mtime < 86400:
        try:
            stored = json.loads(file.read_text(encoding="utf-8"))
            return stored["payload"], stored["request"]
        except (ValueError, KeyError, OSError):
            pass
    try:
        for attempt in range(3):
            try:
                r = requests.get(url, headers={"Accept": "application/json"}, timeout=(10, 45))
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)
        payload = r.json()
        request = {"url": r.url, "sha256": hashlib.sha256(r.content).hexdigest(),
                   "retrieved_utc": datetime.now(timezone.utc).isoformat()}
        # Only public API responses; uploads are never persisted here.
        try:
            cache.mkdir(parents=True, exist_ok=True)
            file.write_text(json.dumps(dict(payload=payload,request=request)), encoding="utf-8")
        except OSError:
            pass  # A read-only deployment can still analyze live responses.
        return payload, request
    except (requests.RequestException, ValueError) as exc:
        raise DataError(f"NASA ORNL vegetation service unavailable: {exc}") from exc


def parse_subset(payload, scale=.0001, offset=0, fill=-3000):
    if payload.get("nrows") != 1 or payload.get("ncols") != 1:
        raise DataError("Expected one MODIS pixel; refusing to silently average an area.")
    records = {}
    for item in payload.get("subset", []):
        if item["band"] in {NDVI, QUALITY}:
            records.setdefault(item["calendar_date"], {})[item["band"]] = item["data"][0]
    rows = []
    for day, bands in records.items():
        raw, quality = bands.get(NDVI, fill), bands.get(QUALITY, -1)
        good = raw != fill and -2000 <= raw <= 10000 and quality in {0, 1}
        rows.append({"date": pd.Timestamp(day), "value": raw * scale + offset if good else np.nan,
                     "pixel_reliability": quality, "quality_accepted": good})
    if not rows:
        raise DataError("No NDVI and reliability records returned.")
    return pd.DataFrame(rows)


def retrieve_ndvi(lat, lon, start, end, progress=None):
    dates_payload, dates_request = get_json("/MOD13Q1/dates", {"latitude": lat, "longitude": lon})
    bands_payload, bands_request = get_json("/MOD13Q1/bands")
    products, products_request = get_json("/products")
    product = next((p for p in products["products"] if p["product"] == "MOD13Q1"), None)
    meta = next(b for b in bands_payload["bands"] if b["band"] == NDVI)
    dates = [d for d in dates_payload["dates"] if str(start) <= d["calendar_date"] <= str(end)]
    if not dates:
        raise DataError("No MODIS composites available in this interval at this location.")
    frames, responses, requests_meta = [], [], [dates_request, bands_request, products_request]
    for i in range(0, len(dates), 10):
        chunk = dates[i:i + 10]
        payload, request = get_json("/MOD13Q1/subset", dict(latitude=lat, longitude=lon,
            startDate=chunk[0]["modis_date"], endDate=chunk[-1]["modis_date"], kmAboveBelow=0, kmLeftRight=0))
        frames.append(parse_subset(payload, float(meta["scale_factor"]), float(meta.get("add_offset", 0)), float(meta["fill_value"])))
        responses.append(payload)
        requests_meta.append(request)
        if progress:
            progress(min((i + 10) / len(dates), 1.))
    frame = pd.concat(frames).sort_values("date").drop_duplicates("date")
    provenance = dict(source="NASA MODIS MOD13Q1 via ORNL DAAC", product_metadata=product,
        band_metadata=meta, units="NDVI", spatial_resolution="Nominal 250 m MODIS sinusoidal pixel; one pixel, no area average",
        actual_cellsize_metres=responses[0].get("cellsize"), temporal_resolution="16-day composites",
        coverage="Global land; 2000 onward, subject to local availability", retrieved_utc=datetime.now(timezone.utc).isoformat(),
        quality="Reliability 0 (good) and 1 (marginal) accepted; snow/ice, cloudy, fill and out-of-range pixels excluded. Detailed VI bitmask not applied; residual contamination possible.",
        requests=requests_meta, documentation="https://modis.ornl.gov/data/modis_webservice.html")
    return frame, provenance, {"product": product, "bands": bands_payload, "responses": responses}
