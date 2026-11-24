"""Daily realized moments of the underlying.

Intraday version (the one used in the paper), following Amaya, Christoffersen, Jacobs and Vasquez (2015):
    RV_t   = sum r_i^2
    RSk_t  = sqrt(N) * sum r_i^3 / RV_t^(3/2)
    RKu_t  = N * sum r_i^4 / RV_t^2
where r_i are the N intraday 5 minute log returns of day t.
"""
import numpy as np
import pandas as pd

MIN_BARS = 30    # fewer returns than this means a broken day (half days still have 42 bars)


def clean_bars(bars, max_jump=0.01):
    """Drop isolated bad prints: a bar more than max_jump (in logs) away from the median of
    its neighbours that day. One bad print would otherwise dominate the day's skewness."""
    bars = bars.sort_values(["date", "bar"]).copy()
    med = bars.groupby("date")["price"].transform(
        lambda p: p.rolling(5, center=True, min_periods=1).median())
    keep = np.abs(np.log(bars["price"] / med)) <= max_jump
    return bars[keep]


def intraday_moments(bars):
    """bars has columns date, bar, price (bar 0 is the first trade after 09:30)."""
    bars = clean_bars(bars)
    bars["r"] = bars.groupby("date")["price"].transform(lambda p: np.log(p).diff())
    r = bars.dropna(subset=["r"])
    g = r.assign(r2=r.r ** 2, r3=r.r ** 3, r4=r.r ** 4).groupby("date")
    out = pd.DataFrame({
        "n": g["r"].count(),
        "rv": g["r2"].sum(),
        "s3": g["r3"].sum(),
        "s4": g["r4"].sum(),
    })
    out["rskew"] = np.sqrt(out.n) * out.s3 / out.rv ** 1.5
    out["rkurt"] = out.n * out.s4 / out.rv ** 2

    # overnight return: today's first trade against yesterday's last one
    day = bars.groupby("date")["price"].agg(open_px="first", close_px="last")
    out = out.join(day)
    out["ret_overnight"] = np.log(out.open_px / out.close_px.shift(1))
    out = out[out.n >= MIN_BARS]
    return out[["rv", "rskew", "rkurt", "ret_overnight"]].reset_index()


def daily_moments(spx, window=22):
    """Fallback when there is no TAQ data: rolling moments of daily returns
    (what the original paper did, but here on real SPX data)."""
    df = spx.sort_values("date").copy()
    r = np.log(df.close).diff()
    df["rv"] = r ** 2
    df["rskew"] = r.rolling(window).skew()
    df["rkurt"] = r.rolling(window).kurt() + 3
    df["ret_overnight"] = 0.0
    return df[["date", "rv", "rskew", "rkurt", "ret_overnight"]].dropna()
