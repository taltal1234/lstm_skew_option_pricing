"""Step 3: train the network variants and save their out of sample predictions.

Two sample designs:
  walk  (main)  Walk forward, retrained every year. For test year Y the model trains on 2010
                to Y minus 2, stops early on Y minus 1 and prices Y. Every test year is priced
                by a model that has seen all earlier years, so from 2021 on the COVID crash is in
                its training or validation data, and so is each new rate level.
  fixed         One split, no retraining: train 2010 to 2017, validate 2018, test 2019 to 2023.
                Kept as a robustness check on what retraining is worth.

The LSTM variants in config.SEED_VARIANTS are trained once for every seed in config.SEEDS.
Each trained network writes its own prediction file, so a stopped run picks up where it left off.

Usage
    python pipeline/03_train.py            # walk forward
    python pipeline/03_train.py --fixed    # fixed split
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so config and src can be imported

import time
import numpy as np
import pandas as pd
import torch
import config as C
from src.utils import QUOTE_KEYS, load_processed, sample_design, seed_name
from src.benchmarks import prev_smile
from src.model import PricingNet, make_arrays, batch_inputs, predict
torch.set_num_threads(2)


def fit(model, A, train, valid, tag):
    """Adam on the training rows with early stopping on the validation MSE.
    Returns the weights of the best epoch and the loss history."""
    opt = torch.optim.Adam(model.parameters(), lr=C.LR)
    loss_fn = torch.nn.MSELoss()
    best, best_state, wait, history = np.inf, None, 0, []
    for epoch in range(C.EPOCHS):
        t0 = time.time()
        model.train()
        perm = np.random.permutation(train)
        total = 0.0
        for i in range(0, len(perm), C.BATCH):
            rows = torch.tensor(perm[i:i + C.BATCH])
            loss = loss_fn(model(*batch_inputs(A, rows)), A["y"][rows])
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item() * len(rows)
        train_mse = total / len(perm)
        valid_mse = float(np.mean((predict(model, A, torch.tensor(valid)) - A["y"][valid].numpy()) ** 2))
        history.append({"epoch": epoch + 1, "train_mse": train_mse, "valid_mse": valid_mse})
        print(f"  [{tag}] epoch {epoch + 1:2d}  train {train_mse:.3e}  valid {valid_mse:.3e}  "
              f"({time.time() - t0:.0f}s)", flush=True)
        if valid_mse < best:
            best, wait = valid_mse, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            wait += 1
            if wait >= C.PATIENCE:
                break
    print(f"  [{tag}] best valid {best:.3e} after {len(history)} epochs", flush=True)
    return best_state, history


def test_predictions(model, A, column, constrained, test_end):
    """Prices for the test window, in dollars, one row per option quote."""
    o = A["options"]
    rows = np.where((A["split"] == "test") & (o.date <= test_end))[0]
    y_hat = predict(model, A, torch.tensor(rows))
    o = o.iloc[rows]
    out = pd.DataFrame({k: o[k].values for k in QUOTE_KEYS})
    if constrained:
        out[column] = y_hat * o.scale.values
    else:
        # the original study's approach: raw output, clamped to the bounds afterwards
        out[column + "_unclamped"] = y_hat * o.scale.values
        out[column] = np.clip(y_hat, o.lower.values, o.upper.values) * o.scale.values
    return out


def train_one(tag, variant, seed, market, options, window, out_dir, weights=None):
    """Train one network on [start, train_end], stop early on (train_end, valid_end] and price
    (valid_end, test_end]. Weights, loss history and predictions are saved under out_dir.
    weights: an already trained network on the same window, loaded instead of retraining."""
    train_end, valid_end, test_end = window
    use_lstm, use_moments, constrained, use_smile = C.VARIANTS[variant]
    torch.manual_seed(seed)
    np.random.seed(seed)
    A = make_arrays(market, options, use_moments, train_end, valid_end, use_smile)
    train = np.where(A["split"] == "train")[0]
    valid = np.where(A["split"] == "valid")[0]
    model = PricingNet(A["M"].shape[1], A["X"].shape[1], use_lstm, constrained)

    if weights is None:
        best_state, history = fit(model, A, train, valid, tag)
    else:
        best_state = torch.load(weights)
        history = pd.read_csv(Path(weights).parent / f"history_{Path(weights).stem}.csv").to_dict("records")
    model.load_state_dict(best_state)
    preds = test_predictions(model, A, seed_name(variant, seed), constrained, test_end)

    out_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), out_dir / f"{tag}.pt")
    pd.DataFrame(history).to_csv(out_dir / f"history_{tag}.csv", index=False)
    preds.to_parquet(out_dir / f"preds_{tag}.parquet", index=False)


def training_windows(design):
    """(train_end, valid_end, test_end, year label) for every network that has to be trained."""
    if design == "walk":
        return [(f"{y - 2}-12-31", f"{y - 1}-12-31", f"{y}-12-31", str(y)) for y in C.TEST_YEARS]
    return [(C.TRAIN_END, C.VALID_END, "2099-12-31", "")]


def main():
    design = sample_design()
    out_dir = C.MODEL_DIR / design
    market, options = load_processed()
    options = prev_smile(options, market, options)   # inputs for the "+ yesterday's smile" networks
    jobs = [(v, s) for v in C.VARIANTS for s in (C.SEEDS if v in C.SEED_VARIANTS else [C.SEED])]

    for train_end, valid_end, test_end, year in training_windows(design):
        for variant, seed in jobs:
            tag = seed_name(variant, seed)
            tag = f"{tag}_{year}" if year else tag
            if (out_dir / f"preds_{tag}.parquet").exists():
                print(f"{tag}: already trained, skipping")
                continue
            # the fixed split has the same training window as the first walk forward year,
            # so those networks are reused and only the (longer) test window is priced again
            same = C.MODEL_DIR / "walk" / f"{tag}_{C.TEST_YEARS[0]}.pt"
            reuse = design == "fixed" and train_end == f"{C.TEST_YEARS[0] - 2}-12-31" and same.exists()
            print(f"{design}: {'reusing' if reuse else 'training'} {tag} (train to {train_end}, validate to {valid_end})", flush=True)
            train_one(tag, variant, seed, market, options, (train_end, valid_end, test_end), out_dir,
                      weights=same if reuse else None)
    print("done:", out_dir)


if __name__ == "__main__":
    main()
