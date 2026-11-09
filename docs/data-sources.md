# Connected data source

Documentation reviewed 2026-11-09. Dataset: NASA POWER daily meteorological data, T2M based on NASA GMAO MERRA-2 reanalysis. POWER is the serving product, not a local weather station.

| Field | First-release choice |
|---|---|
| Variable | T2M, daily mean air temperature at 2 metres |
| Units | Degrees Celsius; API response units are validated before analysis |
| Temporal resolution | Daily; explicit UTC time standard |
| Spatial resolution | Native meteorology: 0.5° latitude × 0.625° longitude |
| Spatial coverage | Global; one grid-scale point request, no polygon averaging |
| Temporal coverage | POWER daily service: 1981-01-01 to near real time, subject to availability |
| App default | Mirpur/Dhaka coordinate 23.8223 N, 90.3654 E; 2001–2024 |
| Access | Public HTTPS GET, JSON, no API key or Earthdata login |

Official references:

- [Daily API and UTC coverage](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [Meteorology methodology and MERRA-2 sources](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)
- [NASA tutorial: native resolution and revisions](https://power.larc.nasa.gov/docs/tutorials/)
- [NASA API request tutorial](https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/)

Endpoint: `https://power.larc.nasa.gov/api/temporal/daily/point`
Parameters: `parameters=T2M&community=AG&latitude=23.8223&longitude=90.3654&start=20010101&end=20241231&format=JSON&time-standard=UTC`.

NASA documentation also mentions a 0.5° × 0.5° request grid in the daily API warning. We describe the meteorological source's native resolution from the NASA methodology/tutorial rather than claim that request coordinates provide finer information. Returned geometry is recorded as API geometry, not asserted to be an exact source-cell centre. Reanalysis represents modelled grid-scale conditions informed by observations. It cannot resolve a street, drainage channel or individual urban flood.

NASA notes recent meteorological data can be superseded by improved climate-quality values after roughly 2–3 months. The app avoids the current calendar year but users should still retain retrieval metadata. Each result includes the original header, T2M metadata, request URL, UTC retrieval timestamp and original response SHA-256. The exported original JSON is reformatted, so its bytes will differ from the original HTTP-body hash.

No NASA data is bundled or manufactured. Synthetic data are generated only by explicit user selection, labeled everywhere, and are not location-dependent. Source/API failures produce an error. Other datasets mentioned in the original proposal are future work.
