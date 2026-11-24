"""Every setting for the project: sample, filters, splits, features and network size."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"          # WRDS downloads (parquet)
PROC_DIR = ROOT / "data" / "processed"   # cleaned panel
OUT_DIR = ROOT / "results"               # tables, figures, trained models

# ---------------- sample ----------------
START_YEAR = 2010
END_YEAR = 2023             # set this to the last year your OptionMetrics subscription covers
SPX_SECID = 108105          # OptionMetrics secid of the S&P 500 index
TAQ_SYMBOL = "SPY"          # intraday proxy for SPX (the index itself never trades)

# Main design: walk forward, retrained every year. For test year Y the network trains on
# START_YEAR to Y minus 2, stops early on Y minus 1 and prices Y. So from 2021 on the COVID
# crash is part of what the model has already seen.
TEST_YEARS = [2019, 2020, 2021, 2022, 2023]
COVID_START, COVID_END = "2020-02-20", "2020-04-30"   # crash and peak volatility, reported on its own

# Robustness design: one fixed split, no retraining
TRAIN_END = "2017-12-31"    # train: START_YEAR to TRAIN_END
VALID_END = "2018-12-31"    # validation (early stopping): TRAIN_END to VALID_END
                            # test: everything after VALID_END (covers COVID 2020 and the 2022 bear market)

# ---------------- option filters ----------------
MIN_DTE, MAX_DTE = 7, 365           # days to expiry
MIN_MONEY, MAX_MONEY = 0.80, 1.20   # strike / spot
MIN_MID = 0.375                     # drop options quoted below 3/8 (Bakshi, Cao, Chen 1997)
MAX_REL_SPREAD = 0.50               # (ask minus bid) / mid
REQUIRE_VOLUME = True               # keep only contracts that traded that day
CP_FLAGS = ["C", "P"]               # calls and puts
STANDARD_EXPIRIES_ONLY = True       # monthly AM settled SPX only (drops the SPXW weeklies)

# ---------------- realized moments ----------------
BAR_MINUTES = 5                     # 78 bars per day, same as the original paper
RV_WINDOW = 22                      # days in the trailing realized vol benchmark

# ---------------- model ----------------
SEQ_LEN = 22                        # the LSTM looks back one trading month
MARKET_BASE = ["ret", "ret_overnight", "log_rv", "vix"]
MARKET_MOMENTS = ["rskew", "rkurt"]  # the realized higher moments under study
CONTRACT_FEATURES = ["log_mny", "tau", "sqrt_tau", "is_call"]   # rates enter only via F and discounting
SMILE_FEATURES = ["iv_prev", "y_prev"]  # yesterday's fitted smile at this contract (known before today)

HIDDEN = 32                         # LSTM units (as in the paper)
HEAD = 64                           # dense units (as in the paper)
EPOCHS = 50
PATIENCE = 6
BATCH = 4096
LR = 1e-3
SEED = 42                            # main seed (every variant)
SEEDS = [42, 1, 2]                   # the LSTMs below are also trained with these seeds
SEED_VARIANTS = ["lstm_no_moments", "lstm_full", "lstm_smile_no_moments", "lstm_smile_full"]

# Network variants trained by 03_train.py:
#   name -> (use_lstm, use_moments, constrained, use_smile)
VARIANTS = {
    "mlp_full":              (False, True,  True,  False),  # no sequence memory: is the LSTM needed?
    "lstm_no_moments":       (True,  False, True,  False),  # no realized skew/kurt: does skewness help?
    "lstm_full":             (True,  True,  True,  False),  # main model, no arbitrage bounds built in
    "lstm_full_raw":         (True,  True,  False, False),  # linear output + clamp afterwards, as in the original study
    "lstm_smile_no_moments": (True,  False, True,  True),   # also sees yesterday's smile
    "lstm_smile_full":       (True,  True,  True,  True),   # yesterday's smile + realized skew/kurt
}

# ---------------- smoke test on synthetic data (never used for results) ----------------
if os.environ.get("SMOKE_TEST"):
    RAW_DIR = ROOT / "data_mock" / "raw"
    PROC_DIR = ROOT / "data_mock" / "processed"
    OUT_DIR = ROOT / "results_mock"
    START_YEAR, END_YEAR = 2014, 2021
    TEST_YEARS = [2020, 2021]
    EPOCHS = int(os.environ.get("EPOCHS", 3))

# ---------------- result sub folders ----------------
TABLE_DIR = OUT_DIR / "tables"      # tables.md and every csv
FIG_DIR = OUT_DIR / "figures"       # png figures
MODEL_DIR = OUT_DIR / "models"      # trained weights, training histories, predictions
