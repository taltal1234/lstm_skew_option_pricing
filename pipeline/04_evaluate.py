"""Step 4: benchmarks, error tables, no arbitrage checks, Diebold Mariano tests, figures.

Every number is computed on the out of sample test period (2019 to 2023) and on the common set
of options that every model can price, so the models are always compared on the same quotes.
The COVID crash window is also reported on its own.

Usage
    python pipeline/04_evaluate.py            # walk forward design (main)
    python pipeline/04_evaluate.py --fixed    # fixed split design
Outputs: results/tables/<design>/ (tables.md and csv files) and results/figures/<design>/ (png)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so config and src can be imported

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config as C
from src.utils import QUOTE_KEYS, plain, load_processed, sample_design, seed_name
from src.benchmarks import add_benchmarks
from src.finance import implied_vol, contract_terms

BENCHMARKS = ["bs_20", "bs_rv", "bs_vix", "ahbs"]
LABELS = {
    "bs_20": "BS 20% vol", "bs_rv": "BS realized vol", "bs_vix": "BS VIX",
    "ahbs": "Ad hoc BS (DFW)", "mlp_full": "MLP (no memory)",
    "lstm_no_moments": "LSTM w/o skew, kurt", "lstm_full": "LSTM (bounded)",
    "lstm_full_raw": "LSTM raw + clamp",
    "lstm_no_moments_ens": "LSTM w/o skew, kurt (3 seed avg)", "lstm_full_ens": "LSTM bounded (3 seed avg)",
    "lstm_smile_no_moments": "LSTM + smile, w/o skew", "lstm_smile_full": "LSTM + smile, with skew",
    "lstm_smile_no_moments_ens": "LSTM + smile, w/o skew (3 seed avg)",
    "lstm_smile_full_ens": "LSTM + smile, with skew (3 seed avg)",
}
COLORS = {  # one fixed color per model, so a model looks the same in every figure
    "lstm_full": "#2a78d6", "lstm_full_raw": "#eb6834", "ahbs": "#1baf7a",
    "bs_20": "#eda100", "bs_vix": "#e87ba4", "bs_rv": "#008300",
    "mlp_full": "#6250d6", "lstm_no_moments": "#e34948",
    "lstm_full_ens": "#2a78d6", "lstm_no_moments_ens": "#e34948",
    "lstm_smile_no_moments": "#1a7f99", "lstm_smile_full": "#7a5c00",
}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

# pairs of models compared with Diebold Mariano tests, on top of "main model against everything"
DM_PAIRS = [("lstm_full_ens", "lstm_no_moments_ens"), ("lstm_no_moments_ens", "ahbs"), ("lstm_full_ens", "ahbs"),
            ("mlp_full", "ahbs"), ("lstm_smile_no_moments_ens", "ahbs"), ("lstm_smile_full_ens", "ahbs"),
            ("lstm_smile_full_ens", "lstm_smile_no_moments_ens"),
            ("lstm_smile_no_moments_ens", "lstm_no_moments_ens")]
# (column, title) of the RMSE breakdowns
GROUPS = [("period", "RMSE by period ($)"), ("year", "RMSE by year ($)"),
          ("money_bucket", "RMSE by moneyness K/S ($)"), ("dte_bucket", "RMSE by days to expiry ($)"),
          ("vix_regime", "RMSE by volatility regime ($)"), ("cp_flag", "RMSE by option type ($)")]


# ------------------------------------------------------------------ error measures
def rmse(err):
    return np.sqrt(np.mean(err ** 2))


def price_error(df, m):
    return df[m] - df.mid


def iv_error(df, m):
    """Model implied vol minus market implied vol (NaN where either has no implied vol)."""
    return (df[f"iv_{m}"] - df.iv_mid).dropna()


def metrics(df, models):
    rows = []
    for m in models:
        e = price_error(df, m)
        rows.append({"model": LABELS[m], "RMSE": rmse(e), "MAE": np.mean(np.abs(e)),
                     "MAPE %": 100 * np.mean(np.abs(e) / df.mid), "Bias": np.mean(e),
                     "IV RMSE (vol pts)": 100 * rmse(iv_error(df, m))})
    return pd.DataFrame(rows)


def rmse_by_group(df, models, col, error=price_error, scale=1.0, show_n=True):
    """One row per value of col, one RMSE column per model."""
    rows = []
    for g, sub in df.groupby(col, observed=True):
        row = {col: str(g)}
        if show_n:
            row["n"] = f"{len(sub):,}"
        for m in models:
            row[LABELS[m]] = scale * rmse(error(sub, m))
        rows.append(row)
    return pd.DataFrame(rows)


def diebold_mariano(df, a, b, lags=5):
    """DM test on daily mean squared errors with a Newey West variance.
    A negative statistic means model a has the lower error."""
    d = df.assign(la=(df[a] - df.mid) ** 2, lb=(df[b] - df.mid) ** 2).groupby("date")[["la", "lb"]].mean()
    d = (d.la - d.lb).values
    T, u = len(d), d - d.mean()
    var = np.sum(u * u) / T
    for k in range(1, lags + 1):
        var += 2 * (1 - k / (lags + 1)) * np.sum(u[k:] * u[:-k]) / T
    return d.mean() / np.sqrt(var / T)


def shape_violations(df, col):
    """Cross strike no arbitrage on each (date, expiry, type) slice: calls must fall in K and puts
    rise in K (monotone), and both must be convex in K. Returns the % of violations of each."""
    s = df.sort_values(["date", "exdate", "cp_flag", "strike"])
    g = s.groupby(["date", "exdate", "cp_flag"])
    dp, dk = g[col].diff(), g["strike"].diff()
    slope = dp / dk
    call = s.cp_flag == "C"
    mono = np.where(call, dp > 0.01, dp < -0.01)
    conv = g.cumcount() >= 2
    conv_bad = (slope - slope.groupby([s.date, s.exdate, s.cp_flag]).shift(1)) < -1e-3
    has_pair = dp.notna()
    return 100 * mono[has_pair.values].mean(), 100 * conv_bad[conv].mean()


def md_table(df, digits=3):
    df = df.copy()
    for c in df.select_dtypes("number"):
        df[c] = df[c].map(lambda v: f"{v:,.{digits}f}" if abs(v) < 1e6 else f"{v:,.0f}")
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    body = ["| " + " | ".join(map(str, r)) + " |" for r in df.values]
    return "\n".join([head, sep] + body)


def section(title, table, note=""):
    """One block of tables.md: a heading, an optional note, the table."""
    return f"## {title}\n\n" + (f"{note}\n\n" if note else "") + table + "\n"


# ------------------------------------------------------------------ the test set
def load_predictions(design):
    """Join the prediction files written by 03_train.py (one file per network and test year)."""
    groups = {}
    for f in sorted((C.MODEL_DIR / design).glob("preds_*.parquet")):
        df = plain(pd.read_parquet(f))
        cols = tuple(c for c in df.columns if c not in QUOTE_KEYS)
        groups.setdefault(cols, []).append(df)     # the yearly files of one network are stacked first
    preds = None
    for parts in groups.values():
        df = pd.concat(parts, ignore_index=True)
        preds = df if preds is None else preds.merge(df, on=QUOTE_KEYS, how="outer")
    return preds


def add_seed_averages(test):
    """Average price of the networks trained with different seeds: a small ensemble, and the
    most reliable estimate of what each LSTM variant can do."""
    ens = []
    for v in C.SEED_VARIANTS:
        cols = [v] + [seed_name(v, s) for s in C.SEEDS if s != C.SEED]
        if all(c in test for c in cols):
            test[f"{v}_ens"] = test[cols].mean(axis=1)
            ens.append(f"{v}_ens")
    return ens


def add_buckets(test):
    test["money_bucket"] = pd.cut(test.strike / test.spot, [0, 0.94, 0.97, 1.00, 1.03, 1.06, 9],
                                  labels=["<0.94", "0.94–0.97", "0.97–1.00", "1.00–1.03", "1.03–1.06", ">1.06"])
    test["dte_bucket"] = pd.cut(test.dte, [0, 30, 90, 400], labels=["<30d", "30–90d", ">90d"])
    test["year"] = test.date.dt.year
    test["vix_regime"] = pd.cut(test.vix, [0, 0.15, 0.25, 9], labels=["VIX<15", "VIX 15–25", "VIX>25"])
    covid = (test.date >= C.COVID_START) & (test.date <= C.COVID_END)
    test["period"] = np.where(covid, f"COVID crash {C.COVID_START} to {C.COVID_END}", "Rest of test period")
    return covid


def build_test_set(design, market, options):
    """Test quotes with the price of every model, implied vols and the grouping columns."""
    test = options[options.date > C.VALID_END].merge(load_predictions(design), on=QUOTE_KEYS, how="inner")
    test = add_benchmarks(test, market, options)
    ens = add_seed_averages(test)
    models = BENCHMARKS + [m for m in C.VARIANTS if m in test] + ens
    n_all = len(test)
    test = test.dropna(subset=models).copy()
    print(f"{design}: test rows {n_all:,}, priced by every model {len(test):,}", flush=True)

    S, K, tau, r, q = contract_terms(test)
    call = test.cp_flag.values == "C"
    for m in ["mid"] + models:
        test[f"iv_{m}"] = implied_vol(test[m].values, S, K, tau, r, q, call)
    covid = add_buckets(test)
    return test, models, ens, covid, call


# ------------------------------------------------------------------ tables
def seed_table(test, covid):
    rows = []

    def row(col, label, seed):
        e = test[col] - test.mid
        return {"model": label, "seed": seed, "RMSE": rmse(e), "RMSE outside COVID window": rmse(e[~covid])}

    for v in C.SEED_VARIANTS:
        for s in C.SEEDS:
            if seed_name(v, s) in test:
                rows.append(row(seed_name(v, s), LABELS[v], str(s)))
        if f"{v}_ens" in test:
            rows.append(row(f"{v}_ens", LABELS[v], "average of seeds"))
    return pd.DataFrame(rows)


def no_arbitrage_table(test, models):
    rows = []
    raw = "lstm_full_raw_unclamped"
    if raw in test:
        lo, hi = test.lower * test.scale, test.upper * test.scale
        rows.append({"series": "LSTM raw before clamp",
                     "below lower bound %": 100 * (test[raw] < lo - 1e-8).mean(),
                     "above upper bound %": 100 * (test[raw] > hi + 1e-8).mean()})
    for m in ["mid"] + models:
        mono, conv = shape_violations(test, m)
        rows.append({"series": "Market mid" if m == "mid" else LABELS[m],
                     "monotonicity in K violated %": mono, "convexity in K violated %": conv})
    return pd.DataFrame(rows)


def dm_table(test, models, ens, covid):
    pairs = [("lstm_full", m) for m in models if m not in ("lstm_full",) + tuple(ens)]
    pairs += [(a, b) for a, b in DM_PAIRS if a in test and b in test]
    return pd.DataFrame([{"model": LABELS[a], "vs": LABELS[b],
                          "DM all": diebold_mariano(test, a, b),
                          "DM outside COVID window": diebold_mariano(test[~covid], a, b)} for a, b in pairs])


def write_tables(test, models, ens, covid, call, design, table_dir):
    out = [f"# Results, {design} design (test period {test.date.min().date()} to {test.date.max().date()})\n",
           f"{len(test):,} option quotes on {test.date.nunique():,} days, calls {100 * call.mean():.0f}%. "
           f"COVID crash window: {covid.sum():,} quotes on {test[covid].date.nunique()} days.\n"]

    overall = metrics(test, models)
    rest = metrics(test[~covid], models)
    out.append(section("Pricing error, all options", md_table(overall),
                       "Dollar errors; IV RMSE in volatility points (model implied vol minus market implied vol)."))
    out.append(section("Pricing error outside the COVID crash window", md_table(rest)))
    for col, title in GROUPS:
        t = rmse_by_group(test, models, col)
        t.to_csv(table_dir / f"rmse_by_{col}.csv", index=False)
        out.append(section(title, md_table(t)))

    iv_year = rmse_by_group(test, models, "year", error=iv_error, scale=100, show_n=False)
    iv_year.to_csv(table_dir / "iv_rmse_by_year.csv", index=False)
    out.append(section("IV RMSE by year (vol points)", md_table(iv_year, 2)))

    seeds = seed_table(test, covid)
    if len(seeds):
        seeds.to_csv(table_dir / "seed_robustness.csv", index=False)
        out.append(section("Random seeds ($)", md_table(seeds, 2),
                           "The two LSTMs retrained from different random starting points."))

    arb = no_arbitrage_table(test, models)
    out.append(section("No arbitrage checks", md_table(arb, 2).replace("nan", ""),
                       "Bound violations are per quote. Monotonicity and convexity are checked on neighbouring "
                       "strikes of the same expiry (convexity tolerance 0.001 in slope)."))

    dm = dm_table(test, models, ens, covid)
    dm.to_csv(table_dir / "diebold_mariano.csv", index=False)
    out.append(section("Diebold Mariano tests", md_table(dm, 2),
                       "Daily mean squared $ error, Newey West with 5 lags. "
                       "Below -1.96: first model significantly better; above 1.96: significantly worse."))

    overall.to_csv(table_dir / "overall.csv", index=False)
    rest.to_csv(table_dir / "overall_outside_covid.csv", index=False)
    arb.to_csv(table_dir / "no_arbitrage.csv", index=False)
    (table_dir / "tables.md").write_text("\n".join(out))
    print("\n".join(out))


# ------------------------------------------------------------------ figures
def style(ax, title, ylabel):
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_ylabel(ylabel, color=MUTED)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=9)


def save_figure(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def atm_call_series(test):
    """Each day, the call closest to the money with 20 to 45 days to expiry: a real contract
    series to redo the original paper's two figures on."""
    c = test[(test.cp_flag == "C") & test.dte.between(20, 45)].copy()
    c["dist"] = c.log_mny.abs()
    return c.sort_values("dist").groupby("date").head(1).sort_values("date")


def plot_atm_call(test, design, fig_dir):
    atm = atm_call_series(test)
    show = [m for m in ["lstm_full", "lstm_full_raw", "ahbs", "bs_20"] if m in atm]

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(atm.date, atm.mid, color=INK, lw=1.6, label="Market mid")
    for m in show:
        ax.plot(atm.date, atm[m], color=COLORS[m], lw=1.2, label=LABELS[m])
    style(ax, f"At the money 1 month SPX call: market vs models ({design} design)", "Price ($)")
    ax.legend(frameon=False, ncol=5, loc="upper left", fontsize=8)
    save_figure(fig, fig_dir / "atm_call_prices.png")

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.axhline(0, color=MUTED, lw=0.8)
    for m in show:
        ax.plot(atm.date, atm[m] - atm.mid, color=COLORS[m], lw=1.0, label=LABELS[m])
    style(ax, "Pricing error (model minus market) for the same series", "Error ($)")
    ax.legend(frameon=False, ncol=4, loc="upper left", fontsize=8)
    save_figure(fig, fig_dir / "atm_call_errors.png")


def plot_rmse_by_moneyness(test, models, fig_dir):
    t = rmse_by_group(test, models, "money_bucket")
    fig, ax = plt.subplots(figsize=(10, 4.8))
    w = 0.8 / len(models)
    x = np.arange(len(t))
    for i, m in enumerate(models):
        ax.bar(x + i * w - 0.4 + w / 2, t[LABELS[m]], width=w * 0.92, color=COLORS[m], label=LABELS[m])
    ax.set_xticks(x, t.money_bucket.astype(str))
    ax.set_xlabel("Moneyness K/S", color=MUTED)
    style(ax, "RMSE by moneyness, test period", "RMSE ($)")
    ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    save_figure(fig, fig_dir / "rmse_by_moneyness.png")


def plot_rolling_rmse(test, market, fig_dir):
    """Rolling 21 day RMSE through time, with VIX in its own panel underneath (no dual axis)."""
    show = [m for m in ["lstm_full", "lstm_no_moments", "ahbs", "bs_vix"] if m in test]
    daily = test.assign(**{m: (test[m] - test.mid) ** 2 for m in show}).groupby("date")[show].mean()
    roll = np.sqrt(daily.rolling(21, min_periods=10).mean())
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, height_ratios=[2.2, 1])
    for m in show:
        a1.plot(roll.index, roll[m], color=COLORS[m], lw=1.3, label=LABELS[m])
    style(a1, "Rolling 21 day RMSE", "RMSE ($)")
    a1.legend(frameon=False, ncol=4, fontsize=8, loc="upper left")
    v = market[market.date.isin(daily.index)]
    a2.plot(v.date, 100 * v.vix, color=MUTED, lw=1.0)
    style(a2, "VIX", "Index level")
    save_figure(fig, fig_dir / "rolling_rmse_and_vix.png")


def plot_validation_loss(design, fig_dir):
    """Training curves. Fixed design: one network per variant. Walk forward: the last year's networks."""
    fig, ax = plt.subplots(figsize=(7, 3.6))
    suffix = "" if design == "fixed" else f"_{C.TEST_YEARS[-1]}"
    for m in C.VARIANTS:
        p = C.MODEL_DIR / design / f"history_{m}{suffix}.csv"
        if p.exists():
            h = pd.read_csv(p)
            ax.plot(h.epoch, h.valid_mse, color=COLORS[m], lw=1.4, label=LABELS[m])
    ax.set_yscale("log")
    ax.set_xlabel("Epoch", color=MUTED)
    style(ax, "Validation loss (MSE of price in forward units)", "MSE")
    ax.legend(frameon=False, fontsize=8)
    save_figure(fig, fig_dir / "validation_loss.png")


def make_figures(test, market, models, fig_dir, design):
    fig_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID})
    plot_atm_call(test, design, fig_dir)
    plot_rmse_by_moneyness(test, models, fig_dir)
    plot_rolling_rmse(test, market, fig_dir)
    plot_validation_loss(design, fig_dir)
    print("figures saved to", fig_dir)


def main():
    design = sample_design()
    table_dir = C.TABLE_DIR / design
    table_dir.mkdir(parents=True, exist_ok=True)
    market, options = load_processed()
    test, models, ens, covid, call = build_test_set(design, market, options)
    write_tables(test, models, ens, covid, call, design, table_dir)
    single_models = [m for m in models if not m.endswith("_ens")]   # the seed averages would crowd the figures
    make_figures(test, market, single_models, C.FIG_DIR / design, design)


if __name__ == "__main__":
    main()
