from pathlib import Path
from unittest.mock import patch
import io
import streamlit as st
from streamlit.testing.v1 import AppTest
APP = str(Path(__file__).resolve().parents[1] / "app.py")


def launch():
    return AppTest.from_file(APP, default_timeout=30).run()


def click_analyze(app):
    next(b for b in app.button if b.label == "Analyze").click().run()
    return app


def test_demo_switching_and_ask():
    app=launch()
    assert not app.exception
    app.sidebar.radio[1].set_value("Synthetic demo").run()
    click_analyze(app)
    assert not app.exception and len(app.metric)==3
    app.text_input[0].set_value("Will it flood tomorrow?").run()
    assert any("Unsupported" in e.value for e in app.info)
    app.sidebar.radio[0].set_value("Rainfall / precipitation").run()
    assert not app.metric
    click_analyze(app)
    assert not app.exception
    assert any("mm/day/year" in m.value for m in app.markdown)


def test_bad_dates_and_source_failure(monkeypatch):
    import requests
    from datetime import date
    st.cache_data.clear()
    def unavailable(*args,**kwargs):
        raise requests.ConnectionError("offline test")
    monkeypatch.setattr(requests,"get",unavailable)
    app=launch()
    click_analyze(app)
    assert app.error and not app.metric and not app.exception
    app.sidebar.date_input[0].set_value(date(2024,1,1))
    app.sidebar.date_input[1].set_value(date(2023,1,1))
    click_analyze(app)
    assert any("Start date" in e.value for e in app.error)


def test_upload_wizard_end_to_end():
    content="date,value\n"+"\n".join(f"{y}-01-01,{20+(y-2001)*.1}" for y in range(2001,2025))
    class File(io.BytesIO):
        name="annual.csv"
        def getvalue(self): return content.encode()
    with patch("streamlit.file_uploader",return_value=File()):
        app=launch()
        app.sidebar.radio[1].set_value("Upload CSV").run()
        assert not app.exception
        next(s for s in app.selectbox if s.label=="Observation frequency").set_value("Annual")
        next(t for t in app.text_input if t.label=="Dataset name, version and source link").set_value("Test observations")
        next(t for t in app.text_input if t.label=="Location represented by this file").set_value("Sylhet station")
        next(c for c in app.checkbox if c.label.startswith("I confirm")).check()
        click_analyze(app)
        assert not app.exception and len(app.metric)==3
        assert any("User-provided data" in m.value for m in app.markdown)
        assert any("Sylhet station" in s.value for s in app.subheader)


def test_globe_navigation():
    app=launch()
    next(b for b in app.button if b.label=="Explore Bangladesh").click().run()
    assert not app.exception
    assert app.query_params["view"]==["bangladesh"]
