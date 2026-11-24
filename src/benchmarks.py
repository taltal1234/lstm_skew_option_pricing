"""Benchmark prices the networks are compared with.

bs_20   Black Scholes with a constant 20% volatility (the original paper's benchmark)
bs_rv   Black Scholes with the trailing 22 day realized volatility from 5 minute returns
bs_vix  Black Scholes with VIX as the volatility
ahbs    "ad hoc" Black Scholes of Dumas, Fleming and Whaley (1998): regress yesterday's implied
        vols on moneyness and maturity, then price today with the fitted surface. This is what
        practitioners actually use, and it is hard to beat.

prev_smile() gives every option on day t the implied vol that yesterday's fitted surface assigns
to it (iv_prev) and the matching price in forward units (y_prev). The ad hoc benchmark is that
same price in dollars, and the "LSTM + yesterday's smile" networks take both as inputs.
"""
import numpy as np
import pandas as pd
from src.finance import bs_price, contract_terms

COEFS = [f"b{i}" for i in range(6)]


def surface_terms(m, tau):
    """Regressors of the ad hoc surface: 1, m, m^2, tau, m tau, tau^2 (m = K/S)."""
    return np.column_stack([np.ones_like(m), m, m ** 2, tau, m * tau, tau ** 2])


def ahbs_coefficients(options):
    """One implied vol surface regression per day, fitted separately for calls and puts."""
    o = options.dropna(subset=["impl_volatility"])
    o = o[o.impl_volatility > 0]
    rows = []
    for (date, cp), g in o.groupby(["date", "cp_flag"]):
        if len(g) < 10:
            continue
        m = (g.strike / g.spot).values
        beta, *_ = np.linalg.lstsq(surface_terms(m, g.tau.values), g.impl_volatility.values, rcond=None)
        rows.append([date, cp, *beta])
    return pd.DataFrame(rows, columns=["date", "cp_flag"] + COEFS)


def prev_smile(df, market, options):
    """Yesterday's fitted smile evaluated at each of today's contracts.
    Adds iv_prev (a volatility) and y_prev (a price in forward units, the target's units)."""
    coef = ahbs_coefficients(options)
    days = np.sort(market.date.unique())
    next_day = pd.Series(days[1:], index=days[:-1])
    coef["date"] = coef.date.map(next_day)              # the fit from yesterday is used today
    df = df.merge(coef.dropna(subset=["date"]), on=["date", "cp_flag"], how="left")
    S, K, tau, r, q = contract_terms(df)
    df["iv_prev"] = np.clip(np.sum(surface_terms(K / S, tau) * df[COEFS].values, axis=1), 0.03, 2.0)
    price = bs_price(S, K, tau, r, q, df.iv_prev.values, df.cp_flag.values == "C")
    df["y_prev"] = price / (S * np.exp(-q * tau))        # forward units: price / (F exp(-r tau))
    return df.drop(columns=COEFS)


def add_benchmarks(df, market, options):
    """df: the option rows to price. market: the daily table. options: the full panel (for yesterday's surface)."""
    df = df.merge(market[["date", "vix", "rv_vol"]], on="date", how="left")
    S, K, tau, r, q = contract_terms(df)
    call = df.cp_flag.values == "C"

    df["bs_20"] = bs_price(S, K, tau, r, q, 0.20, call)
    df["bs_rv"] = bs_price(S, K, tau, r, q, df.rv_vol.values, call)
    df["bs_vix"] = bs_price(S, K, tau, r, q, df.vix.values, call)

    if "iv_prev" not in df:
        df = prev_smile(df, market, options)
    df["ahbs"] = bs_price(S, K, tau, r, q, df.iv_prev.values, call)
    return df
