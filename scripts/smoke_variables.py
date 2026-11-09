"""Live source validation: writes only ignored local verification data."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.data import retrieve, json_bytes
from src.vegetation import retrieve_ndvi
from src.workflows import aggregate
from src.trends import analyze

folder=Path("data/cache")
folder.mkdir(parents=True,exist_ok=True)
for code in ["TS","PRECTOTCORR","NDVI"]:
    start,end="2010-01-01","2024-12-31"
    if code == "NDVI":
        frame,provenance,raw=retrieve_ndvi(23.8223,90.3654,start,end,
            progress=lambda v: print(f"MODIS retrieval {v:.0%}",flush=True))
        cadence="16-day"
    else:
        frame,provenance,raw=retrieve(23.8223,90.3654,start,end,code)
        frame=frame.rename(columns={"temperature_c":"value"})
        cadence="Daily"
    annual,processed=aggregate(frame,start,end,cadence)
    frame.to_csv(folder/f"{code}_source.csv",index=False)
    annual.to_csv(folder/f"{code}_annual.csv",index=False)
    (folder/f"{code}_raw.json").write_bytes(json_bytes(raw))
    (folder/f"{code}_provenance.json").write_bytes(json_bytes(provenance))
    try:
        result=analyze(annual).to_dict()
    except ValueError as exc:
        result={"not_tested":str(exc)}
    print(json_bytes(dict(variable=code,valid=int(processed.value.count()),expected=len(processed),
                          accepted_years=int(annual.included.sum()),result=result)).decode(),flush=True)
