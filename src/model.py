"""The pricing network and the code that feeds it.

The network has two inputs:
  1. the last SEQ_LEN days of market state (returns, realized vol, realized skewness and
     kurtosis, VIX), read by an LSTM
  2. the terms of the contract (log moneyness K/F, maturity, call or put), plus yesterday's
     smile for the "+ smile" variants

The LSTM's summary of the market and the contract terms go through a small dense head.
The output is the option price in forward units: price / (F exp(-r tau)).

constrained=True  : price = lower + (upper - lower) * sigmoid(out), so every prediction sits
                    inside the no arbitrage bounds by construction.
constrained=False : price = out (linear), the original paper's setup; it gets clamped afterwards.
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import config as C


class PricingNet(nn.Module):
    def __init__(self, n_market, n_contract, use_lstm=True, constrained=True):
        super().__init__()
        self.use_lstm = use_lstm
        self.constrained = constrained
        if use_lstm:
            self.lstm = nn.LSTM(n_market, C.HIDDEN, batch_first=True)
            n_state = C.HIDDEN
        else:
            n_state = n_market          # the MLP only sees today's market state, no memory
        self.head = nn.Sequential(
            nn.Linear(n_state + n_contract, C.HEAD), nn.ReLU(),
            nn.Linear(C.HEAD, C.HEAD), nn.ReLU(),
            nn.Linear(C.HEAD, 1),
        )
        if constrained:
            # start near the lower bound (little time value) instead of halfway to the upper bound
            nn.init.constant_(self.head[-1].bias, -3.0)

    def forward(self, seq, day_of_row, x, lower, upper):
        """seq: (unique days, SEQ_LEN, n_market). day_of_row says which day each option row belongs to."""
        if self.use_lstm:
            _, (h, _) = self.lstm(seq)
            state = h[-1]
        else:
            state = seq[:, -1]
        out = self.head(torch.cat([state[day_of_row], x], dim=1)).squeeze(1)
        if self.constrained:
            return lower + (upper - lower) * torch.sigmoid(out)
        return out


def make_arrays(market, options, use_moments, train_end, valid_end, use_smile=False):
    """Everything the network needs, as tensors. Rows up to train_end are training, up to
    valid_end validation, later rows test. Features are scaled with statistics from the
    training window only, so nothing from the future leaks in."""
    mcols = C.MARKET_BASE + (C.MARKET_MOMENTS if use_moments else [])
    train_days = market.date <= train_end

    # market features: clip the extreme 1% (crash days) and standardize
    M = market[mcols].copy()
    lo, hi = M[train_days].quantile(0.005), M[train_days].quantile(0.995)
    M = M.clip(lo, hi, axis=1)
    M = (M - M[train_days].mean()) / M[train_days].std()

    # an option row needs a full month of market history and (for the smile variants) yesterday's smile
    day_pos = pd.Series(np.arange(len(market)), index=market.date)
    d = day_pos.loc[options.date].values
    keep = d >= C.SEQ_LEN - 1
    cols = C.CONTRACT_FEATURES + (C.SMILE_FEATURES if use_smile else [])
    keep &= options[cols].notna().all(axis=1).values
    opt = options[keep].reset_index(drop=True)
    d = d[keep]

    X = opt[cols]
    train_rows = opt.date <= train_end
    X = (X - X[train_rows].mean()) / X[train_rows].std().replace(0, 1)

    split = np.where(opt.date <= train_end, "train",
                     np.where(opt.date <= valid_end, "valid", "test"))
    return {
        "M": torch.tensor(M.values, dtype=torch.float32),
        "d": torch.tensor(d, dtype=torch.long),
        "X": torch.tensor(X.values, dtype=torch.float32),
        "lower": torch.tensor(opt.lower.values, dtype=torch.float32),
        "upper": torch.tensor(opt.upper.values, dtype=torch.float32),
        "y": torch.tensor(opt.y.values, dtype=torch.float32),
        "split": split,
        "options": opt,
    }


def batch_inputs(A, rows):
    """Gather one batch. The LSTM runs once per unique day in the batch, not once per option,
    which is what makes training on millions of quotes affordable on a laptop."""
    d = A["d"][rows]
    days, day_of_row = torch.unique(d, return_inverse=True)
    window = days[:, None] + torch.arange(-C.SEQ_LEN + 1, 1)
    seq = A["M"][window]
    return seq, day_of_row, A["X"][rows], A["lower"][rows], A["upper"][rows]


def predict(model, A, rows, batch=50000):
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(rows), batch):
            r = rows[i:i + batch]
            out.append(model(*batch_inputs(A, r)))
    return torch.cat(out).numpy()
