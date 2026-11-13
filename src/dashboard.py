"""ECHO EARTH trend-first interface."""
from datetime import date, datetime
from zoneinfo import ZoneInfo
import hashlib
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from src.data import DataError, DEMO_LABEL, retrieve, synthetic, json_bytes
from src.trends import analyze, explanation
from src.workflows import VARIABLES, read_csv, prepare_upload, aggregate, upload_provenance
from src.vegetation import retrieve_ndvi
from src.maps import LOCATIONS, globe_html, region_map
from src.theme import apply_theme
from src.chat import respond


@st.cache_data(ttl=86400, max_entries=32, show_spinner=False)
def nasa_data(lat, lon, start, end, code, api_key="kDgGKpwj6dqqLQQpTc97W68cgC87NR7KkrMLBPwg"):
    if code == "NDVI":
        progress = st.progress(0., text="Loading MODIS metadata and quality-screened composites…")
        try:
            return retrieve_ndvi(lat, lon, start, end,
                progress=lambda fraction: progress.progress(fraction, text=f"MODIS composites retrieved: {fraction:.0%}"))
        finally:
            progress.empty()
    frame, provenance, raw = retrieve(lat, lon, start, end, code, api_key=api_key)
    return frame.rename(columns={"temperature_c": "value"}), provenance, raw


@st.cache_data(show_spinner=False)
def globe():
    return globe_html()


def show_table(frame):
    try:
        st.dataframe(frame, hide_index=True, width="stretch", height=300)
    except ImportError:
        st.caption("Accessible basic table view")
        st.html('<div tabindex="0" aria-label="Data table" style="overflow:auto;max-height:320px">' +
                frame.to_html(index=False, escape=True, na_rep="Missing", border=0) + '</div>')


def upload_wizard(spec, variable):
    st.subheader("Bring your data")
    st.write("Upload one location and variable, map the columns, then analyze. No coding or model training needed.")
    st.caption("CSV up to 10 MB / 100,000 rows. NetCDF, GeoTIFF and HDF require dataset-specific conversion.")
    st.download_button("Download CSV layout example (illustrative only)", "date,value\n2001-01-01,25\n2001-01-02,26\n", "illustrative_layout.csv", "text/csv")
    file = st.file_uploader("Choose a CSV file", type="csv")
    if not file:
        return None
    content = file.getvalue()
    frame = read_csv(content)
    st.write("1. Preview your file")
    show_table(frame.head(20))
    st.write("2. Map columns and units")
    a, b, c = st.columns(3)
    dc = a.selectbox("Date column", frame.columns)
    vc = b.selectbox("Value column", frame.columns, index=min(1, len(frame.columns)-1))
    units = c.selectbox("Input units", ["Celsius", "Kelvin"] if spec["code"] in {"TS", "T2M"} else [spec["units"]])
    frequency = st.selectbox("Observation frequency", ["Daily", "Monthly", "Annual"])
    st.caption("Monthly/annual values must be period means. Precipitation: mean mm/day, not totals. NDVI: quality-screened and scaled to -0.2…1.")
    fmt = st.selectbox("Date format", ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m", "%Y"])
    missing = st.text_input("Numeric missing-value marker (optional)", "-999")
    source = st.text_input("Dataset name, version and source link")
    place = st.text_input("Location represented by this file")
    resolution = st.text_input("Spatial resolution (or station / unknown)", "unknown")
    confirmed = st.checkbox("I confirm one location and quality-screened values in the selected units and frequency.")
    preview = prepare_upload(frame, dc, vc, frequency, variable, units, missing, fmt)
    st.success(f"Validated {len(preview):,} time periods: {preview.value.count():,} numeric values; {preview.value.isna().sum():,} missing. File coverage: {preview.date.min():%Y-%m-%d} to {preview.date.max():%Y-%m-%d}.")
    st.caption("The sidebar dates determine the analysis window. Select complete calendar years within this file's coverage. Values outside that window are not fitted.")
    return dict(content=content, filename=file.name, frame=frame, dc=dc, vc=vc, units=units,
                frequency=frequency, fmt=fmt, missing=missing, source=source, place=place,
                resolution=resolution, confirmed=confirmed)


def landing():
    left, right = st.columns([1, 1.2], gap="large")
    with left:
        st.html('<div class="ee-kicker">EARTH SYSTEM TREND DETECTIVE</div>')
        st.title("ECHO EARTH")
        st.write("See what changed. Understand the evidence.")
        st.caption("MIST-DREAMERS | Earth System Trend Detective | Historical analysis")
        st.html('<p class="ee-intro">Explore the Earth through its changing surface temperature, rainfall and vegetation. Start in Bangladesh, choose a record, and follow the evidence from observations to a clear result.</p>')
        if st.button("Explore Bangladesh", type="primary", width="stretch"):
            st.query_params["view"] = "explore"
            st.rerun()
        st.caption("Public NASA data · Your own CSV files · No account or paid AI key")
    with right:
        if hasattr(st, "iframe"):
            st.iframe(globe(), height=550, alt="Interactive rotating globe. Drag, zoom, pause or focus Bangladesh.")
        else:
            components.html(globe(), height=550)
    a,b,c=st.columns(3)
    a.markdown("**01 / Choose a record**\n\nA location, a variable, and a historical period.")
    b.markdown("**02 / Inspect the change**\n\nTrend magnitude, uncertainty, gaps, and source data.")
    c.markdown("**03 / Ask the evidence**\n\nCompare years and explore what the result means.")
    st.caption("Globe: locally bundled Natural Earth vector outlines. Country-wide and polygon analyses are future work.")


def run():
    st.set_page_config(page_title="ECHO EARTH", page_icon="🌍", layout="wide")
    apply_theme()
    if st.query_params.get("view") not in {"explore", "bangladesh"}:
        landing()
        return
    if "pending_location" in st.session_state:
        st.session_state.location = st.session_state.pop("pending_location")
    with st.sidebar:
        if st.button("← Back to Earth"):
            st.query_params.clear()
            st.rerun()
        st.header("Explore a trend")
        variable = st.radio("Trend type", list(VARIABLES), key="variable")
        spec = VARIABLES[variable]
        mode = st.radio("Data source", ["NASA online", "Upload CSV", "Synthetic demo"], key="mode")
        location = st.selectbox("Location", [*LOCATIONS, "Custom coordinates"], key="location")
        lat, lon = LOCATIONS.get(location, (23.8223, 90.3654))
        if location == "Custom coordinates":
            lat = st.number_input("Latitude", -90., 90., lat, format="%.4f")
            lon = st.number_input("Longitude", -180., 180., lon, format="%.4f")
        last_year = datetime.now(ZoneInfo("Asia/Dhaka")).year - 1
        minimum = date(2000,1,1) if spec["code"] == "NDVI" and mode == "NASA online" else date(1981,1,1) if mode == "NASA online" else date(1900,1,1)
        start = st.date_input("Start date", date(2001,1,1), min_value=minimum, max_value=date(last_year,12,31))
        end = st.date_input("End date", date(2024,12,31), min_value=minimum, max_value=date(last_year,12,31))
        st.text_input("NASA API Key", value="kDgGKpwj6dqqLQQpTc97W68cgC87NR7KkrMLBPwg", key="nasa_api_key", type="password")
        st.caption("✓ Active NASA Open Data API Key (api.nasa.gov)")
        st.caption("At least 10 full years required; prefer 20 or more. Requests cached for 24 hours.")
    st.header("Trend explorer")
    st.subheader(variable)
    st.caption(f"{location} · {abs(lat):.4f}° {'N' if lat >= 0 else 'S'}, {abs(lon):.4f}° {'E' if lon >= 0 else 'W'} · {start:%d %b %Y} – {end:%d %b %Y}")
    st.write(spec["note"])
    if spec["code"] == "NDVI" and mode == "NASA online":
        st.info("MODIS retrieval is slower than POWER. Download attempts have a two-minute request budget; successful batches are retained. If paused, click Analyze again to continue from cache. NASA outages produce an error, not a partial trend. You can also upload quality-screened NDVI CSV data.")
    with st.expander("Choose a point on the Bangladesh map", expanded=False):
        event = st.plotly_chart(region_map(location,lat,lon), key=f"map_{location}_{lat}_{lon}", on_select="rerun", width="stretch")
        points = event.selection.points
        if points and points[0].get("customdata") in LOCATIONS and points[0]["customdata"] != location:
            st.session_state.pending_location = points[0]["customdata"]
            st.rerun()
        st.caption("Select a city marker or use the Location selector. Orange marks your point. These are grid locations, not district averages. Basemap: OpenStreetMap contributors. Uploads use their declared location instead.")
    settings = None
    if mode == "Upload CSV":
        try:
            settings = upload_wizard(spec, variable)
        except DataError as exc:
            st.error(str(exc))
    signature = repr((variable,mode,location,lat,lon,start,end,
        {k: hashlib.sha256(v).hexdigest() if k == "content" else v for k,v in settings.items() if k != "frame"} if settings else None))
    if st.session_state.get("signature") != signature:
        st.session_state.pop("analysis",None)
        st.session_state.pop("conversation",None)
    if st.button("Analyze",type="primary",width="stretch"):
        st.session_state.pop("analysis",None)
        st.session_state.pop("conversation",None)
        try:
            if start > end:
                raise DataError("Start date must be on or before end date.")
            with st.spinner("Retrieving and screening data. Multi-year MODIS requests can take several minutes…"):
                frequency = "16-day" if spec["code"] == "NDVI" and mode == "NASA online" else "Daily"
                if mode == "NASA online":
                    user_key = st.session_state.get("nasa_api_key", "kDgGKpwj6dqqLQQpTc97W68cgC87NR7KkrMLBPwg")
                    frame, provenance, raw = nasa_data(lat, lon, start, end, spec["code"], api_key=user_key)
                elif mode == "Synthetic demo":
                    frame,provenance,raw = synthetic(start,end)
                    frame = frame.rename(columns={"temperature_c":"value"})
                    if spec["code"] == "NDVI":
                        frame["value"] = .4 + (frame.value-25)/50
                    elif spec["code"] == "PRECTOTCORR":
                        frame["value"] = np.maximum(0,frame.value-20)
                else:
                    if not settings:
                        raise DataError("Upload a CSV and map its columns first.")
                    u = settings
                    if not u["source"].strip() or not u["place"].strip() or not u["confirmed"]:
                        raise DataError("Enter the dataset source and location, then confirm the input definitions.")
                    frequency = u["frequency"]
                    frame = prepare_upload(u["frame"],u["dc"],u["vc"],frequency,variable,u["units"],u["missing"],u["fmt"])
                    provenance = upload_provenance(u["content"],u["filename"],u["source"],u["place"],frequency,
                        dict(date=u["dc"],value=u["vc"],input_units=u["units"],date_format=u["fmt"],missing_marker=u["missing"]))
                    provenance["spatial_resolution"] = u["resolution"] + " (user-declared)"
                    raw = None
                annual,processed = aggregate(frame,start,end,frequency)
                provenance.update(variable=variable,units=spec["units"],frequency=frequency,
                    requested_period=[str(start),str(end)],method_version="2.0",location=provenance.get("location",location),
                    annual_aggregation="Arithmetic mean of accepted observations; no interpolation or imputation")
                if mode != "Upload CSV":
                    provenance.update(latitude=lat,longitude=lon)
                try:
                    result,problem = analyze(annual),None
                except ValueError as exc:
                    result,problem = None,str(exc)
                st.session_state.analysis = (annual,processed,provenance,raw,result,problem,frame)
                st.session_state.signature = signature
        except (DataError,ValueError,KeyError,TypeError) as exc:
            st.error(str(exc))
            st.info("No result generated. Check the input or retry the source. Synthetic data are never substituted automatically.")
    if mode == "Synthetic demo":
        st.warning(DEMO_LABEL + ". Values do not describe the selected location.")
    if "analysis" not in st.session_state:
        st.html('<div class="ee-empty"><strong>Your evidence starts here.</strong><br>Choose a record in the sidebar and select Analyze. Your chart, uncertainty, downloads and Ask Earth conversation will appear together.</div>')
    else:
        render_result(st.session_state.analysis,variable,spec,mode,start,end)
    st.caption("Historical trends only. Mirpur waterlogging is storytelling context, not a demonstrated consequence of these trends. Forecasting is future research, outside this app.")


def render_result(bundle,variable,spec,mode,start,end):
    annual,processed,provenance,raw,result,problem,original = bundle
    label,units = provenance["source"],spec["units"]
    completeness = float(processed.value.notna().mean()) if len(processed) else 0
    st.divider()
    st.caption(f"{provenance['location']} | {variable} | requested {start.year}-{end.year} | {label}")
    if result:
        heading = ("Increasing" if result.slope > 0 else "Decreasing") + " trend detected" if result.p < .05 else "No clear monotonic trend detected"
        st.subheader(heading)
        st.caption("At the unadjusted 0.05 threshold. Read the assumptions before interpreting significance.")
    else:
        st.warning(problem)
    a,b,c,d=st.columns(4)
    a.metric("Estimated change / decade",f"{result.slope*10:+.3f} {units}" if result else "Not tested")
    b.metric("Mann-Kendall p-value",f"{result.p:.4g}" if result else "Not tested")
    c.metric("Accepted years",str(int(annual.included.sum())))
    d.metric("Observation completeness",f"{completeness:.1%}")
    st.caption(f"{processed.value.count():,} valid / {len(processed):,} expected observations. A fitted trend is not a forecast.")
    overview,evidence,data,chat=st.tabs(["Overview","Evidence","Data & downloads","Ask Earth"])
    with overview:
        accepted,rejected=annual.loc[annual.included],annual.loc[~annual.included]
        fig=go.Figure(go.Scatter(x=annual.year.tolist(),y=annual.annual_mean.where(annual.included).tolist(),mode="lines+markers",
            name="Accepted annual mean",line=dict(color="#2ca892",width=2.5),marker=dict(size=7),connectgaps=False))
        fig.add_trace(go.Scatter(x=rejected.year.tolist(),y=rejected.annual_mean.tolist(),mode="markers",name="Excluded (not fitted)",marker=dict(symbol="x",color="#d59143",size=10)))
        if result:
            fig.add_trace(go.Scatter(x=accepted.year.tolist(),y=(result.intercept+result.slope*accepted.year).tolist(),name="Theil-Sen fit",line=dict(dash="dash",color="#8b92dd",width=2)))
        fig.update_layout(xaxis_title="Calendar year",yaxis_title=f"Annual mean ({units})",legend=dict(orientation="h",y=-.2),
            height=420,margin=dict(l=20,r=20,t=20,b=40),hovermode="x unified")
        st.plotly_chart(fig,width="stretch")
        st.caption(label + ". Values are annual means; excluded years are never fitted.")
        if result:
            st.write(explanation(result,variable.lower(),units))
            st.info(f"95% slope interval: {result.low:+.5f} to {result.high:+.5f} {units}/year. This describes slope uncertainty under independence assumptions, not future values.")
    with evidence:
        st.subheader("Follow the calculation")
        st.write(f"Input cadence: {provenance['frequency']}. Annual arithmetic means; no interpolation or imputation.")
        st.write("Daily: >=90% valid days/year and >=80%/month. Monthly: all 12 means, equal weights. Annual: one supplied mean; within-year completeness unknown. MODIS: >=18/23 composites and >=3/quarter, equal weights. Partial requested years excluded.")
        st.code("S = sum(sign(value[j] - value[i])) for i < j\nslope = median((value[j] - value[i]) / (year[j] - year[i]))\np = 2 * normal_survival(abs(continuity_corrected_Z))")
        if result:
            st.write(f"{result.n} accepted years: S={result.s}, Z={result.z:.4f}, p={result.p:.6g}; 95% slope interval [{result.low:.5f}, {result.high:.5f}] {units}/year.")
            st.caption(f"Fitted years: {accepted.year.min()}-{accepted.year.max()}. Calendar gaps preserved. Detrended lag-1 correlation: {result.lag1 if result.lag1 is not None else 'undefined'}; adjacent-year pairs: {result.lag_pairs}.")
            if result.n < 20:
                st.warning("Fewer than 20 accepted years: short record for long-term interpretation.")
        st.warning("Exploratory inference: serial correlation and repeated comparisons are not corrected. Annual averaging hides seasonal changes and extremes. Missingness and dataset uncertainty can bias results. Significance is not causation.")
        st.write("Mann-Kendall uses tie-adjusted variance and continuity correction. Theil-Sen confidence limits come from SciPy. Uploaded source and quality declarations are not independently verified.")
        with st.expander("Full source and processing record"):
            st.json(provenance)
    with data:
        st.caption(label)
        show_table(annual)
        year=st.selectbox("Observation preview year",sorted(processed.date.dt.year.unique()))
        show_table(processed.loc[processed.date.dt.year==year])
        prefix="synthetic" if mode=="Synthetic demo" else "uploaded" if mode=="Upload CSV" else "nasa"
        for name,frame in [("annual",annual),("processed",processed),("source_values",original)]:
            export=frame.assign(source=label,variable=variable,units=units,location=provenance["location"])
            st.download_button(f"Download {name.replace('_',' ')} CSV",export.to_csv(index=False).encode(),f"{prefix}_{spec['code']}_{name}.csv","text/csv")
        st.download_button("Download analysis and provenance",json_bytes(dict(provenance=provenance,result=result.to_dict() if result else None,
            completeness=completeness,limitations="Unadjusted dependence and multiple comparisons; not causal or predictive")),f"{prefix}_analysis.json","application/json")
        if raw:
            st.download_button("Download original source response",json_bytes(raw),f"{prefix}_source.json","application/json")
    with chat:
        render_chat(annual,processed,provenance)


def render_chat(annual,processed,provenance):
    st.subheader("Ask Earth")
    st.write("Ask in your own words about this record: changes, year comparisons, highest or lowest years, uncertainty, gaps, sources, or methods.")
    st.caption("A local data assistant, not a general-purpose AI. It computes supported answers and explains its limits. Nothing in this conversation is sent to an external AI service.")
    conversation=st.session_state.setdefault("conversation",[])
    suggestions=st.columns(3)
    quick=None
    for col,label in zip(suggestions,["Explain this change","Which year was highest?","How certain is the trend?"]):
        if col.button(label,key="ask_"+label):
            quick=label
    def add_answer(prompt):
        answer=respond(prompt,annual,processed,provenance)
        conversation.extend([dict(role="user",text=prompt),dict(role="assistant",text=answer.text,derivation=answer.derivation)])
        del conversation[:-20]
    if quick:
        add_answer(quick)
    for item in conversation:
        with st.chat_message(item["role"]):
            st.write(item["text"])
            if item.get("derivation"):
                with st.expander("How this answer was derived"):
                    st.text(item["derivation"])
    prompt=st.chat_input("Ask about the selected change...",key="earth_chat",max_chars=1000)
    if prompt:
        add_answer(prompt)
        st.rerun()
