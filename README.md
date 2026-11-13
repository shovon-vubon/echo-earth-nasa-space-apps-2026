# 🌍 ECHO EARTH: Evidence-Based Earth System Trend Intelligence

[![NASA Space Apps Challenge](https://img.shields.io/badge/NASA%20Space%20Apps-Challenge%202026-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)](https://www.spaceappschallenge.org/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-echoearth--app.web.app-008080?style=for-the-badge&logo=google-cloud&logoColor=white)](https://echoearth-app.web.app)
[![Custom Domain](https://img.shields.io/badge/Domain-echoearth.app-2E7D32?style=for-the-badge)](https://echoearth.app)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **See what changed. Understand the evidence.**  
> A transparent, scientifically grounded Earth observation and environmental trend analysis platform developed by **Team MIST-DREAMERS** for the **NASA International Space Apps Challenge**.

---

## 🌟 Executive Summary

Environmental trends are rarely uniform: surface temperatures can rise in urban settlements while adjacent wetlands experience distinct precipitation shifts. Traditional climate portals often hide the mathematical nuance behind complex black-box averages or generate speculative predictive forecasts. 

**ECHO EARTH** is an explainable Earth-intelligence web application that translates 24+ years of multi-sensor NASA Earth observation data into robust, transparent, and reproducible statistical trends. Focusing on climate-vulnerable regions across Bangladesh, the platform analyzes:
- **Surface Skin Temperature (`TS`)**
- **Ambient Air Temperature (`T2M`)**
- **Corrected Precipitation (`PRECTOTCORR`)**
- **Vegetation Dynamics (`NDVI`)**

Every trend is validated using non-parametric statistical methods (**Theil–Sen robust slope estimation** and **Mann–Kendall monotonic trend tests**) with rigorous data-completeness filtering, accompanied by **"Ask Earth"**, a grounded, zero-hallucination deterministic query assistant.

---

## 🚀 Live Demo & Access

- 🌐 **Primary Web Application**: [https://echoearth-app.web.app](https://echoearth-app.web.app)
- 🔗 **Production Domain**: [https://echoearth.app](https://echoearth.app)
- ⚡ **Zero-Installation Experience**: Fully accessible via modern web browsers on desktop and mobile devices.

---

## ✨ Key Features

### 1. 🌐 Interactive 3D D3.js Earth Globe
- Locally rendered client-side orthographic globe built with bundled **Natural Earth 1:110m** vector geometry.
- Full drag rotation, inertia physics, zoom controls, and a dedicated **Focus Bangladesh** action button.
- Zero external CDN dependencies or heavy WebGL overhead; automatically honors OS `prefers-reduced-motion` settings.

### 2. 🗺️ Live OpenStreetMap Slippy Basemap
- Embedded interactive canvas tile navigator with real-time pan and zoom controls.
- Interactive division markers across Bangladesh (Dhaka, Chittagong, Rajshahi, Sylhet, Khulna, Barisal, Rangpur, Mymensingh) alongside custom coordinate pin inputs.
- Clear distinction between point-location sampling and district/basin spatial aggregates.

### 3. 🔬 Multi-Decade NASA Earth Observation Workflows
Direct integration with NASA Earth Science data services authenticated via official NASA Open Data API keys (`api.nasa.gov`):
- **Surface Skin Temperature (`TS`)**: NASA POWER / MERRA-2 daily land skin temperature (Celsius).
- **Air Temperature (`T2M`)**: NASA POWER / MERRA-2 daily ambient temperature at 2 meters (Celsius).
- **Precipitation (`PRECTOTCORR`)**: NASA POWER / MERRA-2 bias-corrected daily precipitation rate (mm/day).
- **Vegetation Indices (`MOD13Q1`)**: NASA Terra MODIS 250m 16-day composite Normalized Difference Vegetation Index (NDVI) with pixel reliability screening.

### 4. 📐 Rigorous Non-Parametric Scientific Statistics
- **Theil–Sen Estimator**: Computes median pairwise slopes resistant to extreme anomalies and seasonal outliers, reporting 95% confidence intervals.
- **Mann–Kendall Trend Test**: Detects monotonic directionality with tie-adjusted variance and continuity-corrected Z-scores ($p < 0.05$ threshold).
- **Strict Quality & Completeness Filtering**: Requires $\ge 90\%$ annual completeness and $\ge 80\%$ monthly completeness for daily meteorology; NDVI requires at least 18 of 23 valid composites per year across all four quarters.
- **Scientific Honesty**: Explicitly separates statistical significance from physical causation and avoids misleading extrapolations.

### 5. 🤖 Grounded Deterministic Assistant ("Ask Earth")
- Local, deterministic conversational query engine with interactive chat history.
- Explains warming rates, trend slopes, confidence bounds, extreme years, and dataset provenance.
- Every numerical response is dynamically derived from verified mathematical calculations rather than probabilistic large-language-model guessing.

### 6. 📂 No-Code Data Upload & Ground Station Benchmarking
- Ingest custom in-situ station observations (e.g., Bangladesh Meteorological Department CSV records) without writing code.
- Automatic column mapping, date parsing (YYYY-MM-DD, DD/MM/YYYY, YYYY), unit conversions (Kelvin to Celsius), and SHA-256 cryptographic verification.
- Enables side-by-side comparison between ground truth sensors and satellite reanalysis.

---

## 📊 NASA Datasets & Provenance

All observations used in ECHO EARTH are sourced directly from NASA Earth Science platforms:

| Workflow | NASA Product / Sensor | Resolution & Cadence | Primary Purpose & Usage |
|---|---|---|---|
| **Surface Temperature** | NASA POWER / MERRA-2 `TS` | 0.5° × 0.625°, Daily | Multi-decade ground skin warming trends and Theil–Sen slope estimation. |
| **Air Temperature** | NASA POWER / MERRA-2 `T2M` | 0.5° × 0.625°, Daily | Ambient atmospheric heat trends distinct from surface ground heat. |
| **Rainfall / Precipitation** | NASA POWER / MERRA-2 `PRECTOTCORR` | 0.5° × 0.625°, Daily | Long-term precipitation variability and annual mean daily rainfall analysis. |
| **Vegetation Health** | NASA Terra MODIS `MOD13Q1` (v6.1) | 250 m, 16-Day | Multi-decade NDVI greening/browning dynamics with pixel reliability screening. |
| **API Authentication** | NASA Open Data (`api.nasa.gov`) | REST API | Official client authorization, endpoint rate limiting, and dataset provenance tracking. |

### Supporting Open Datasets & Assets
- **Natural Earth (1:110m Cultural & Physical Vectors, v5.1.2)**: Global land boundary polygons for the 3D interactive globe.
- **OpenStreetMap Standard Tile Cartography**: OpenStreetMap contributors basemap for regional coordinate navigation.
- **BMD Historical Ground Station Benchmark**: Ground-truth validation schema for user-uploaded observational records.

---

## 🛠️ Local Development & Setup

### Prerequisites
- Python 3.11 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/echo-earth-nasa-space-apps-2026.git
cd echo-earth-nasa-space-apps-2026
```

### 2. Set Up Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the Streamlit Application
```powershell
# Windows
.\.venv\Scripts\python.exe -m streamlit run app.py

# macOS / Linux
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Testing & Verification

The scientific algorithms and data ingestion workflows are verified by automated test suites:

```powershell
# Run unit and scientific validation tests
.\.venv\Scripts\python.exe -m pytest tests/test_science.py tests/test_workflows.py -q

# Run live NASA API smoke tests (writes data/cache/ verification records)
.\.venv\Scripts\python.exe -X utf8 scripts/smoke_variables.py
```

---

## 📁 Project Architecture

```text
echo-earth-nasa-space-apps-2026/
├── app.py                      # Main application entry point
├── src/
│   ├── dashboard.py            # Streamlit UI layout, state, and user controls
│   ├── data.py                 # NASA POWER API client, caching & provenance
│   ├── vegetation.py           # NASA MODIS MOD13Q1 retrieval & QA screening
│   ├── trends.py               # Mann-Kendall test & Theil-Sen slope calculation
│   ├── workflows.py            # Data aggregation, quality checks & CSV ingestion
│   ├── chat.py                 # Grounded deterministic 'Ask Earth' query engine
│   ├── maps.py                 # Map coordinate transforms & Leaflet/OSM wrappers
│   └── theme.py                # Accessible styling, responsive UI & typography
├── public/                     # Standalone web app build for Firebase Hosting
│   ├── index.html              # Pure web dashboard (OpenStreetMap + NASA APIs)
│   └── globe.html              # Standalone D3.js interactive rotating 3D globe
├── assets/maps/                # Natural Earth vector geometries and D3 libraries
├── scripts/
│   ├── build_firebase_public.py # Static compiler for public/ distribution
│   └── smoke_variables.py      # Live NASA API verification script
├── tests/
│   ├── test_science.py         # Statistical algorithm tests (Mann-Kendall, Theil-Sen)
│   └── test_workflows.py       # Quality screening, unit conversion & upload tests
├── docs/                       # Scientific methodology and data source documentation
├── requirements.txt            # Python dependencies
└── firebase.json               # Firebase Hosting deployment configuration
```

---

## 🔬 Scientific Methodology & Disclaimers

1. **Spatial Resolution**:
   - NASA POWER meteorology has a native spatial resolution of $0.5^\circ \times 0.625^\circ$. Coastal grid cells can represent combined land-water responses.
   - MODIS MOD13Q1 provides a nominal 250 m ground resolution per pixel composite.
2. **Completeness Thresholds**:
   - Years failing the 90% annual or 80% monthly completeness criteria are rejected to eliminate seasonal bias.
3. **Correlation vs. Causation**:
   - A statistically significant monotonic trend ($p < 0.05$) indicates directional persistence over the analyzed window, not environmental causation or attribution.
4. **No Speculative Forecasting**:
   - ECHO EARTH focuses strictly on empirical historical evidence. Speculative multi-decadal predictive forecasting has been intentionally excluded to adhere to scientific verification standards.
5. **NASA Disclaimer**:
   - This project is developed as part of the NASA International Space Apps Challenge. It utilizes publicly available NASA Earth Science data but is not an official NASA product or agency endorsement.

---

## 👥 Team MIST-DREAMERS

Developed with dedication for the **NASA International Space Apps Challenge 2026**:
- **Affiliation**: Military Institute of Science and Technology (MIST), Dhaka, Bangladesh
- **Focus**: Climate Resilience, Earth Observation Data Science & Accessible Science Communication

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.  
All NASA data products are distributed under NASA Open Data policies. OpenStreetMap tiles are © OpenStreetMap contributors. Natural Earth vector geometries are public domain.
