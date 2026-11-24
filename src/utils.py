"""Small helpers that more than one pipeline script needs."""
import sys
import pandas as pd
import config as C

# the columns that identify one option quote; predictions are matched back to quotes on these
QUOTE_KEYS = ["date", "optionid", "exdate", "cp_flag", "strike"]
TEXT_COLUMNS = ["cp_flag", "symbol", "expiry_indicator"]


def read_raw(path):
    """Read a WRDS parquet file with plain numpy dtypes.

    WRDS returns nullable Float64 and string columns. Numbers become float64, the text columns
    become plain strings with "" for missing. OptionMetrics' own forward price is dropped,
    because I compute the forward myself from the zero curve and the dividend yield.
    """
    df = pd.read_parquet(path)
    num = df.select_dtypes("number").columns
    df[num] = df[num].astype("float64")
    txt = [c for c in TEXT_COLUMNS if c in df]
    df[txt] = df[txt].astype("string").fillna("").astype(object)
    return df.drop(columns=["forward_price"], errors="ignore")


def plain(df):
    """Nullable pandas dtypes (Float64, string) to plain numpy dtypes, so numpy and torch accept them."""
    df = df.copy()
    for c in df.columns:
        if str(df[c].dtype) in ("Float64", "Int64", "boolean"):
            df[c] = df[c].astype("float64")
        elif str(df[c].dtype) == "string":
            df[c] = df[c].astype(object)
    return df


def load_processed():
    """The two tables written by step 2: one row per day (market) and one per option per day."""
    market = plain(pd.read_parquet(C.PROC_DIR / "market.parquet"))
    options = plain(pd.read_parquet(C.PROC_DIR / "options.parquet"))
    return market, options


def sample_design():
    """'walk' (the main design) unless the script was started with --fixed."""
    return "fixed" if "--fixed" in sys.argv else "walk"


def seed_name(variant, seed):
    """Column and file name of one trained network. The main seed keeps the plain variant name."""
    return variant if seed == C.SEED else f"{variant}_seed{seed}"
