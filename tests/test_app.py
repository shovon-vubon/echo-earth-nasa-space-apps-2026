from streamlit.testing.v1 import AppTest


def test_demo_analysis_and_selection_invalidation():
    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert not app.exception
    app.sidebar.checkbox[0].check().run()
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert any("Illustrative synthetic data" in w.value for w in app.warning)
    assert len(app.metric) == 3
    app.text_input[0].set_value("Will it flood tomorrow?").run()
    assert any("Unsupported question" in m.value for m in app.markdown)
    app.sidebar.selectbox[0].select("Sylhet — grid location (not a basin average)").run()
    assert not app.metric


def test_invalid_dates_and_short_record():
    app = AppTest.from_file("app.py", default_timeout=30).run()
    from datetime import date
    app.sidebar.checkbox[0].check()
    app.sidebar.date_input[0].set_value(date(2024, 1, 1))
    app.sidebar.date_input[1].set_value(date(2023, 1, 1))
    app.sidebar.button[0].click().run()
    assert app.error
    app.sidebar.date_input[1].set_value(date(2024, 12, 31))
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert any("At least 10" in w.value for w in app.warning)
