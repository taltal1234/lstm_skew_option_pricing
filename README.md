# Realized Skewness and LSTM Networks for S&P 500 Option Pricing

By Ahmed Tallal Bajwa. This repository rebuilds an earlier research project, *"Incorporating Realized Skewness into Deep Learning Models for Option Pricing: A Study Using LSTMs"*, on **real market data from WRDS**.

The question stays the same: **does realized skewness of the underlying, read through an LSTM, help price options, and how does such a model compare with Black Scholes once no arbitrage bounds are enforced?** Everything else is redone so the answer can actually be trusted.

## What changed from the original study

| | Original DRP | This version |
|---|---|---|
| Option prices | Simulated with Black Scholes (so Black Scholes was being tested against itself) | Real SPX end of day quotes from OptionMetrics, 2010 to 2023 |
| Cross section | One strike (`Call_100_Price`) | Full panel: calls and puts, 7 to 365 days, K/S from 0.8 to 1.2 |
| Skewness | Rolling skew of simulated returns | Realized skewness and kurtosis from SPY 5 minute TAQ returns (Amaya, Christoffersen, Jacobs, Vasquez 2015) |
| LSTM input | One row treated as one time step | A real 22 trading day sequence of market state |
| Scaling | Scaler fit on the whole sample (look ahead) | Fit on the training period only |
| Split | 80/20 | Walk forward: one model per test year 2019 to 2023, trained on every earlier year, so from 2021 on the COVID crash is in the model's history; the COVID crash window is also reported on its own. A single fixed split (train 2010 to 2017) is kept as a robustness check |
| No arbitrage | Post prediction clamp at the call lower bound | Bounds built into the output layer for calls and puts, plus the paper's clamp as a comparison, plus cross strike monotonicity and convexity checks |
| Rates | Fed to the network as an input | Enter only through the forward price and discounting (prices in forward units), so the model does not break when rates leave the training range |
| Benchmarks | Black Scholes with 20% vol | BS 20%, BS with realized vol, BS with VIX, and the ad hoc Black Scholes surface of Dumas, Fleming, Whaley (1998) |
| Evidence | Plots only | RMSE, MAE, MAPE, bias by moneyness, maturity, type and volatility regime; Diebold Mariano tests; ablations without memory and without higher moments |
| Inflation | Included | Dropped: monthly, published with a lag, so it carries no daily information and risks look ahead |

## Results (test period 2019 to 2023, 1.31 million quotes)

Walk forward design: every network is retrained each year on all earlier data. "3 seed avg" = average price of three networks trained with different random seeds. The study has two stages: networks that see market data only, then networks that also see yesterday's implied volatility smile (the information the ad hoc benchmark uses).

| Model | RMSE ($) | Outside COVID crash ($) | COVID crash window ($) | IV RMSE (vol points) |
|---|---|---|---|---|
| **Stage 2:** LSTM + yesterday's smile, without realized skew, 3 seed avg | **8.48** | **5.86** | 31.20 | **2.37** |
| **Stage 2:** LSTM + yesterday's smile, with realized skew, 3 seed avg | 8.63 | 5.95 | 31.86 | 2.38 |
| Ad hoc Black Scholes (Dumas, Fleming, Whaley) | 11.17 | 10.01 | **26.75** | 2.50 |
| Stage 1: LSTM without realized skew, 3 seed avg | 11.95 | 9.92 | 34.82 | 2.74 |
| Stage 1: LSTM with realized skew (bounded), 3 seed avg | 12.76 | 10.53 | 37.57 | 2.77 |
| Stage 1: MLP (no memory) | 12.92 | 10.90 | 36.37 | 2.85 |
| Stage 1: LSTM raw output + clamp | 13.00 | 10.80 | 37.75 | 5.26 |
| Black Scholes with VIX | 35.14 | 30.47 | 92.81 | 6.71 |
| Black Scholes 20% vol (original benchmark) | 36.57 | 34.12 | 74.18 | 8.18 |
| Black Scholes with realized vol | 51.09 | 49.86 | 74.81 | 10.51 |

* With market data only, the networks cut errors by about two thirds against every single volatility Black Scholes model, and tie the ad hoc benchmark outside the COVID crash.
* With yesterday's smile added, the LSTM beats the ad hoc benchmark by 24% overall and 41% outside the crash (Diebold Mariano -13.8), in every year except 2020. The crash is the one place the benchmark still wins.
* Realized skewness does not reliably help in either stage. Its only positive sign, a small implied volatility gain in 2021 and 2022, disappears in the fixed split and reverses in dollars.
* Bounds built into the output layer keep prices consistent across strikes (0.06% monotonicity violations vs 3.13% for the clamp).
* A first version that fed interest rates to the network broke down in 2022 and 2023; pricing in forward units fixed it.

Full tables: `results/tables/walk/tables.md` (main) and `results/tables/fixed/tables.md` (single split, no retraining). The paper: `paper/LSTM_realized_skewness_SPX_options.pdf`.

## Data (WRDS)

You need a WRDS account with **OptionMetrics IvyDB US**, **TAQ Millisecond** and **CBOE Indexes** (if CBOE is missing the script uses VIX from FRED instead). `python pipeline/01_download_wrds.py --check` tells you what your account can see.

| Source | WRDS table | Fields | Used for |
|---|---|---|---|
| OptionMetrics | `optionm.opprcdYYYY` | date, exdate, cp_flag, strike_price, best_bid, best_offer, volume, open_interest, impl_volatility, expiry_indicator, am_settlement | Option quotes (SPX, secid 108105). Target is the bid ask midpoint |
| OptionMetrics | `optionm.secprd` | close | SPX level |
| OptionMetrics | `optionm.zerocd` | days, rate | Zero coupon curve, interpolated to each option's maturity |
| OptionMetrics | `optionm.idxdvd` | rate | SPX dividend yield |
| TAQ Millisecond | `taqm_YYYY.ctm_YYYYMMDD` | time_m, price, sym_root, tr_corr | SPY last trade in every 5 minute bar (aggregated on the WRDS server) |
| CBOE Indexes | `cboe.cboe` | vix | VIX close |

SPX itself does not trade, so SPY (the ETF that tracks it) supplies the intraday returns. 78 five minute returns per day, as in the original paper.

**WRDS data is licensed to you. Do not commit it.** The `.gitignore` already excludes `data/`.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python pipeline/01_download_wrds.py --username YOUR_WRDS_USERNAME --check   # what can I access?
python pipeline/01_download_wrds.py --username YOUR_WRDS_USERNAME           # download (resumable)
python pipeline/02_build_dataset.py      # clean, realized moments, features
python pipeline/03_train.py              # walk forward: train every variant for each test year
python pipeline/04_evaluate.py           # benchmarks, tables, tests, figures -> results/*/walk/
python pipeline/03_train.py --fixed      # robustness: one fixed split, no retraining
python pipeline/04_evaluate.py --fixed   # -> results/*/fixed/
# or steps 2 to 4 for both designs in one go:
python run_all.py
```

Notes

* The first login asks for your WRDS password and a Duo approval, and offers to save a `.pgpass` file so later runs log in silently.
* Set `END_YEAR` in `config.py` to the last year your OptionMetrics subscription covers.
* The option download takes minutes. The TAQ part sends one query per trading day and can take a few hours; it saves one file per month, so you can stop and restart it. `--skip_taq` skips it and falls back to rolling daily moments (weaker, but lets you start).
* The walk forward design trains 70 networks (six variants in five test years; the four LSTMs compared on realized skewness with three seeds each) and takes about 4 to 5 hours on a laptop CPU. A GPU is not needed. Every finished network is saved, so a stopped run resumes where it left off. The fixed split reuses the first year's networks and only re-predicts.
* If Python crashes with a segmentation fault while reading parquet files, your Anaconda base environment has mismatched numpy and pandas builds. Use a clean environment instead: `conda create -n lstm python=3.12 -y`, `conda activate lstm`, `pip install -r requirements.txt`, then run the scripts from that Terminal.
* Retraining will not give bit for bit the same networks: PyTorch spreads the LSTM's arithmetic over several CPU threads, and the order of those additions changes from run to run. In a test the predicted prices moved by less than half a cent and the RMSEs only in the sixth significant digit, so the tables do not change in any way that matters. For exactly repeatable runs, call `torch.use_deterministic_algorithms(True)` and use one thread (slower).

## Method

### Realized moments (daily, from 5 minute returns $r_{t,i}$, $i = 1..N$)

$$RV_t=\sum_i r_{t,i}^2,\qquad RSk_t=\frac{\sqrt{N}\sum_i r_{t,i}^3}{RV_t^{3/2}},\qquad RKu_t=\frac{N\sum_i r_{t,i}^4}{RV_t^{2}}$$

Isolated bad prints are removed with a rolling median filter before returns are taken.

### Model

For option $j$ on day $t$:

* **Market state sequence** (last 22 trading days): SPX return, overnight return, log RV, realized skewness, realized kurtosis, VIX. Read by an LSTM with 32 units (as in the paper).
* **Contract terms**: log moneyness $\ln(K/F)$, $\tau$, $\sqrt{\tau}$, call or put.
* **Yesterday's smile** (stage 2 networks only): the implied volatility that yesterday's fitted ad hoc surface assigns to this contract, and the matching price in forward units. Known before today's prices, so no look ahead.
* **Head**: the LSTM's last hidden state concatenated with the contract terms, two dense layers of 64 ReLU units, one output.
* **Target**: price in forward units, $y = V/(F e^{-r\tau})$ with $F = S e^{(r-q)\tau}$. Rates and dividends enter only here, never as network inputs.
* **No arbitrage output layer**: $\hat y = L + (U-L)\,\sigma(z)$ with
  calls: $L=\max(0, 1-K/F)$, $U=1$; puts: $L=\max(0, K/F-1)$, $U=K/F$.
  Every prediction is inside the bounds by construction.
* Loss MSE, Adam, learning rate 0.001, batch 4096, early stopping on the year before each test year.

### Variants (the ablations that answer the research question)

| Name | Sequence memory | Realized skew and kurtosis | Output |
|---|---|---|---|
| `lstm_full` | yes | yes | bounded by construction (main model) |
| `lstm_no_moments` | yes | no | bounded |
| `mlp_full` | no (today only) | yes | bounded |
| `lstm_full_raw` | yes | yes | linear, then clamped (the original paper's approach) |
| `lstm_smile_no_moments` | yes, plus yesterday's smile | no | bounded (stage 2) |
| `lstm_smile_full` | yes, plus yesterday's smile | yes | bounded (stage 2): does realized skew add anything beyond the market's own skew? |

`lstm_full` vs `lstm_no_moments` tests whether realized skewness adds pricing information; `lstm_smile_full` vs `lstm_smile_no_moments` tests it again once the network knows the market's own skew. `lstm_full` vs `mlp_full` tests whether the LSTM's memory matters.

### Benchmarks

* `bs_20`: Black Scholes with constant 20% volatility (the original benchmark)
* `bs_rv`: Black Scholes with trailing 22 day realized volatility
* `bs_vix`: Black Scholes with VIX
* `ahbs`: ad hoc Black Scholes. Each day, regress implied vols on $m, m^2, \tau, m\tau, \tau^2$ (with $m=K/S$), separately for calls and puts, and use yesterday's fitted surface to price today. This is the practitioner benchmark and the hardest one to beat, because it uses the option market's own information.

### Evaluation (test period only)

* RMSE, MAE, MAPE and bias in dollars, overall and by moneyness, maturity, option type and VIX regime
* No arbitrage: share of raw predictions outside the bounds; share of neighbouring strike pairs violating monotonicity or convexity
* Diebold Mariano tests on daily mean squared errors (Newey West, 5 lags), main model vs every other model
* Figures: market vs model prices for a rolling at the money one month call (the paper's two figures, on real data), RMSE by moneyness, rolling RMSE through time with VIX, validation loss

## Repository layout

```
lstm_skew_option_pricing/
├── README.md
├── requirements.txt
├── config.py                  every setting: years, filters, splits, features, network size
├── run_all.py                 runs steps 2 to 4 for both designs
├── paper/
│   └── LSTM_realized_skewness_SPX_options.pdf
├── pipeline/
│   ├── 01_download_wrds.py    WRDS download (OptionMetrics, TAQ 5 minute bars, VIX)
│   ├── 02_build_dataset.py    filters, rates, forwards, bounds, realized moments
│   ├── 03_train.py            trains the networks (walk forward or fixed split), saves predictions
│   └── 04_evaluate.py         benchmarks, error and IV tables, COVID window, no arbitrage, DM tests, figures
├── src/                       shared code the pipeline scripts import
│   ├── utils.py               reading WRDS files, loading the processed data, naming of trained networks
│   ├── finance.py             Black Scholes, implied vol, zero curve, forward units and no arbitrage bounds
│   ├── realized.py            realized variance, skewness and kurtosis
│   ├── model.py               the LSTM pricing network and data batching
│   └── benchmarks.py          Black Scholes variants and the ad hoc BS surface
├── results/
│   ├── tables/walk, fixed/    tables.md plus every table as csv, one folder per design
│   ├── figures/walk, fixed/   png figures
│   ├── models/walk, fixed/    training histories (weights and predictions stay local)
│   └── archive_v1_rate_input/ first specification, kept for Section 5.6 of the paper
├── tests/                     synthetic data in the WRDS layout and an end to end smoke test
└── data/                      raw and processed WRDS data (never committed)
```

## Testing without WRDS

```bash
bash tests/smoke_test.sh
```

This writes **synthetic** files in the exact WRDS layout and runs the whole pipeline in under a minute (also run by GitHub Actions on every push). The numbers it produces are fake and only show that the code runs.

## References

* Amaya, D., Christoffersen, P., Jacobs, K., Vasquez, A. (2015). Does realized skewness predict the cross section of equity returns? *Journal of Financial Economics*, 118(1), 135 to 167.
* Andersen, T. G., Bollerslev, T., Diebold, F. X., Labys, P. (2003). Modeling and forecasting realized volatility. *Econometrica*, 71(2), 579 to 625.
* Bakshi, G., Cao, C., Chen, Z. (1997). Empirical performance of alternative option pricing models. *Journal of Finance*, 52(5), 2003 to 2049.
* Diebold, F. X., Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business and Economic Statistics*, 13(3), 253 to 263.
* Dumas, B., Fleming, J., Whaley, R. E. (1998). Implied volatility functions: empirical tests. *Journal of Finance*, 53(6), 2059 to 2106.
* Hochreiter, S., Schmidhuber, J. (1997). Long short term memory. *Neural Computation*, 9(8), 1735 to 1780.
* Hutchinson, J., Lo, A., Poggio, T. (1994). A nonparametric approach to pricing and hedging derivative securities via learning networks. *Journal of Finance*, 49(3), 851 to 889.
* Ruf, J., Wang, W. (2020). Neural networks for option pricing and hedging: a literature review. *Journal of Computational Finance*, 24(1).
