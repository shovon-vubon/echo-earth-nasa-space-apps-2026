# ECHO EARTH

See what changed. Understand the evidence. A trend-focused Python + Streamlit app by MIST-DREAMERS.

## Run

Python 3.11+ recommended. From the project root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501. On macOS/Linux substitute `.venv/bin/python`.
No credentials or paid language-model service are required.

## Explore

1. Start with the rotating globe; click the Bangladesh marker or **Explore Bangladesh**. Dragging stops rotation; reduced-motion preferences disable it.
2. Choose a city marker or the accessible Location selector. The map centres on the selected location. Custom coordinates also work. These are point/grid selections, not district or basin averages.
3. Switch **Surface temperature / Rainfall / Vegetation / Air temperature** in the sidebar.
4. Choose dates and **Analyze**. At least 10 accepted years are required; prefer 20+.
5. Inspect the chart, calculations, exclusions, uncertainty and provenance. Download the processed/source CSVs and analysis/source JSON.

Surface temperature is primary. It uses NASA POWER **TS (Earth Skin Temperature)** from MERRA-2 reanalysis: a coarse modelled surface temperature over land, not air temperature and not a high-resolution MODIS thermal image. Coastal cells can mix land and water.

| Workflow | NASA product | Units / cadence |
|---|---|---|
| Surface temperature | POWER / MERRA-2 TS | Celsius, daily |
| Rainfall / precipitation | POWER / MERRA-2 PRECTOTCORR | mm/day, daily; includes frozen precipitation |
| Vegetation | MODIS MOD13Q1 via NASA ORNL DAAC | NDVI, 16-day composites, nominal 250 m |
| Air temperature | POWER / MERRA-2 T2M | Celsius, daily |

POWER native meteorology resolution is 0.5 degrees latitude by 0.625 degrees longitude. Multi-year MODIS requests are batched ten dates at a time and can take several minutes. Requests are cached for 24 hours; MODIS public responses are also cached under ignored `data/cache/modis/` so retries can reuse successful batches. Network failures receive at most three attempts. Source failures never become synthetic results. MODIS source metadata, pixel reliability and API requests are retained.

## Upload new data without coding

Choose **Upload CSV**, preview the file, map date/value columns, choose units and Daily/Monthly/Annual cadence, supply a source and location, and confirm the input definitions. Then Analyze. The same analysis functions run on uploaded data; this is statistical analysis, not model training.

- UTF-8 CSV, maximum 10 MB / 100,000 rows, one variable and location.
- Supported explicit date formats: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, YYYY-MM, YYYY.
- Celsius or Kelvin temperatures (converted); precipitation in mean mm/day; scaled NDVI in -0.2 to 1.
- Monthly and annual records must already be period means, not precipitation totals. Quality-screen NDVI first.
- Numeric missing markers and nonnumeric values become missing; invalid dates, duplicate periods, invalid ranges and missing declarations produce actionable errors.
- File SHA-256, mapping, units, declared source and location accompany exports. Files remain in the Streamlit process and are not sent to NASA or an AI service. They are not written to the repository by the upload workflow.
- User-provided files are not automatically certified as NASA observations. HDF, NetCDF, GeoTIFF and automatic polygon aggregation need future dataset-specific adapters.

The CSV layout example is only two illustrative rows; it shows formatting and cannot support a trend test. New competition datasets can be uploaded once converted to these documented columns and units. Release dates/content are not assumed by the app.

## Scientific interpretation

[Methods](docs/methodology.md) and [sources](docs/data-sources.md) document processing and limitations. Daily annual means require 90% annual and 80% monthly completeness. Monthly uploads require 12 values. Annual uploads have unknown within-year completeness. NDVI requires 18 of 23 accepted composites and at least three in each quarter; reliability 0 and 1 are accepted, with marginal-quality limitations disclosed.

Mann-Kendall uses tie-adjusted variance and continuity correction. Theil-Sen uses actual year spacing and reports a 95% slope interval. Annual averaging can hide seasonal changes and extremes. Neither serial dependence nor multiple comparisons is corrected. Statistical significance is not causation; findings are exploratory.

Ask Earth recomputes the selected annual analysis for supported trend/slope questions and shows the function, sample count and source used. Completeness questions count actual valid observations. Unsupported questions are rejected.

**Synthetic demo** is explicit and labeled "Illustrative synthetic data-not NASA observations" throughout. It is never a source-error fallback.

## Scope and roadmap

Forecasting has been removed from the product interface. Future research may assess hazard models only after appropriate data, labels and independent validation exist. Global country drill-down, area/polygon averages, satellite thermal products, seasonal tests and broader upload adapters are future work. Mirpur waterlogging is a story context, not a consequence established by a temperature trend. This is not an official NASA product or endorsement.

## Code and tests

- `app.py`: entry point; `src/dashboard.py`: interface, cache and supported questions.
- `src/data.py`: POWER access; `src/vegetation.py`: MODIS retrieval and QA.
- `src/workflows.py`: variable definitions, upload validation and annual aggregation.
- `src/trends.py`: statistics; `src/maps.py`: globe and location map.
- `src/preprocessing.py` and `src/questions.py`: retained first-release compatibility helpers.
- `tests/`: offline science, upload and app-interaction tests.
- `scripts/smoke_variables.py`: live source verification; writes ignored `data/cache/` evidence.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -X utf8 scripts/smoke_variables.py
```

Globe boundaries and OpenStreetMap tiles require browser internet access. If Arrow's native DLL is blocked, data tables fall back to accessible escaped HTML without weakening Windows security. The original proposal and first-release documentation/code are preserved in `docs/`. Secrets, virtual environments and local data caches are ignored by Git.
