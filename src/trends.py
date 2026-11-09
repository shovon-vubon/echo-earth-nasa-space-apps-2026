"""Classical two-sided Mann–Kendall and actual-calendar-year Theil–Sen."""
from dataclasses import dataclass, asdict
import numpy as np
from scipy.stats import norm, theilslopes


@dataclass
class Trend:
    n: int
    slope: float
    intercept: float
    low: float
    high: float
    p: float
    s: int
    z: float
    direction: str
    lag1: float | None
    lag_pairs: int

    def to_dict(self):
        return asdict(self)


def analyze(annual):
    valid = annual.loc[annual.included].sort_values("year")
    x = valid.year.to_numpy(dtype=float)
    y = valid.mean_temperature_c.to_numpy(dtype=float)
    if len(y) < 10:
        raise ValueError("At least 10 accepted complete calendar years are needed; select a longer period.")
    if not np.isfinite(y).all() or len(set(x)) != len(x):
        raise ValueError("Trend inputs must have unique years and finite annual means.")
    n = len(y)
    s = int(sum(np.sign(y[i + 1:] - y[i]).sum() for i in range(n - 1)))
    _, ties = np.unique(y, return_counts=True)
    variance = (n * (n - 1) * (2 * n + 5) - np.sum(ties * (ties - 1) * (2 * ties + 5))) / 18
    z = (s - np.sign(s)) / np.sqrt(variance) if variance > 0 else 0.0
    p = float(2 * norm.sf(abs(z)))
    slope, intercept, low, high = theilslopes(y, x, alpha=.95)
    residuals = y - (intercept + slope * x)
    consecutive = np.diff(x) == 1
    a, b = residuals[:-1][consecutive], residuals[1:][consecutive]
    lag1 = None
    if len(a) >= 3 and np.std(a) > 1e-10 and np.std(b) > 1e-10:
        lag1 = float(np.corrcoef(a, b)[0, 1])
    return Trend(n, float(slope), float(intercept), float(low), float(high), p,
                 s, float(z), "increasing" if slope > 0 else "decreasing" if slope < 0 else "flat",
                 lag1, len(a))


def explanation(result):
    evidence = "evidence of a monotonic trend" if result.p < .05 else "insufficient evidence of a monotonic trend"
    return (f"The estimated annual-mean temperature trend is {result.direction}: "
            f"{result.slope:+.4f} °C/year ({result.slope * 10:+.3f} °C/decade). "
            f"The 95% slope confidence interval is {result.low:+.4f} to {result.high:+.4f} °C/year. "
            f"Across {result.n} accepted years, the unadjusted Mann–Kendall p-value is {result.p:.4g}: "
            f"{evidence} at α = 0.05 under the test assumptions. "
            "Statistical significance does not establish causation or predict a flood.")
