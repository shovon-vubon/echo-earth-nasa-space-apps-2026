"""Exploration views: globe introduction and selectable Bangladesh locations."""
import plotly.graph_objects as go

LOCATIONS = {
    "Mirpur / Dhaka": (23.8223, 90.3654), "Sylhet": (24.8949, 91.8687),
    "Chattogram": (22.3569, 91.7832), "Rajshahi": (24.3745, 88.6042),
    "Khulna": (22.8456, 89.5403), "Barishal": (22.7010, 90.3535),
    "Rangpur": (25.7439, 89.2752), "Mymensingh": (24.7471, 90.4203),
}


def globe_html():
    fig = go.Figure(go.Scattergeo(lat=[23.7], lon=[90.35], text=["Explore Bangladesh"],
                                 mode="markers+text", textposition="top center",
                                 marker=dict(size=12, color="#56E0C4"), textfont=dict(color="white")))
    fig.update_geos(projection_type="orthographic", projection_rotation=dict(lon=70, lat=15),
                    showland=True, landcolor="#257065", showocean=True, oceancolor="#102F48",
                    showcountries=True, countrycolor="#71A39A", coastlinecolor="#71A39A",
                    bgcolor="#071C29", lataxis_showgrid=True, lonaxis_showgrid=True)
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#071C29")
    # User-activated navigation carries no data; the ordinary Streamlit button is the accessible fallback.
    script = """
    const g=document.getElementById('{plot_id}');
    let lon=70, stopped=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    g.on('plotly_click',()=>{stopped=true; window.open('?view=bangladesh','_top');});
    g.addEventListener('pointerdown',()=>stopped=true);
    const timer=setInterval(()=>{if(!stopped){lon+=0.25;Plotly.relayout(g,{'geo.projection.rotation.lon':lon});}},150);
    window.addEventListener('pagehide',()=>clearInterval(timer));
    """
    return fig.to_html(full_html=True, include_plotlyjs=True, post_script=script,
                       config={"displayModeBar": False, "scrollZoom": False, "responsive": True})


def region_map(location, lat, lon):
    fig = go.Figure(go.Scattermap(lat=[v[0] for v in LOCATIONS.values()],
                                 lon=[v[1] for v in LOCATIONS.values()],
                                 text=list(LOCATIONS), customdata=list(LOCATIONS),
                                 mode="markers", marker=dict(size=13, color="#087F8C"),
                                 hovertemplate="%{text}<extra>Select location</extra>"))
    fig.add_trace(go.Scattermap(lat=[lat], lon=[lon], text=[location], mode="markers",
                               marker=dict(size=18, color="#E67928"), name="Selected point"))
    fig.update_layout(map=dict(style="open-street-map", center=dict(lat=lat, lon=lon), zoom=8),
                      height=340, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
                      clickmode="event+select")
    return fig
