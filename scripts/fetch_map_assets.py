"""Download public map data and pinned D3 bundles for the offline globe."""
from pathlib import Path
import hashlib
import json
import requests

ROOT = Path(__file__).resolve().parents[1] / "assets" / "maps"
FILES = {
    "land.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_land.geojson",
    "countries.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/ne_110m_admin_0_countries.geojson",
    "d3-array.min.js": "https://cdn.jsdelivr.net/npm/d3-array@3.2.4/dist/d3-array.min.js",
    "d3-geo.min.js": "https://cdn.jsdelivr.net/npm/d3-geo@3.1.1/dist/d3-geo.min.js",
    "d3-array-LICENSE": "https://cdn.jsdelivr.net/npm/d3-array@3.2.4/LICENSE",
    "d3-geo-LICENSE": "https://cdn.jsdelivr.net/npm/d3-geo@3.1.1/LICENSE",
}
if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, url in FILES.items():
        r = requests.get(url, timeout=(10,60))
        r.raise_for_status()
        (ROOT/name).write_bytes(r.content)
        manifest[name] = dict(url=url, sha256=hashlib.sha256(r.content).hexdigest())
        print(name, len(r.content), flush=True)
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
