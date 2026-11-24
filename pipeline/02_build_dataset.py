"""Step 2: clean the option panel, compute the realized moments, merge everything.

Outputs (data/processed/)
    market.parquet   one row per trading day: returns, realized moments, VIX, rates
    options.parquet  one row per option per day: contract terms, mid price, no arbitrage bounds
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so config and src can be imported

import numpy as np
import pandas as pd
import config as C
from src.utils import read_raw
from src.finance import forward_units, zero_rate
from src.realized import intraday_moments, daily_moments

OPTION_COLUMNS = ["date", "exdate", "optionid", "cp_flag", "is_call", "strike", "spot", "mid",
                  "best_bid", "best_offer", "volume", "impl_volatility", "dte", "tau", "sqrt_tau",
                  "r", "q", "forward", "log_mny", "lower", "upper", "scale", "y"]


def raw(name):
    return read_raw(C.RAW_DIR / name)


def realized_moments(spx):
    """From SPY 5 minute bars when the TAQ files are there, otherwise from daily SPX returns."""
    taq_files = sorted(C.RAW_DIR.glob(f"taq_{C.TAQ_SYMBOL}_*.parquet"))
    if not taq_files:
        print("no TAQ files found: using rolling daily return moments (fallback)")
        return daily_moments(spx)
    bars = pd.concat([read_raw(f) for f in taq_files], ignore_index=True)
    moments = intraday_moments(bars)
    print(f"realized moments from TAQ {C.BAR_MINUTES} minute bars: {len(moments):,} days")
    return moments


def build_market(zero_curve):
    spx = raw("spx.parquet").sort_values("date")
    spx = spx[spx.close > 0]
    spx["ret"] = np.log(spx.close).diff()
    moments = realized_moments(spx)

    vix = raw("vix.parquet")
    vix["vix"] = vix.vix / 100.0
    dividend = raw("divyield.parquet").rename(columns={"rate": "q"})
    dividend["q"] = dividend.q / 100.0

    m = spx[["date", "close", "ret"]].merge(moments, on="date", how="inner")
    m = m.merge(vix, on="date", how="left").merge(dividend, on="date", how="left")
    m[["vix", "q"]] = m[["vix", "q"]].ffill()
    m["rf_3m"] = zero_rate(zero_curve, m.date.values, np.full(len(m), 91))
    m["rf_3m"] = m.rf_3m.ffill()
    m["log_rv"] = np.log(m.rv + 1e-10)
    # annualized trailing realized vol, only used by the BS(RV) benchmark
    m["rv_vol"] = np.sqrt(252 * m.rv.rolling(C.RV_WINDOW).mean())
    return m.dropna().reset_index(drop=True)


def filter_quotes(df):
    """Apply the option filters from config.py to one year of raw quotes
    (one year at a time keeps the memory use low)."""
    df["strike"] = df.strike_price / 1000.0            # OptionMetrics stores strike times 1000
    df["mid"] = (df.best_bid + df.best_offer) / 2
    df["dte"] = (df.exdate - df.date).dt.days
    df["tau"] = df.dte / 365.0
    df["is_call"] = (df.cp_flag == "C").astype(float)

    keep = df.cp_flag.isin(C.CP_FLAGS)
    if C.STANDARD_EXPIRIES_ONLY:
        if "expiry_indicator" in df:
            keep &= df.expiry_indicator == ""
        elif "symbol" in df:
            keep &= ~df.symbol.str.startswith("SPXW")
        if "am_settlement" in df:
            keep &= df.am_settlement.fillna(1) == 1
    keep &= df.dte.between(C.MIN_DTE, C.MAX_DTE)
    keep &= (df.strike / df.spot).between(C.MIN_MONEY, C.MAX_MONEY)
    keep &= df.mid >= C.MIN_MID
    keep &= (df.best_offer - df.best_bid) / df.mid <= C.MAX_REL_SPREAD
    if C.REQUIRE_VOLUME:
        keep &= df.volume > 0
    return df[keep]


def filtered_quotes():
    """All years of quotes after the filters. Kept in its own function so the raw yearly files
    (several million rows each) are freed as soon as they are filtered."""
    n_downloaded, parts = 0, []
    for f in sorted(C.RAW_DIR.glob("options_*.parquet")):
        quotes = read_raw(f)
        n_downloaded += len(quotes)
        parts.append(filter_quotes(quotes))
        print(f"  {f.name}: {len(quotes):,} quotes -> {len(parts[-1]):,} kept")
    return pd.concat(parts, ignore_index=True), n_downloaded


def build_options(market, zero_curve):
    df, n_downloaded = filtered_quotes()

    # every option gets the zero rate for its own maturity and the day's dividend yield
    df["r"] = zero_rate(zero_curve, df.date.values, df.dte.values)
    df = df.merge(market[["date", "q"]], on="date", how="inner")

    S, K = df.spot.values, df.strike.values
    df["forward"] = S * np.exp((df.r - df.q) * df.tau)
    df["log_mny"] = np.log(K / df.forward)
    df["sqrt_tau"] = np.sqrt(df.tau)
    df["y"], df["lower"], df["upper"], df["scale"] = forward_units(
        df.mid.values, S, K, df.tau.values, df.r.values, df.q.values, df.is_call.values == 1)

    # quotes that already break the bounds are stale or bad data
    inside = (df.y >= df.lower) & (df.y <= df.upper)
    df = df[inside].dropna(subset=["r", "q", "y"])
    print(f"options: {n_downloaded:,} downloaded -> {len(df):,} after filters")
    return df[[c for c in OPTION_COLUMNS if c in df]].sort_values(["date", "exdate", "cp_flag", "strike"])


def main():
    C.PROC_DIR.mkdir(parents=True, exist_ok=True)
    zero_curve = raw("zerocd.parquet")
    market = build_market(zero_curve)
    options = build_options(market, zero_curve)
    options = options[options.date.isin(market.date)]
    market.to_parquet(C.PROC_DIR / "market.parquet", index=False)
    options.to_parquet(C.PROC_DIR / "options.parquet", index=False)

    print(f"market days: {len(market):,}  ({market.date.min().date()} to {market.date.max().date()})")
    print(f"option rows: {len(options):,}")
    print(market[["ret", "log_rv", "rskew", "rkurt", "vix", "rf_3m"]].describe().round(4))


if __name__ == "__main__":
    main()
