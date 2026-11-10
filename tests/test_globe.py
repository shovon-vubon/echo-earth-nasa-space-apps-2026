from src.maps import globe_html, region_map


def test_globe_is_local_interactive_and_accessible():
    html=globe_html()
    assert "__LAND__" not in html
    assert '<script src=' not in html
    for token in ["requestAnimationFrame", "pointermove", "prefers-reduced-motion", "geoOrthographic", "Focus Bangladesh", "ArrowLeft"]:
        assert token in html
    assert 'href="?view=explore"' in html


def test_map_centres_on_selection():
    fig=region_map("Sylhet",24.8949,91.8687)
    assert fig.layout.map.center.lat==24.8949
    assert fig.layout.map.center.lon==91.8687
    assert fig.layout.map.zoom==8
