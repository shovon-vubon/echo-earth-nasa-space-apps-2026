"""Run with: streamlit run app.py."""
from datetime import date
from zoneinfo import ZoneInfo
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data import DataError, DEMO_LABEL, NASA_LABEL, retrieve, synthetic, json_bytes
from src.preprocessing import annualize
from src.trends import analyze, explanation
from src.questions import QUESTIONS, answer

st.set_page_config(page_title="ECHO EARTH", page_icon="🌍", layout="wide")
st.title("ECHO EARTH")
st.write("Explore long-term Earth trends. Inspect the evidence behind every result.")
st.caption("MIST-DREAMERS · Historical trend explorer · First working release")

LOCATIONS = {"Mirpur / Dhaka — grid location": (23.8223, 90.3654),
             "Sylhet — grid location (not a basin average)": (24.8949, 91.8687),
             "Chattogram — grid location": (22.3569, 91.7832),
             "Custom coordinates": (23.8223, 90.3654)}


@st.cache_data(ttl=86400, max_entries=32, show_spinner=False)
def cached_retrieve(lat, lon, start, end):
    return retrieve(lat, lon, start, end)


def show_table(frame, height=None):
    """Keep data inspectable on hosts that cannot load Arrow's native library."""
    try:
        st.dataframe(frame, hide_index=True, width="stretch", **({"height": height} if height else {}))
    except ImportError:
        st.caption("Basic accessible table view (interactive table library unavailable).")
        st.html('<div style="overflow-x:auto;max-height:420px;overflow-y:auto" tabindex="0" aria-label="Data table">'
                + frame.to_html(index=False, escape=True, na_rep="Missing", border=0) + '</div>')


with st.sidebar:
    st.header("Choose your analysis")
    location = st.selectbox("Location", list(LOCATIONS))
    lat, lon = LOCATIONS[location]
    if location == "Custom coordinates":
        lat = st.number_input("Latitude (degrees north)", -90., 90., lat, format="%.4f")
        lon = st.number_input("Longitude (degrees east)", -180., 180., lon, format="%.4f")
    st.selectbox("Variable", ["Air temperature at 2 metres (T2M)"])
    st.caption("Rainfall, vegetation, and wind workflows are not implemented in this release.")
    # Limit to past full years; recent near-real-time products may be revised.
    last_year = datetime.now(ZoneInfo("Asia/Dhaka")).year - 1
    start = st.date_input("Start date", date(2001, 1, 1), min_value=date(1981, 1, 1), max_value=date(last_year, 12, 31))
    end = st.date_input("End date", date(min(2024, last_year), 12, 31), min_value=date(1981, 1, 1), max_value=date(last_year, 12, 31))
    demo = st.checkbox("Demo Mode (synthetic)", value=False)
    if demo:
        st.warning(DEMO_LABEL)
    submitted = st.button("Analyze", type="primary", width="stretch")
    st.caption("NASA requests are cached for 24 hours. No API key is required.")

selection = (location, lat, lon, start, end, demo)
if st.session_state.get("selection") != selection:
    st.session_state.pop("analysis", None)

if submitted:
    st.session_state.pop("analysis", None)
    if start > end:
        st.error("Start date must be on or before end date.")
    else:
        try:
            with st.spinner("Preparing daily data and screening calendar years…"):
                daily, provenance, raw = synthetic(start, end) if demo else cached_retrieve(lat, lon, start, end)
                annual = annualize(daily, start, end)
                provenance.update({"selected_location": location, "requested_period": [str(start), str(end)],
                                   "processing": "No imputation. Exclude partial years; require >=90% annual and >=80% each-month daily completeness. Daily-weighted annual mean.",
                                   "method_version": "1.0", "synthetic": demo})
                try:
                    result, analysis_error = analyze(annual), None
                except ValueError as exc:
                    result, analysis_error = None, str(exc)
                st.session_state.analysis = (daily, annual, provenance, raw, result, analysis_error)
                st.session_state.selection = selection
        except (DataError, ValueError) as exc:
            st.error(str(exc))
            st.info("No result was generated. Retry NASA later or explicitly select Demo Mode.")

trend_tab, flood_tab = st.tabs(["Historical trends", "Flood Hazard — Experimental"])
with trend_tab:
    st.subheader(f"{location} · Temperature at 2 metres")
    st.write(f"**Requested period:** {start:%d %b %Y} – {end:%d %b %Y} · **Coordinates:** {lat:.4f}, {lon:.4f}")
    st.caption("Point request for a coarse grid-scale value; not a station measurement or a regional/basin average.")
    if demo:
        st.warning(DEMO_LABEL + ". Location controls do not change the synthetic series.")
    if "analysis" not in st.session_state:
        st.info("Choose a location and dates, then select Analyze. At least 10 accepted full years are required for a trend test; 20+ years are preferable.")
    else:
        daily, annual, provenance, raw, result, analysis_error = st.session_state.analysis
        label = provenance["source"]
        completeness = float(daily.temperature_c.notna().mean())
        st.write(f"**Data provenance: {label}**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Valid daily values", f"{daily.temperature_c.count():,} / {len(daily):,}")
        c2.metric("Requested-period completeness", f"{completeness:.1%}")
        c3.metric("Accepted calendar years", str(int(annual.included.sum())))
        if result:
            st.write(explanation(result))
            accepted = annual.loc[annual.included]
            st.caption(f"Actual trend period: {accepted.year.min()}–{accepted.year.max()}; excluded years are not fitted.")
        else:
            st.warning(analysis_error)
        fig = go.Figure()
        accepted = annual.loc[annual.included]
        fig.add_trace(go.Scatter(x=annual.year, y=annual.mean_temperature_c.where(annual.included),
                                 name="Accepted annual mean", mode="lines+markers", connectgaps=False,
                                 line=dict(color="#00796B")))
        excluded = annual.loc[~annual.included]
        fig.add_trace(go.Scatter(x=excluded.year, y=excluded.mean_temperature_c,
                                 name="Excluded year (not fitted)", mode="markers",
                                 marker=dict(symbol="x", color="#AD5700", size=10)))
        if result:
            fig.add_trace(go.Scatter(x=accepted.year, y=result.intercept + result.slope * accepted.year,
                                     name="Theil–Sen fit", mode="lines", line=dict(dash="dash", color="#334EAC")))
        fig.update_layout(title=f"Annual mean temperature · {label}", xaxis_title="Calendar year (UTC)",
                          yaxis_title="Air temperature at 2 metres (°C)", legend=dict(orientation="h"),
                          margin=dict(l=20, r=20, t=70, b=20))
        st.plotly_chart(fig, width="stretch")
        st.caption("The table below provides the chart values for keyboard and screen-reader access. A slope interval is not a prediction interval.")

        with st.expander("Data, methods, limitations & provenance", expanded=True):
            st.markdown("**Processing:** UTC daily values → missing-value screening → calendar-year means → annual trend test. No interpolation or imputation. Partial calendar years are excluded. Each accepted year needs ≥90% valid days overall and ≥80% in every month.")
            st.write("Annual averaging reduces seasonal-cycle effects but hides seasonal changes and extremes. The annual mean weights each available day equally; missing days may still bias it.")
            st.write("Mann–Kendall: two-sided normal approximation, tie-adjusted variance, continuity correction, α = 0.05. Theil–Sen: median pairwise slope using actual calendar years, with a 95% slope interval from SciPy.")
            st.warning("P-values and confidence intervals assume independent annual values. Serial correlation is not corrected. All inference is exploratory; repeated searches across locations or date ranges have no multiple-comparison adjustment. Significance is not causation.")
            if result:
                lag = "undefined (insufficient variation or consecutive pairs)" if result.lag1 is None else f"{result.lag1:+.3f}"
                st.write(f"Detrended lag-1 correlation: {lag}; {result.lag_pairs} consecutive-year pairs. This diagnostic does not establish independence.")
                if result.n < 20:
                    st.warning("Fewer than 20 accepted years: the record is short for long-term interpretation.")
            st.write("Temperature trends alone cannot explain urban waterlogging or forecast floods. This is reanalysis, combining observations and modelling, not direct local thermometer observations.")
            st.json(provenance)
        with st.expander("View and download processed data", expanded=True):
            st.caption(label)
            show_table(annual)
            preview_year = st.selectbox("Daily data preview year", sorted(daily.date.dt.year.unique()))
            show_table(daily.loc[daily.date.dt.year == preview_year], height=220)
            prefix = "synthetic" if demo else "nasa_power"
            exported_daily = daily.assign(source=label, latitude=lat, longitude=lon)
            exported_annual = annual.assign(source=label, latitude=lat, longitude=lon)
            st.download_button("Download daily CSV", exported_daily.to_csv(index=False).encode(), f"{prefix}_daily.csv", "text/csv")
            st.download_button("Download annual CSV (includes exclusions)", exported_annual.to_csv(index=False).encode(), f"{prefix}_annual.csv", "text/csv")
            bundle = {"provenance": provenance, "result": result.to_dict() if result else None,
                      "daily_completeness": completeness,
                      "limitations": "Unadjusted serial dependence and multiple comparisons; exploratory, not causal or predictive."}
            st.download_button("Download analysis and provenance JSON", json_bytes(bundle), f"{prefix}_analysis.json", "application/json")
            if raw:
                st.download_button("Download original NASA response JSON", json_bytes(raw), "nasa_power_response.json", "application/json")
        if result:
            st.subheader("Ask Earth")
            st.caption(label + ". Supported questions: " + " · ".join(QUESTIONS))
            question = st.text_input("Ask about this analysis", placeholder="What is the trend?")
            if question:
                st.write(answer(question, result, provenance, completeness))

with flood_tab:
    st.subheader("Flood Hazard — Experimental")
    st.warning("Not implemented: no flood probability, alert, or 24/48/72-hour forecast is calculated.")
    st.write("A future flood model needs current rainfall and wetness inputs, archived issue-time forecasts, terrain and river context, verified time-stamped flood labels, and enough independent events for validation.")
    st.write("Required evaluation: time-ordered and event-separated holdouts, leakage checks, baseline comparisons, probability calibration, PR-AUC, Brier score, lead-time assessment, and external validation. Compare a model with long-term trends against the same model without them.")
    st.info("Story context: the Mirpur animation depicts urban waterlogging. Mirpur is the default grid location here, but this temperature workflow does not model drainage. Selecting Sylhet changes the study location; it does not turn the Mirpur story into a Sylhet flood case study.")
    st.write("Long-term trend tests cannot derive tomorrow’s weather or a specific flood prediction. Use official services for emergency guidance.")
