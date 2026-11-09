# ECHO EARTH

Historical Earth trends with traceable evidence. MIST-DREAMERS, Dhaka.
Built for the proposed NASA Space Apps challenge workflow, "Be an Earth System Trend Detective."

## First working release

A Python + Streamlit dashboard retrieves real NASA POWER daily **T2M (air temperature at 2 metres)**, screens data completeness, and analyzes annual means with Mann-Kendall and Theil-Sen. No private credentials or paid AI service is needed. The original project proposal is preserved in [docs/original-proposal.md](docs/original-proposal.md); its multi-variable and hazard roadmap is not a claim of implemented functionality.

## Setup and run

Python 3.11 or newer recommended. From the repository root, on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On macOS/Linux use `.venv/bin/python` instead. Open http://localhost:8501. Internet access to NASA POWER is required for real data. Choose a location, temperature, and dates, then **Analyze**. Default: Mirpur/Dhaka, 2001-2024. At least 10 accepted calendar years are required; 20+ are preferable. Dates are limited to past calendar years. Changing a selection clears the previous result until Analyze is pressed again.

NASA requests are cached in memory for 24 hours (maximum 32 selections). Source errors are displayed; there is no automatic fallback or invented NASA result. Download daily and annual CSVs, analysis/provenance JSON, and the original NASA response. The provenance records retrieval time, request URL, response hash, API metadata and processing choices.

## Demo Mode

Explicitly enable **Demo Mode (synthetic)** and click Analyze. Every synthetic result and chart is labeled **Illustrative synthetic data - not NASA observations**; CSV rows carry that source label and filenames start with `synthetic`. Fixed-seed data demonstrate controls and methods only, have no spatial meaning, and are not cached NASA data. Turn Demo Mode off and Analyze to retrieve real values.

## Science and scope

- [Data sources](docs/data-sources.md): verified NASA documentation, variable, units, coverage and access.
- [Methods](docs/methodology.md): completeness screens, annual aggregation, formulas, assumptions and limitations.
- One working variable: temperature. No precipitation, NDVI or wind retrieval is implemented.
- Location selection is a grid-scale point request, not a basin average or local sensor.
- Ask Earth accepts four explicit result-grounded questions, displayed in the app. Unsupported questions are rejected; no LLM is involved.
- Flood Hazard is an **unimplemented experimental area**. It contains requirements, no probabilities, warnings or 24/48/72-hour predictions.
- Mirpur urban waterlogging is the storytelling context. A Sylhet selection is a separate grid location, not evidence about Mirpur and not a validated Sylhet flood study.
- This student project is not an official NASA warning service or NASA endorsement.

## Structure

```text
app.py                     Streamlit interface and cache boundary
src/data.py                NASA access, response validation, explicit synthetic mode
src/preprocessing.py       Daily completeness and calendar-year aggregation
src/trends.py              Mann-Kendall, Theil-Sen, residual correlation diagnostic
src/questions.py           Supported result-grounded questions
scripts/smoke_nasa.py       Opt-in real NASA integration check
tests/                    Scientific and Streamlit interaction tests
docs/                      Source/method records and original proposal
```

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/smoke_nasa.py
```

The first command runs offline tests. The second makes a live NASA request and saves its original JSON, processed annual CSV and provenance to ignored `data/cache/`; failures are not replaced with fixtures. Dependencies use bounded versions in requirements.txt; this is not a fully locked environment.

## Future hazard work

Require current-condition inputs, issue-time forecasts, terrain/rivers/exposure, verified timestamped flood-event labels and a trained, independently validated model. Use time- and event-separated evaluation, leakage controls, calibration, PR-AUC/Brier scores, baseline comparison and external validation. Test whether adding long-term trends improves the baseline. Until this evidence exists, the interface must not show a real probability or forecast.

No secrets are required. `.env`, Streamlit secrets, virtual environments and local retrieval caches are ignored by Git. Do not put credentials in code or exports.

If Windows blocks Arrow's native table library, the app automatically displays escaped, scrollable HTML tables instead. Charts, calculations and CSV downloads still work; no security-policy changes are needed.

