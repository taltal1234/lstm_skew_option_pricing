# Results (test period 2019-01-02 to 2023-12-29)

1,314,360 option quotes on 1,258 days, calls 42%.

## Pricing error, all options ($)

| model | RMSE | MAE | MAPE % | Bias |
|---|---|---|---|---|
| BS 20% vol | 36.573 | 27.021 | 89.897 | -0.969 |
| BS realized vol | 51.089 | 36.523 | 56.718 | -32.335 |
| BS VIX | 35.144 | 23.048 | 78.196 | 8.159 |
| Ad hoc BS (DFW) | 11.169 | 6.704 | 15.534 | 0.913 |
| MLP (no memory) | 34.312 | 21.419 | 37.606 | -5.291 |
| LSTM w/o skew, kurt | 46.820 | 29.202 | 41.513 | -27.862 |
| LSTM (bounded) | 31.469 | 19.627 | 32.835 | -14.476 |
| LSTM raw + clamp | 58.290 | 35.961 | 171.220 | 3.037 |

## RMSE by moneyness K/S ($)

| money_bucket | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp |
|---|---|---|---|---|---|---|---|---|---|
| <0.94 | 432,082 | 35.052 | 53.310 | 26.758 | 9.233 | 30.447 | 29.528 | 18.645 | 70.822 |
| 0.94–0.97 | 149,349 | 32.000 | 61.259 | 21.972 | 10.083 | 39.686 | 43.281 | 24.479 | 43.771 |
| 0.97–1.00 | 191,533 | 34.389 | 59.000 | 23.415 | 11.467 | 38.106 | 54.749 | 32.959 | 52.752 |
| 1.00–1.03 | 188,210 | 39.301 | 51.474 | 31.968 | 12.379 | 36.241 | 67.269 | 43.705 | 61.051 |
| 1.03–1.06 | 130,059 | 40.885 | 40.629 | 41.074 | 11.961 | 34.522 | 56.427 | 39.203 | 56.149 |
| >1.06 | 223,127 | 39.018 | 34.268 | 57.006 | 13.272 | 32.201 | 41.527 | 36.328 | 40.609 |

## RMSE by days to expiry ($)

| dte_bucket | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp |
|---|---|---|---|---|---|---|---|---|---|
| <30d | 240,361 | 16.964 | 14.569 | 10.858 | 6.029 | 11.294 | 17.930 | 13.891 | 33.827 |
| 30–90d | 500,729 | 28.906 | 30.598 | 21.766 | 8.751 | 19.692 | 34.261 | 26.184 | 45.231 |
| >90d | 573,270 | 47.077 | 71.256 | 48.667 | 14.279 | 48.033 | 62.176 | 39.884 | 74.319 |

## RMSE by volatility regime ($)

| vix_regime | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp |
|---|---|---|---|---|---|---|---|---|---|
| VIX<15 | 217,437 | 41.983 | 38.890 | 19.435 | 8.084 | 40.843 | 46.345 | 26.521 | 84.121 |
| VIX 15–25 | 742,092 | 29.202 | 52.194 | 25.754 | 9.643 | 29.215 | 47.276 | 27.472 | 53.135 |
| VIX>25 | 354,831 | 45.729 | 55.172 | 54.372 | 15.085 | 39.418 | 46.146 | 40.729 | 48.423 |

## RMSE by option type ($)

| cp_flag | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp |
|---|---|---|---|---|---|---|---|---|---|
| C | 558,379 | 36.951 | 47.470 | 40.204 | 10.365 | 32.665 | 48.970 | 34.216 | 53.044 |
| P | 755,981 | 36.292 | 53.605 | 30.877 | 11.727 | 35.480 | 45.166 | 29.275 | 61.880 |

## No arbitrage checks

Bound violations are per quote. Monotonicity and convexity are checked on neighbouring strikes of the same expiry (convexity tolerance 0.001 in slope).

| series | below lower bound % | above upper bound % | monotonicity in K violated % | convexity in K violated % |
|---|---|---|---|---|
| LSTM raw before clamp | 11.50 | 0.00 |  |  |
| Market mid |  |  | 0.03 | 11.30 |
| BS 20% vol |  |  | 0.00 | 0.00 |
| BS realized vol |  |  | 0.00 | 0.00 |
| BS VIX |  |  | 0.00 | 0.00 |
| Ad hoc BS (DFW) |  |  | 0.04 | 0.00 |
| MLP (no memory) |  |  | 2.25 | 13.26 |
| LSTM w/o skew, kurt |  |  | 1.44 | 14.56 |
| LSTM (bounded) |  |  | 2.11 | 13.25 |
| LSTM raw + clamp |  |  | 15.46 | 24.75 |

## Diebold Mariano: LSTM (bounded) vs each model

Daily mean squared $ error, Newey West with 5 lags. Below -1.96: LSTM significantly better; above 1.96: significantly worse.

| vs | DM stat |
|---|---|
| BS 20% vol | -6.53 |
| BS realized vol | -10.55 |
| BS VIX | -2.49 |
| Ad hoc BS (DFW) | 8.47 |
| MLP (no memory) | -2.88 |
| LSTM w/o skew, kurt | -8.27 |
| LSTM raw + clamp | -7.98 |
