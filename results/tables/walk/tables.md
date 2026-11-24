# Results, walk design (test period 2019-01-02 to 2023-12-29)

1,314,360 option quotes on 1,258 days, calls 42%. COVID crash window: 52,504 quotes on 50 days.

## Pricing error, all options

Dollar errors; IV RMSE in volatility points (model implied vol minus market implied vol).

| model | RMSE | MAE | MAPE % | Bias | IV RMSE (vol pts) |
|---|---|---|---|---|---|
| BS 20% vol | 36.573 | 27.021 | 89.897 | -0.969 | 8.184 |
| BS realized vol | 51.089 | 36.523 | 56.718 | -32.335 | 10.510 |
| BS VIX | 35.144 | 23.048 | 78.196 | 8.159 | 6.706 |
| Ad hoc BS (DFW) | 11.169 | 6.704 | 15.534 | 0.913 | 2.500 |
| MLP (no memory) | 12.916 | 7.849 | 22.218 | 0.036 | 2.850 |
| LSTM w/o skew, kurt | 11.872 | 7.256 | 26.107 | 1.886 | 2.805 |
| LSTM (bounded) | 13.324 | 8.071 | 23.778 | 3.248 | 2.847 |
| LSTM raw + clamp | 12.998 | 8.014 | 27.378 | 2.609 | 5.255 |
| LSTM + smile, w/o skew | 8.760 | 4.650 | 17.484 | 0.458 | 2.498 |
| LSTM + smile, with skew | 10.122 | 5.106 | 16.325 | 0.374 | 2.658 |
| LSTM w/o skew, kurt (3 seed avg) | 11.952 | 7.192 | 23.447 | 2.311 | 2.739 |
| LSTM bounded (3 seed avg) | 12.757 | 7.671 | 23.304 | 3.110 | 2.769 |
| LSTM + smile, w/o skew (3 seed avg) | 8.478 | 4.503 | 17.192 | 0.718 | 2.372 |
| LSTM + smile, with skew (3 seed avg) | 8.634 | 4.565 | 16.397 | 0.770 | 2.381 |

## Pricing error outside the COVID crash window

| model | RMSE | MAE | MAPE % | Bias | IV RMSE (vol pts) |
|---|---|---|---|---|---|
| BS 20% vol | 34.122 | 25.728 | 91.152 | 1.269 | 6.937 |
| BS realized vol | 49.857 | 35.909 | 55.753 | -34.414 | 10.217 |
| BS VIX | 30.465 | 21.422 | 76.737 | 6.082 | 6.081 |
| Ad hoc BS (DFW) | 10.008 | 6.231 | 15.203 | 0.922 | 2.018 |
| MLP (no memory) | 10.896 | 7.250 | 22.101 | 0.570 | 2.045 |
| LSTM w/o skew, kurt | 10.191 | 6.746 | 26.244 | 2.563 | 2.089 |
| LSTM (bounded) | 11.386 | 7.494 | 23.752 | 4.112 | 2.021 |
| LSTM raw + clamp | 10.803 | 7.358 | 27.015 | 3.479 | 4.757 |
| LSTM + smile, w/o skew | 6.018 | 4.072 | 17.396 | 1.124 | 1.561 |
| LSTM + smile, with skew | 6.423 | 4.316 | 16.119 | 1.299 | 1.542 |
| LSTM w/o skew, kurt (3 seed avg) | 9.917 | 6.623 | 23.562 | 3.171 | 1.904 |
| LSTM bounded (3 seed avg) | 10.525 | 7.025 | 23.348 | 4.083 | 1.896 |
| LSTM + smile, w/o skew (3 seed avg) | 5.861 | 3.961 | 17.157 | 1.351 | 1.516 |
| LSTM + smile, with skew (3 seed avg) | 5.951 | 3.992 | 16.270 | 1.441 | 1.447 |

## RMSE by period ($)

| period | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| COVID crash 2020-02-20 to 2020-04-30 | 52,504 | 74.176 | 74.813 | 92.805 | 26.752 | 36.366 | 32.127 | 36.449 | 37.746 | 32.413 | 39.662 | 34.820 | 37.568 | 31.202 | 31.861 |
| Rest of test period | 1,261,856 | 34.122 | 49.857 | 30.465 | 10.008 | 10.896 | 10.191 | 11.386 | 10.803 | 6.018 | 6.423 | 9.917 | 10.525 | 5.861 | 5.951 |

## RMSE by year ($)

| year | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 160,424 | 26.304 | 26.480 | 14.223 | 6.101 | 6.542 | 5.218 | 5.662 | 5.641 | 3.412 | 3.641 | 5.007 | 5.365 | 3.185 | 3.609 |
| 2020 | 218,461 | 47.261 | 56.993 | 52.022 | 15.723 | 20.663 | 19.974 | 20.585 | 21.252 | 17.093 | 20.494 | 20.165 | 20.975 | 16.484 | 16.983 |
| 2021 | 262,989 | 32.095 | 65.976 | 32.490 | 11.737 | 10.903 | 12.450 | 13.939 | 12.105 | 6.918 | 8.004 | 11.824 | 12.375 | 7.114 | 6.866 |
| 2022 | 337,501 | 34.810 | 46.149 | 39.384 | 10.947 | 13.699 | 10.503 | 11.625 | 9.951 | 6.906 | 6.388 | 11.176 | 10.708 | 6.330 | 6.130 |
| 2023 | 334,985 | 37.825 | 47.156 | 24.345 | 9.029 | 8.554 | 6.852 | 10.779 | 11.761 | 4.401 | 5.507 | 6.905 | 10.103 | 4.452 | 4.826 |

## RMSE by moneyness K/S ($)

| money_bucket | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <0.94 | 432,082 | 35.052 | 53.310 | 26.758 | 9.233 | 10.320 | 9.270 | 9.942 | 10.539 | 7.055 | 8.113 | 9.204 | 9.691 | 6.801 | 6.858 |
| 0.94–0.97 | 149,349 | 32.000 | 61.259 | 21.972 | 10.083 | 11.627 | 11.263 | 11.720 | 11.845 | 8.162 | 9.897 | 10.871 | 11.402 | 7.887 | 8.077 |
| 0.97–1.00 | 191,533 | 34.389 | 59.000 | 23.415 | 11.467 | 12.826 | 12.702 | 13.739 | 12.873 | 9.263 | 10.722 | 12.057 | 12.886 | 8.887 | 8.961 |
| 1.00–1.03 | 188,210 | 39.301 | 51.474 | 31.968 | 12.379 | 14.984 | 13.740 | 15.328 | 14.478 | 9.490 | 11.466 | 13.890 | 14.738 | 9.498 | 9.992 |
| 1.03–1.06 | 130,059 | 40.885 | 40.629 | 41.074 | 11.961 | 15.073 | 13.827 | 16.180 | 15.086 | 9.087 | 11.039 | 14.364 | 15.538 | 9.092 | 9.498 |
| >1.06 | 223,127 | 39.018 | 34.268 | 57.006 | 13.272 | 14.930 | 13.027 | 15.799 | 15.313 | 10.645 | 11.397 | 13.802 | 14.941 | 10.004 | 9.933 |

## RMSE by days to expiry ($)

| dte_bucket | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <30d | 240,361 | 16.964 | 14.569 | 10.858 | 6.029 | 6.801 | 6.985 | 6.472 | 7.379 | 6.146 | 6.590 | 6.631 | 6.330 | 5.848 | 6.027 |
| 30–90d | 500,729 | 28.906 | 30.598 | 21.766 | 8.751 | 9.556 | 8.943 | 9.401 | 10.074 | 7.781 | 8.863 | 8.924 | 9.292 | 7.357 | 7.613 |
| >90d | 573,270 | 47.077 | 71.256 | 48.667 | 14.279 | 16.832 | 15.258 | 17.671 | 16.610 | 10.355 | 12.168 | 15.476 | 16.760 | 10.157 | 10.250 |

## RMSE by volatility regime ($)

| vix_regime | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VIX<15 | 217,437 | 41.983 | 38.890 | 19.435 | 8.084 | 6.203 | 5.632 | 7.731 | 7.892 | 3.942 | 4.035 | 5.816 | 7.180 | 3.865 | 3.856 |
| VIX 15–25 | 742,092 | 29.202 | 52.194 | 25.754 | 9.643 | 10.346 | 9.794 | 11.583 | 11.054 | 5.730 | 6.371 | 9.295 | 10.434 | 5.618 | 5.699 |
| VIX>25 | 354,831 | 45.729 | 55.172 | 54.372 | 15.085 | 19.248 | 17.378 | 18.449 | 18.223 | 14.355 | 16.871 | 18.102 | 18.534 | 13.823 | 14.110 |

## RMSE by option type ($)

| cp_flag | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 558,379 | 36.951 | 47.470 | 40.204 | 10.365 | 12.880 | 11.644 | 13.157 | 12.920 | 7.702 | 9.198 | 11.594 | 12.436 | 7.194 | 7.648 |
| P | 755,981 | 36.292 | 53.605 | 30.877 | 11.727 | 12.942 | 12.037 | 13.446 | 13.056 | 9.466 | 10.753 | 12.209 | 12.988 | 9.313 | 9.295 |

## IV RMSE by year (vol points)

| year | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 6.26 | 9.00 | 5.56 | 1.80 | 2.09 | 1.72 | 1.56 | 4.09 | 1.02 | 1.05 | 1.41 | 1.37 | 1.10 | 1.09 |
| 2020 | 13.75 | 13.49 | 9.63 | 4.32 | 5.39 | 5.35 | 5.61 | 7.97 | 5.20 | 5.62 | 5.35 | 5.41 | 4.83 | 4.99 |
| 2021 | 6.78 | 12.37 | 6.70 | 2.15 | 2.00 | 2.14 | 2.03 | 4.41 | 1.86 | 2.06 | 2.02 | 2.14 | 1.76 | 1.64 |
| 2022 | 7.17 | 8.56 | 6.07 | 2.10 | 2.43 | 1.92 | 2.16 | 4.25 | 1.64 | 1.49 | 1.92 | 1.99 | 1.60 | 1.43 |
| 2023 | 5.73 | 9.05 | 5.38 | 1.65 | 1.32 | 1.86 | 1.49 | 5.05 | 0.95 | 1.00 | 1.70 | 1.59 | 1.12 | 1.11 |

## Random seeds ($)

The two LSTMs retrained from different random starting points.

| model | seed | RMSE | RMSE outside COVID window |
|---|---|---|---|
| LSTM w/o skew, kurt | 42 | 11.87 | 10.19 |
| LSTM w/o skew, kurt | 1 | 11.95 | 9.79 |
| LSTM w/o skew, kurt | 2 | 14.10 | 12.16 |
| LSTM w/o skew, kurt | average of seeds | 11.95 | 9.92 |
| LSTM (bounded) | 42 | 13.32 | 11.39 |
| LSTM (bounded) | 1 | 13.28 | 10.82 |
| LSTM (bounded) | 2 | 13.65 | 11.58 |
| LSTM (bounded) | average of seeds | 12.76 | 10.53 |
| LSTM + smile, w/o skew | 42 | 8.76 | 6.02 |
| LSTM + smile, w/o skew | 1 | 9.25 | 6.53 |
| LSTM + smile, w/o skew | 2 | 8.44 | 6.24 |
| LSTM + smile, w/o skew | average of seeds | 8.48 | 5.86 |
| LSTM + smile, with skew | 42 | 10.12 | 6.42 |
| LSTM + smile, with skew | 1 | 8.79 | 6.62 |
| LSTM + smile, with skew | 2 | 8.63 | 6.58 |
| LSTM + smile, with skew | average of seeds | 8.63 | 5.95 |

## No arbitrage checks

Bound violations are per quote. Monotonicity and convexity are checked on neighbouring strikes of the same expiry (convexity tolerance 0.001 in slope).

| series | below lower bound % | above upper bound % | monotonicity in K violated % | convexity in K violated % |
|---|---|---|---|---|
| LSTM raw before clamp | 2.85 | 0.00 |  |  |
| Market mid |  |  | 0.03 | 11.30 |
| BS 20% vol |  |  | 0.00 | 0.00 |
| BS realized vol |  |  | 0.00 | 0.00 |
| BS VIX |  |  | 0.00 | 0.00 |
| Ad hoc BS (DFW) |  |  | 0.04 | 0.00 |
| MLP (no memory) |  |  | 0.23 | 11.69 |
| LSTM w/o skew, kurt |  |  | 0.17 | 16.86 |
| LSTM (bounded) |  |  | 0.10 | 15.96 |
| LSTM raw + clamp |  |  | 3.13 | 20.96 |
| LSTM + smile, w/o skew |  |  | 0.27 | 18.22 |
| LSTM + smile, with skew |  |  | 0.16 | 17.34 |
| LSTM w/o skew, kurt (3 seed avg) |  |  | 0.06 | 15.01 |
| LSTM bounded (3 seed avg) |  |  | 0.06 | 15.86 |
| LSTM + smile, w/o skew (3 seed avg) |  |  | 0.12 | 17.56 |
| LSTM + smile, with skew (3 seed avg) |  |  | 0.12 | 16.95 |

## Diebold Mariano tests

Daily mean squared $ error, Newey West with 5 lags. Below -1.96: first model significantly better; above 1.96: significantly worse.

| model | vs | DM all | DM outside COVID window |
|---|---|---|---|
| LSTM (bounded) | BS 20% vol | -16.18 | -24.18 |
| LSTM (bounded) | BS realized vol | -17.59 | -20.34 |
| LSTM (bounded) | BS VIX | -8.02 | -12.64 |
| LSTM (bounded) | Ad hoc BS (DFW) | 2.17 | 3.66 |
| LSTM (bounded) | MLP (no memory) | 1.34 | 1.44 |
| LSTM (bounded) | LSTM w/o skew, kurt | 2.62 | 2.37 |
| LSTM (bounded) | LSTM raw + clamp | 1.30 | 2.08 |
| LSTM (bounded) | LSTM + smile, w/o skew | 9.28 | 11.94 |
| LSTM (bounded) | LSTM + smile, with skew | 7.60 | 12.03 |
| LSTM bounded (3 seed avg) | LSTM w/o skew, kurt (3 seed avg) | 2.49 | 1.67 |
| LSTM w/o skew, kurt (3 seed avg) | Ad hoc BS (DFW) | 1.17 | 0.57 |
| LSTM bounded (3 seed avg) | Ad hoc BS (DFW) | 1.61 | 1.75 |
| MLP (no memory) | Ad hoc BS (DFW) | 1.89 | 2.93 |
| LSTM + smile, w/o skew (3 seed avg) | Ad hoc BS (DFW) | -2.61 | -13.80 |
| LSTM + smile, with skew (3 seed avg) | Ad hoc BS (DFW) | -2.35 | -12.59 |
| LSTM + smile, with skew (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | 2.31 | 1.83 |
| LSTM + smile, w/o skew (3 seed avg) | LSTM w/o skew, kurt (3 seed avg) | -9.10 | -11.54 |
