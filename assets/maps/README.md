# Map display assets

Natural Earth 1:110m land and country outlines, version 5.1.2, public domain. Used for navigation and illustration, not scientific analysis or precise administrative boundaries. https://www.naturalearthdata.com/about/terms-of-use/

D3 Array 3.2.4 and D3 Geo 3.1.1: ISC-licensed bundles with their license files included. Exact download URLs and SHA-256 hashes are recorded in `manifest.json`. Regenerate using `scripts/fetch_map_assets.py`.

The globe is rendered locally from these assets. It requires no browser-side map CDN, WebGL, tile server or image-generation service. It is a vector map, not NASA satellite imagery.
