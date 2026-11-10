"""Exploration views: globe introduction and selectable Bangladesh locations."""
import plotly.graph_objects as go

LOCATIONS = {
    "Mirpur / Dhaka": (23.8223, 90.3654), "Sylhet": (24.8949, 91.8687),
    "Chattogram": (22.3569, 91.7832), "Rajshahi": (24.3745, 88.6042),
    "Khulna": (22.8456, 89.5403), "Barishal": (22.7010, 90.3535),
    "Rangpur": (25.7439, 89.2752), "Mymensingh": (24.7471, 90.4203),
}


def globe_html():
    """Self-contained canvas globe with vendored D3 and public-domain geography."""
    import json
    from pathlib import Path
    folder = Path(__file__).resolve().parents[1] / "assets" / "maps"
    countries = json.loads((folder / "countries.geojson").read_text(encoding="utf-8"))
    bangladesh = next(f for f in countries["features"] if f["properties"].get("ADMIN") == "Bangladesh")
    html = (folder / "globe.html").read_text(encoding="utf-8")
    replacements = {
        "__D3_ARRAY__": (folder / "d3-array.min.js").read_text(encoding="utf-8"),
        "__D3_GEO__": (folder / "d3-geo.min.js").read_text(encoding="utf-8"),
        "__LAND__": (folder / "land.geojson").read_text(encoding="utf-8"),
        "__BANGLADESH__": json.dumps(bangladesh),
    }
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html


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
