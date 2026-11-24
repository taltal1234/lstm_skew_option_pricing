"""Write SYNTHETIC files in exactly the layout 01_download_wrds.py produces, so the whole
pipeline can be tested without a WRDS login (GitHub Actions runs this on every push).
The numbers are made up. Never report results from them.

    SMOKE_TEST=1 python tests/make_mock_data.py
    then steps 2 to 4 with SMOKE_TEST=1, or simply: bash tests/smoke_test.sh
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root
import config as C
from src.finance import bs_price

assert os.environ.get("SMOKE_TEST"), "run with SMOKE_TEST=1 so real data folders are untouched"
rng = np.random.default_rng(0)
C.RAW_DIR.mkdir(parents=True, exist_ok=True)

# trading days and a daily variance process with leverage
days = pd.bdate_range(f"{C.START_YEAR - 1}-01-01", f"{C.END_YEAR}-12-31")
n, nb = len(days), 78
logv = np.empty(n)
logv[0] = np.log(0.15 ** 2)
shock = rng.standard_normal(n)
for t in range(1, n):
    logv[t] = logv[t - 1] + 0.03 * (np.log(0.17 ** 2) - logv[t - 1]) + 0.12 * shock[t]
v = np.exp(logv)

# 5 minute returns: diffusion plus occasional negative jumps (gives negative realized skew)
r5 = rng.standard_normal((n, nb)) * np.sqrt(v[:, None] / (252 * nb))
jumps = (rng.random((n, nb)) < 0.0006) * rng.normal(-0.004, 0.002, (n, nb))
r5 += jumps + 0.0004 / nb
overnight = rng.standard_normal(n) * np.sqrt(v / 252) * 0.4
log_open = np.cumsum(overnight + np.r_[0, r5[:-1].sum(1)]) + np.log(1800)
logp = log_open[:, None] + np.cumsum(r5, axis=1)
close = np.exp(logp[:, -1])

bars = []
for t, d in enumerate(days):
    if d.year < C.START_YEAR - 1:
        continue
    b = pd.DataFrame({"bar": np.r_[0, np.arange(114, 114 + nb)],
                      "price": np.exp(np.r_[log_open[t], logp[t]]) / 10, "date": d})
    bars.append(b)
bars = pd.concat(bars)
for (y, m), g in bars.groupby([bars.date.dt.year, bars.date.dt.month]):
    g[["bar", "price", "date"]].to_parquet(C.RAW_DIR / f"taq_SPY_{y}_{m:02d}.parquet", index=False)

spx = pd.DataFrame({"date": days, "open": np.exp(log_open), "high": close, "low": close,
                    "close": close, "return": np.r_[np.nan, np.diff(np.log(close))]})
spx.to_parquet(C.RAW_DIR / "spx.parquet", index=False)
pd.DataFrame({"date": days, "vix": 100 * np.sqrt(v) * 1.15}).to_parquet(C.RAW_DIR / "vix.parquet", index=False)
pd.DataFrame({"date": days, "rate": 1.9}).to_parquet(C.RAW_DIR / "divyield.parquet", index=False)
zc = pd.DataFrame([(d, k, 0.5 + 0.004 * k ** 0.5 * 10 + 1.0 * (d.year >= 2017)) for d in days
                   for k in [7, 30, 91, 182, 365, 730]], columns=["date", "days", "rate"])
zc.to_parquet(C.RAW_DIR / "zerocd.parquet", index=False)

# realized skew of the last 22 days drives the smile slope, so the moments carry signal
rsk = pd.Series((r5 ** 3).sum(1) * np.sqrt(nb) / (r5 ** 2).sum(1) ** 1.5).rolling(22, 1).mean().values
oid = 0
for year in range(C.START_YEAR, C.END_YEAR + 1):
    rows = []
    for t in np.where(days.year == year)[0]:
        d, S = days[t], close[t]
        fridays = pd.date_range(d, d + pd.Timedelta(days=200), freq="WOM-3FRI")[:5]
        for ex in fridays:
            tau = (ex - d).days / 365
            if tau * 365 < 7:
                continue
            K = np.unique(np.round(S * np.linspace(0.82, 1.18, 13) / 5) * 5)
            m = np.log(K / S)
            iv = np.sqrt(v[t]) * 1.1 - (0.25 - 0.08 * rsk[t]) * m / np.sqrt(max(tau, 0.05)) * 0.3 + 0.6 * m ** 2
            iv = np.clip(iv, 0.05, 1.5)
            for cp in "CP":
                p = bs_price(S, K, tau, 0.015, 0.019, iv, cp == "C") * np.exp(rng.normal(0, 0.02, len(K)))
                half = np.maximum(0.05, 0.03 * p)
                for k, pi, h, s in zip(K, p, half, iv):
                    oid += 1
                    rows.append((d, ex, cp, int(k * 1000), max(pi - h, 0.05), pi + h, rng.integers(0, 500),
                                 1000, s, oid, f"SPX {ex:%y%m%d}{cp}{int(k)}", 1, None, np.nan, S))
    df = pd.DataFrame(rows, columns=["date", "exdate", "cp_flag", "strike_price", "best_bid", "best_offer",
                                     "volume", "open_interest", "impl_volatility", "optionid", "symbol",
                                     "am_settlement", "expiry_indicator", "forward_price", "spot"])
    df.to_parquet(C.RAW_DIR / f"options_{year}.parquet", index=False)
    print(year, len(df), "mock option rows")
print("mock data written to", C.RAW_DIR)
