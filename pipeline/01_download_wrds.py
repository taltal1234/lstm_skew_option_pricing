"""Step 1: download the raw data from WRDS into data/raw/ (parquet).

Usage
    python pipeline/01_download_wrds.py                  # everything
    python pipeline/01_download_wrds.py --check          # only print which tables and columns you can access
    python pipeline/01_download_wrds.py --skip_taq       # no intraday data (falls back to daily moments)

Files that already exist are skipped, so you can stop the script and run it again. The TAQ part
sends one small query per trading day and is the slow part (roughly 1 to 3 seconds per day).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so config can be imported

import argparse
import pandas as pd
import wrds
import config as C

OPTM = "optionm"
FIRST_DAY, LAST_DAY = f"{C.START_YEAR - 1}-01-01", f"{C.END_YEAR}-12-31"   # one extra year for the LSTM history
OPTION_COLUMNS = ["date", "exdate", "cp_flag", "strike_price", "best_bid", "best_offer",
                  "volume", "open_interest", "impl_volatility", "optionid", "symbol",
                  "am_settlement", "expiry_indicator", "forward_price"]
FRED_VIX = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS"
_tables = {}


def tables(db, lib):
    """Table names in a WRDS library (asked once, then remembered)."""
    if lib not in _tables:
        _tables[lib] = set(db.list_tables(library=lib))
    return _tables[lib]


def columns(db, lib, table):
    return set(db.describe_table(lib, table)["name"].str.lower())


def secprd(db, year):
    """Underlying prices: one big table on most WRDS setups, yearly tables on others."""
    return "secprd" if "secprd" in tables(db, OPTM) else f"secprd{year}"


def already_have(name):
    return (C.RAW_DIR / name).exists()


def save(df, name):
    C.RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(C.RAW_DIR / name, index=False)
    print(f"  saved {name}: {len(df):,} rows")


def check_access(db):
    """Print what the project needs and whether this account can see it."""
    print("optionm years:", sorted(t[6:] for t in tables(db, OPTM) if t.startswith("opprcd")))
    for t in ["secprd", f"secprd{C.END_YEAR}", "zerocd", "idxdvd"]:
        print(f"optionm.{t}:", t in tables(db, OPTM))
    print("cboe.cboe:", "cboe" in tables(db, "cboe") if "cboe" in db.list_libraries() else False)
    taq_libs = sorted(lib for lib in db.list_libraries() if lib.startswith("taqm_"))
    print("TAQ millisecond libraries:", taq_libs[:3], "...", taq_libs[-3:])
    last = f"opprcd{C.END_YEAR}"
    if last in tables(db, OPTM):
        print(f"columns of {last}:", sorted(columns(db, OPTM, last)))


# ------------------------------------------------------------------ OptionMetrics
def download_options(db, year):
    """One year of SPX quotes. The rough filters run on the WRDS server to keep the download small;
    the exact ones are applied in step 2."""
    name = f"options_{year}.parquet"
    if already_have(name):
        return
    table = f"opprcd{year}"
    have = columns(db, OPTM, table)
    sel = ", ".join("o." + c for c in OPTION_COLUMNS if c in have)
    lo, hi = C.MIN_MONEY - 0.05, C.MAX_MONEY + 0.05
    extra = ""
    if C.STANDARD_EXPIRIES_ONLY and "expiry_indicator" in have:
        extra += " and coalesce(o.expiry_indicator, '') = ''"   # drops weeklies and dailies
    if C.REQUIRE_VOLUME:
        extra += " and o.volume > 0"                           # only contracts that traded
    sql = f"""
        select {sel}, s.close as spot
        from {OPTM}.{table} o
        join {OPTM}.{secprd(db, year)} s on s.secid = o.secid and s.date = o.date
        where o.secid = {C.SPX_SECID}
          and o.best_bid > 0
          and o.exdate - o.date between {C.MIN_DTE} and {C.MAX_DTE}
          and o.strike_price / 1000.0 between {lo} * s.close and {hi} * s.close
          {extra}
    """
    print(f"options {year} ...")
    save(db.raw_sql(sql, date_cols=["date", "exdate"]), name)


def download_spx(db):
    years = [None] if "secprd" in tables(db, OPTM) else range(C.START_YEAR - 1, C.END_YEAR + 1)
    parts = []
    for year in years:
        t = "secprd" if year is None else f"secprd{year}"
        sql = f"""select date, open, high, low, close from {OPTM}.{t}
                  where secid = {C.SPX_SECID} and date between '{FIRST_DAY}' and '{LAST_DAY}'"""
        parts.append(db.raw_sql(sql, date_cols=["date"]))
    save(pd.concat(parts, ignore_index=True), "spx.parquet")


def download_vix(db):
    """VIX close from CBOE on WRDS, or from FRED if the account has no CBOE access."""
    try:
        sql = f"select date, vix from cboe.cboe where date between '{FIRST_DAY}' and '{LAST_DAY}'"
        df = db.raw_sql(sql, date_cols=["date"])
    except Exception as err:
        print("  cboe.cboe not available, using FRED VIXCLS instead:", err)
        df = pd.read_csv(FRED_VIX)
        df.columns = ["date", "vix"]
        df["date"] = pd.to_datetime(df["date"])
        df["vix"] = pd.to_numeric(df["vix"], errors="coerce")
    save(df.dropna(), "vix.parquet")


def download_daily(db):
    if not already_have("spx.parquet"):
        download_spx(db)

    if not already_have("zerocd.parquet"):
        sql = f"select date, days, rate from {OPTM}.zerocd where date between '{FIRST_DAY}' and '{LAST_DAY}'"
        save(db.raw_sql(sql, date_cols=["date"]), "zerocd.parquet")

    if not already_have("divyield.parquet"):
        sql = f"""select date, rate from {OPTM}.idxdvd
                  where secid = {C.SPX_SECID} and date between '{FIRST_DAY}' and '{LAST_DAY}'"""
        df = db.raw_sql(sql, date_cols=["date"])
        save(df.groupby("date", as_index=False)["rate"].mean(), "divyield.parquet")

    if not already_have("vix.parquet"):
        download_vix(db)


# ------------------------------------------------------------------ TAQ 5 minute bars
# the first trade after 09:30, then the last trade inside every 5 minute bar of the session
BAR_SQL = """
(select 0 as bar, price from {lib}.{table}
  where sym_root = '{sym}' and coalesce(sym_suffix, '') = '' and tr_corr = '00' and price > 0
    and time_m >= '09:30:00' and time_m < '16:00:00'
  order by time_m asc limit 1)
union all
(select distinct on (bar) bar, price from (
    select floor(extract(epoch from time_m) / {sec})::int as bar, time_m, price
    from {lib}.{table}
    where sym_root = '{sym}' and coalesce(sym_suffix, '') = '' and tr_corr = '00' and price > 0
      and time_m >= '09:30:00' and time_m < '16:00:00') t
  order by bar, time_m desc)
"""


def download_taq(db):
    """SPY bars, saved one file per month. The aggregation runs on the WRDS server,
    so only about 79 rows per day come back instead of hundreds of thousands of trades."""
    sec = C.BAR_MINUTES * 60
    for year in range(C.START_YEAR - 1, C.END_YEAR + 1):
        lib = f"taqm_{year}"
        day_tables = sorted(t for t in tables(db, lib) if t.startswith("ctm_2"))
        for month in range(1, 13):
            name = f"taq_{C.TAQ_SYMBOL}_{year}_{month:02d}.parquet"
            if already_have(name):
                continue
            month_tables = [t for t in day_tables if t.startswith(f"ctm_{year}{month:02d}")]
            if not month_tables:
                continue
            print(f"TAQ {year}-{month:02d}: {len(month_tables)} days")
            parts = []
            for table in month_tables:
                df = db.raw_sql(BAR_SQL.format(lib=lib, table=table, sym=C.TAQ_SYMBOL, sec=sec))
                df["date"] = pd.to_datetime(table[4:], format="%Y%m%d")   # table name is ctm_YYYYMMDD
                parts.append(df)
            save(pd.concat(parts, ignore_index=True), name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", default=None)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--skip_taq", action="store_true")
    args = ap.parse_args()

    db = wrds.Connection(wrds_username=args.username)
    if args.check:
        check_access(db)
        return
    download_daily(db)
    for year in range(C.START_YEAR, C.END_YEAR + 1):
        download_options(db, year)
    if not args.skip_taq:
        download_taq(db)
    db.close()
    print("done")


if __name__ == "__main__":
    main()
