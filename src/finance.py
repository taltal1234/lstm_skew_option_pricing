"""Black Scholes Merton pricing, the zero curve, and the no arbitrage bounds (all vectorized numpy)."""
import numpy as np
import pandas as pd
from scipy.special import ndtr as N   # standard normal cdf, and a fast one


def contract_terms(df):
    """Spot, strike, maturity, rate and dividend yield of every row, in the order bs_price wants them."""
    return df.spot.values, df.strike.values, df.tau.values, df.r.values, df.q.values


def bs_price(S, K, tau, r, q, sigma, is_call):
    """European option price with a continuous dividend yield q."""
    sigma = np.maximum(sigma, 1e-6)
    st = sigma * np.sqrt(tau)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * tau) / st
    d2 = d1 - st
    call = S * np.exp(-q * tau) * N(d1) - K * np.exp(-r * tau) * N(d2)
    put = K * np.exp(-r * tau) * N(-d2) - S * np.exp(-q * tau) * N(-d1)
    return np.where(is_call, call, put)


def implied_vol(price, S, K, tau, r, q, is_call, iters=60):
    """Black Scholes implied volatility by bisection, for a whole array at once.

    Gives NaN where no volatility between 0.1% and 490% reproduces the price, which happens
    when the price sits at or outside the no arbitrage bounds.
    """
    price = np.asarray(price, dtype=float)
    lo, hi = np.full(price.shape, 1e-4), np.full(price.shape, 5.0)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        too_high = bs_price(S, K, tau, r, q, mid, is_call) > price
        hi = np.where(too_high, mid, hi)
        lo = np.where(too_high, lo, mid)
    iv = 0.5 * (lo + hi)
    return np.where((iv < 1e-3) | (iv > 4.9), np.nan, iv)


def forward_units(mid, S, K, tau, r, q, is_call):
    """Express prices in forward units (Black 76): the undiscounted price divided by the forward F.

    Rates and dividends then enter only through F and the discount factor, never through the
    network, so the model cannot break when rates move outside the range it saw in training.

    Returns the target y, its no arbitrage bounds, and the dollar value of one unit of y:
      Call: max(0, 1 - K/F) <= y <= 1
      Put:  max(0, K/F - 1) <= y <= K/F
      price in $ = y * F * exp(-r tau)
    """
    F = S * np.exp((r - q) * tau)
    scale = F * np.exp(-r * tau)
    k = K / F
    lower = np.where(is_call, np.maximum(0.0, 1 - k), np.maximum(0.0, k - 1))
    upper = np.where(is_call, 1.0, k)
    return mid / scale, lower, upper, scale


def zero_rate(curve, dates, days):
    """Risk free rate (decimal) for each (date, days to maturity) pair from the OptionMetrics zero curve.

    The curve is in percent and quoted at a handful of maturities, so I interpolate linearly
    between them. On a day with no curve, the latest earlier curve is used.
    """
    dates = pd.to_datetime(pd.Series(dates))
    days = np.asarray(days, dtype=float)
    curves = {d: g.sort_values("days") for d, g in curve.groupby("date")}
    curve_dates = np.array(sorted(curves), dtype="datetime64[ns]")
    out = np.full(len(dates), np.nan)
    for d, idx in dates.groupby(dates).groups.items():
        j = np.searchsorted(curve_dates, np.datetime64(d), side="right") - 1
        if j < 0:
            continue
        g = curves[pd.Timestamp(curve_dates[j])]
        out[idx] = np.interp(days[idx], g.days.values, g.rate.values)
    return out / 100.0
