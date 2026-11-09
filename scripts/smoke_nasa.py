"""Opt-in real integration check; run from the repository root."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import retrieve, json_bytes
from src.preprocessing import annualize
from src.trends import analyze

daily, provenance, raw = retrieve(23.8223, 90.3654, "2001-01-01", "2024-12-31")
annual = annualize(daily, "2001-01-01", "2024-12-31")
result = analyze(annual)
target = Path("data/cache")
target.mkdir(parents=True, exist_ok=True)
(target / "nasa_power_raw.json").write_bytes(json_bytes(raw))
(target / "nasa_power_provenance.json").write_bytes(json_bytes(provenance))
annual.to_csv(target / "nasa_power_annual.csv", index=False)
print(json_bytes({"daily_rows": len(daily), "valid_daily": int(daily.temperature_c.count()),
                  "source": provenance["source"], "result": result.to_dict()}).decode())
