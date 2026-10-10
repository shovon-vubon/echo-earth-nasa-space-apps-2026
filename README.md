# echo-earth-nasa-space-apps-2026
ECHO EARTH | NASA Space Apps 2026 — Explainable Earth-system trend analysis and experimental AI-assisted disaster-risk intelligence using NASA open data.
🌍 ECHO EARTH
From Hidden Earth Trends to Actionable Disaster Intelligence
NASA International Space Apps Challenge 2026  
Challenge: Be An Earth System Trend Detective!  
Local event: Dhaka, Bangladesh  
Project status: Concept / early development
> **ECHO EARTH** is a proposed explainable Earth-intelligence platform that examines how temperature, precipitation, vegetation, and wind speed change across time and location using NASA open data. It aims to connect rigorous environmental trend analysis with a carefully validated, experimental flood-risk intelligence module.
The problem
Environmental changes are not uniform: a variable can increase in one region and decrease in another. Maps and time-series charts alone do not tell us whether a change is statistically meaningful or what its practical implications might be. Meanwhile, near-term disasters require different evidence than long-term climate trends.
Our proposed solution
ECHO EARTH brings together two complementary research components:
Earth Trend Intelligence: Identify what is changing, where, how much, and whether the trend is statistically significant.
Experimental Hazard Intelligence: Explore how recent observations, forecasts, terrain, and rigorously tested machine-learning methods could support flood-related risk assessment, without confusing climate trends with short-term prediction.
The initial geographic focus is Bangladesh, with a future path toward wider regional applications.
Core environmental variables
Variable	Proposed NASA data	Analysis goal
🌡️ Temperature	MERRA-2 near-surface air temperature	Long-term temperature trends
🌧️ Precipitation	GPM IMERG V07	Rainfall trends, anomalies, regional contrasts
🌿 Vegetation	MODIS MOD13C2 V6.1 NDVI	Greening/browning patterns
💨 Wind speed	MERRA-2 near-surface wind components	Wind-speed change over time
💧 Soil moisture (optional)	GLDAS-2.1 or SMAP	Wetness context for environmental and hazard analysis
Proposed common historical analysis period: 2001–2024, subject to coverage and quality screening.
What makes ECHO EARTH different?
Earth Hazard Signature (proposed)
An explainable evidence framework connecting climate memory, current environmental signals, forecast hazard context, and local exposure. This is a proposed design concept—not an established scientific index or a demonstrated prediction model.
Disaster Rewind
An investigation mode that revisits a documented historical event using only the data that would have been available before the event. It then compares a model's historical estimates, where available and validated, with what actually occurred. The approach is designed to make both successful and unsuccessful predictions visible.
Opposite-Trend Discovery
Find regional pairs where a NASA-observed variable exhibits contrasting trends, while showing effect sizes, test assumptions, uncertainty, and data provenance.
Scientific approach (planned)
Quality-control and spatially harmonize NASA datasets.
Estimate trend magnitude using Theil–Sen slopes or another appropriate estimator.
Assess monotonic trends with suitable Mann–Kendall methods, accounting for seasonality and serial correlation when needed.
Consider multiple-testing corrections for spatial trend maps.
Compare environmental-variable anomalies without making unsupported causal claims.
For any flood-risk model, use time-ordered evaluation, independent historical event labels, probability calibration, and comparisons with simpler baselines.
Planned architecture
```text
NASA Earth data ──> Quality control and harmonization
                             │
                             ▼
                   Earth Trend Intelligence
                             │
Recent observations + forecasts + terrain ──> Experimental Hazard Intelligence
                             │
                             ▼
                    Evidence & explanation
                             │
                             ▼
                 Interactive ECHO EARTH app
```
Planned stack
Python, Xarray, Pandas, GeoPandas, SciPy, Streamlit, Plotly; potentially XGBoost/LightGBM for an experimental flood-risk module after training data and baselines have been validated.
Development milestones
[ ] Select the first Bangladesh study regions and verify data access.
[ ] Prepare and document the four NASA datasets.
[ ] Implement and test long-term trend estimation.
[ ] Create trend maps, time series, and region comparisons.
[ ] Build an evidence-inspection interface.
[ ] Select a documented flood case and prepare a leakage-free retrospective investigation.
[ ] Evaluate a flood-risk baseline and only then consider a machine-learning alternative.
[ ] Publish the demo, reproducibility instructions, and a short project video.
Repository layout
```text
README.md                Project overview
.gitignore               Ignore local data, cache, secrets, and model artifacts
docs/
  data-sources.md        Dataset links, units, and preprocessing considerations
  methodology.md         Scientific methods, testing, and uncertainty
  roadmap.md             Scope, milestones, and deliverables
data/README.md           Data handling and download instructions
src/                     Application and analysis source code (forthcoming)
tests/                   Automated tests (forthcoming)
assets/                  Original and properly credited visual assets
```
Current status & responsible-use notice
⚠️ Concept-stage project: Screenshots, diagrams, and interface mockups should be labeled as concepts until backed by actual processed NASA data. No operational disaster-warning system or validated flood forecast is currently claimed. Do not use the project as an emergency alert service; consult official forecasting and emergency-management agencies for real warnings.
NASA data and tools are used for the competition challenge; this student project is not an official NASA warning product or an endorsement by NASA.
References and data credits
NASA Space Apps Challenge 2026
NASA GPM IMERG
NASA MERRA-2
NASA LP DAAC — MODIS vegetation products
NASA Earthdata
NASA GLDAS dataset catalogue
See `docs/data-sources.md` for intended data usage and cautions.
Team
[YOUR TEAM NAME] — NASA Space Apps Challenge 2026, Dhaka.  
Team members: [add member names and GitHub profiles].
License
An open-source license should be selected with agreement from all contributors before release (e.g., MIT). Data and third-party assets retain their respective license and citation requirements.
