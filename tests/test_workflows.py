import pandas as pd
import numpy as np
import pytest
from src.workflows import prepare_upload, aggregate, read_csv
from src.vegetation import parse_subset, NDVI, QUALITY
from src.data import DataError, parse_power
from src.trends import analyze, explanation


def test_kelvin_missing_and_duplicate_upload():
    f = pd.DataFrame({"date":["2001-01-01","2001-01-02"],"v":[300,-999]})
    d = prepare_upload(f,"date","v","Daily","Surface temperature","Kelvin","-999","%Y-%m-%d")
    assert d.value.iloc[0] == pytest.approx(26.85)
    assert pd.isna(d.value.iloc[1])
    with pytest.raises(DataError,match="Duplicate"):
        prepare_upload(pd.concat([f,f]),"date","v","Daily","Surface temperature","Kelvin","-999","%Y-%m-%d")


def test_bad_dates_units_and_upload_size():
    f = pd.DataFrame({"date":["not a date"],"v":[4]})
    with pytest.raises(DataError,match="date values"):
        prepare_upload(f,"date","v","Daily","Vegetation","NDVI","","%Y-%m-%d")
    f["date"] = "2001-01-01"
    with pytest.raises(DataError,match="physical range"):
        prepare_upload(f,"date","v","Daily","Vegetation","NDVI","","%Y-%m-%d")
    with pytest.raises(DataError,match="10 MB"):
        read_csv(b"x" * (10*1024*1024+1))


def test_monthly_yearly_aggregation_and_units():
    dates = pd.date_range("2001-01-01","2012-12-01",freq="MS")
    f = pd.DataFrame({"date":dates,"value":dates.year-2000.})
    a,p = aggregate(f,"2001-01-01","2012-12-31","Monthly")
    assert analyze(a).slope == 1
    assert "mm/day/year" in explanation(analyze(a),"precipitation","mm/day")
    a,_ = aggregate(f.drop(index=2),"2001-01-01","2012-12-31","Monthly")
    assert not a.iloc[0].included
    assert a.iloc[0].valid_observations == 11


def test_modis_quality_scaling_and_coverage():
    records=[]
    for day,raw,q in [("2001-01-01",5000,0),("2001-01-17",6000,1),("2001-02-02",7000,3)]:
        records.extend([dict(calendar_date=day,band=NDVI,data=[raw]),dict(calendar_date=day,band=QUALITY,data=[q])])
    f=parse_subset(dict(nrows=1,ncols=1,subset=records))
    assert list(f.value[:2]) == [.5,.6]
    assert np.isnan(f.value.iloc[2])
    a,p=aggregate(f,"2001-01-01","2001-12-31","16-day")
    assert len(p)==23 and not a.iloc[0].included


def test_power_new_variable_units():
    p=dict(header=dict(fill_value=-999),parameters={"PRECTOTCORR":dict(units="mm/day")},
           properties=dict(parameter={"PRECTOTCORR":{"20010101":12}}))
    assert parse_power(p,"2001-01-01","2001-01-01","PRECTOTCORR").iloc[0].temperature_c==12
