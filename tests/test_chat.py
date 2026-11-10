import pandas as pd
import pytest
from src.chat import respond
from src.workflows import aggregate


@pytest.fixture
def context():
    dates=pd.date_range("2001-01-01","2024-12-31",freq="D")
    f=pd.DataFrame(dict(date=dates,value=20+(dates.year-2001)*.1))
    annual,processed=aggregate(f,"2001-01-01","2024-12-31")
    provenance=dict(variable="Surface temperature",units="°C",location="Sylhet",
                    source="Test observations",frequency="Daily")
    return annual,processed,provenance


def test_year_comparison_is_calculated(context):
    r=respond("Compare 2005 and 2020",*context)
    assert "+1.5000" in r.text
    assert "20.4000" in r.text
    assert "endpoint" in r.derivation


def test_trend_recalculated_and_explained(context):
    r=respond("Is the temperature increasing?",*context)
    assert "+0.1000" in r.text and "Recomputed analyze()" in r.derivation
    r=respond("How certain is this change?",*context)
    assert "95%" in r.text and "not a probability" in r.text


def test_missing_year_and_cross_variable_never_invented(context):
    assert "No accepted" in respond("What about 1995?",*context).text
    assert "Switch the trend type" in respond("Is rainfall increasing?",*context).text
    assert "loaded record" in respond("Compare with Dhaka",*context).text


def test_causes_forecasts_and_unknown_questions(context):
    assert "cannot establish why" in respond("Why is it getting hotter?",*context).text
    assert "cannot predict" in respond("Predict 2030",*context).text
    assert "cannot answer" in respond("Write me a poem",*context).text


def test_extremes_gaps_and_subperiod(context):
    assert "2024" in respond("Which was the hottest year?",*context).text
    assert "100.0%" in respond("Are there gaps?",*context).text
    assert "n=15" in respond("Trend between 2010 and 2024",*context).derivation
    assert "At least 10" in respond("Trend between 2020 and 2024",*context).text


def test_excluded_endpoints_not_used(context):
    a,p,s=context
    a.loc[a.year==2005,"included"]=False
    assert "No accepted" in respond("Compare 2005 and 2020",a,p,s).text


def test_monthly_or_causal_claims_are_not_faked(context):
    assert "does not test seasonal" in respond("Is the monsoon changing?",*context).text


def test_all_missing_record_has_useful_reply(context):
    a,p,s=context
    a["included"]=False
    assert "No years" in respond("Which year was highest?",a,p,s).text
