import numpy as np
import pandas as pd
import pytest
from src.data import parse_power, DataError
from src.preprocessing import annualize
from src.trends import analyze
from src.questions import answer


def series(years, values):
    return pd.DataFrame(dict(year=years, mean_temperature_c=values, included=True))


def test_known_linear_trend_and_actual_year_gaps():
    years = np.array([2000, 2001, 2002, 2004, 2005, 2007, 2008, 2010, 2011, 2015])
    r = analyze(series(years, 20 + .2 * (years - 2000)))
    assert r.slope == pytest.approx(.2)
    assert r.low == pytest.approx(.2)
    assert r.high == pytest.approx(.2)
    assert r.s == 45
    assert r.p == pytest.approx(.000083031070, rel=1e-5)


def test_constant_and_decreasing():
    years = np.arange(2000, 2020)
    r = analyze(series(years, np.ones(20)))
    assert (r.p, r.slope, r.low, r.high) == (1., 0., 0., 0.)
    assert r.lag1 is None
    assert analyze(series(years, -years)).direction == "decreasing"


def test_ties_and_exclusions():
    a = series(np.arange(2000, 2012), np.repeat([1., 2., 3., 4., 5., 6.], 2))
    a.loc[11, "included"] = False
    r = analyze(a)
    assert r.n == 11
    assert r.s == 50
    with pytest.raises(ValueError, match="At least 10"):
        analyze(a.iloc[:9])


def test_leap_partial_and_seasonal_missingness():
    dates = pd.date_range("2000-01-01", "2002-06-30")
    d = pd.DataFrame(dict(date=dates, temperature_c=25.))
    d.loc[(d.date.dt.year == 2001) & (d.date.dt.month == 6), "temperature_c"] = np.nan
    a = annualize(d, dates.min(), dates.max())
    assert a.iloc[0].expected_days == 366
    assert bool(a.iloc[0].included)
    assert a.iloc[1].completeness > .9
    assert a.iloc[1].reason == "at least one month below 80% completeness"
    assert a.iloc[2].reason == "partial calendar year"


def test_fill_missing_dates_invalid_units_and_empty():
    payload = {"header": {"fill_value": -999}, "parameters": {"T2M": {"units": "C"}},
               "properties": {"parameter": {"T2M": {"20000101": 25, "20000103": -999}}}}
    d = parse_power(payload, "2000-01-01", "2000-01-03")
    assert d.temperature_c.isna().sum() == 2
    payload["parameters"]["T2M"]["units"] = "K"
    with pytest.raises(DataError, match="units"):
        parse_power(payload, "2000-01-01", "2000-01-03")
    with pytest.raises(DataError):
        parse_power({}, "2000-01-01", "2000-01-03")


def test_unsupported_question_does_not_guess():
    assert answer("Will it flood tomorrow?", None, {}, 1).startswith("Unsupported")
