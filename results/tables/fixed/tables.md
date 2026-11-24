# Results, fixed design (test period 2019-01-02 to 2023-12-29)

1,314,360 option quotes on 1,258 days, calls 42%. COVID crash window: 52,504 quotes on 50 days.

## Pricing error, all options

Dollar errors; IV RMSE in volatility points (model implied vol minus market implied vol).

| model | RMSE | MAE | MAPE % | Bias | IV RMSE (vol pts) |
|---|---|---|---|---|---|
| BS 20% vol | 36.573 | 27.021 | 89.897 | -0.969 | 8.184 |
| BS realized vol | 51.089 | 36.523 | 56.718 | -32.335 | 10.510 |
| BS VIX | 35.144 | 23.048 | 78.196 | 8.159 | 6.706 |
| Ad hoc BS (DFW) | 11.169 | 6.704 | 15.534 | 0.913 | 2.500 |
| MLP (no memory) | 13.282 | 8.591 | 33.186 | 1.223 | 3.168 |
| LSTM w/o skew, kurt | 13.045 | 8.059 | 28.816 | 3.216 | 2.943 |
| LSTM (bounded) | 14.282 | 8.465 | 26.518 | 4.048 | 3.057 |
| LSTM raw + clamp | 13.528 | 8.065 | 29.910 | 2.934 | 5.188 |
| LSTM + smile, w/o skew | 9.522 | 4.734 | 12.848 | 0.608 | 2.440 |
| LSTM + smile, with skew | 10.206 | 5.314 | 12.037 | 1.323 | 2.370 |
| LSTM w/o skew, kurt (3 seed avg) | 12.283 | 7.404 | 22.688 | 2.567 | 2.713 |
| LSTM bounded (3 seed avg) | 13.258 | 7.682 | 21.280 | 2.922 | 2.868 |
| LSTM + smile, w/o skew (3 seed avg) | 8.702 | 4.488 | 13.996 | 0.838 | 2.284 |
| LSTM + smile, with skew (3 seed avg) | 9.300 | 5.062 | 14.289 | 1.619 | 2.267 |

## Pricing error outside the COVID crash window

| model | RMSE | MAE | MAPE % | Bias | IV RMSE (vol pts) |
|---|---|---|---|---|---|
| BS 20% vol | 34.122 | 25.728 | 91.152 | 1.269 | 6.937 |
| BS realized vol | 49.857 | 35.909 | 55.753 | -34.414 | 10.217 |
| BS VIX | 30.465 | 21.422 | 76.737 | 6.082 | 6.081 |
| Ad hoc BS (DFW) | 10.008 | 6.231 | 15.203 | 0.922 | 2.018 |
| MLP (no memory) | 11.492 | 8.020 | 33.280 | 1.709 | 2.542 |
| LSTM w/o skew, kurt | 11.120 | 7.475 | 29.035 | 4.062 | 2.192 |
| LSTM (bounded) | 11.940 | 7.782 | 26.623 | 5.103 | 2.128 |
| LSTM raw + clamp | 10.794 | 7.266 | 29.261 | 4.016 | 4.688 |
| LSTM + smile, w/o skew | 6.291 | 4.055 | 12.580 | 1.392 | 1.329 |
| LSTM + smile, with skew | 7.183 | 4.561 | 11.693 | 2.266 | 1.334 |
| LSTM w/o skew, kurt (3 seed avg) | 10.250 | 6.822 | 22.755 | 3.422 | 1.881 |
| LSTM bounded (3 seed avg) | 10.617 | 6.956 | 21.199 | 3.957 | 1.837 |
| LSTM + smile, w/o skew (3 seed avg) | 5.975 | 3.914 | 13.842 | 1.499 | 1.359 |
| LSTM + smile, with skew (3 seed avg) | 6.920 | 4.490 | 14.148 | 2.353 | 1.363 |

## RMSE by period ($)

| period | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| COVID crash 2020-02-20 to 2020-04-30 | 52,504 | 74.176 | 74.813 | 92.805 | 26.752 | 35.249 | 35.890 | 40.988 | 42.204 | 36.313 | 36.978 | 35.384 | 41.123 | 32.213 | 31.849 |
| Rest of test period | 1,261,856 | 34.122 | 49.857 | 30.465 | 10.008 | 11.492 | 11.120 | 11.940 | 10.794 | 6.291 | 7.183 | 10.250 | 10.617 | 5.975 | 6.920 |

## RMSE by year ($)

| year | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 160,424 | 26.304 | 26.480 | 14.223 | 6.101 | 6.542 | 5.218 | 5.662 | 5.641 | 3.412 | 3.641 | 5.007 | 5.365 | 3.185 | 3.609 |
| 2020 | 218,461 | 47.261 | 56.993 | 52.022 | 15.723 | 20.150 | 21.159 | 22.342 | 22.739 | 18.980 | 19.292 | 20.499 | 22.268 | 17.027 | 16.918 |
| 2021 | 262,989 | 32.095 | 65.976 | 32.490 | 11.737 | 12.013 | 12.731 | 12.120 | 11.621 | 6.389 | 7.561 | 11.446 | 10.841 | 6.151 | 6.931 |
| 2022 | 337,501 | 34.810 | 46.149 | 39.384 | 10.947 | 13.291 | 11.835 | 14.493 | 11.824 | 7.282 | 8.541 | 10.844 | 11.957 | 6.874 | 8.008 |
| 2023 | 334,985 | 37.825 | 47.156 | 24.345 | 9.029 | 10.755 | 9.711 | 11.512 | 10.896 | 5.458 | 6.420 | 9.199 | 10.780 | 5.088 | 6.646 |

## RMSE by moneyness K/S ($)

| money_bucket | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <0.94 | 432,082 | 35.052 | 53.310 | 26.758 | 9.233 | 10.632 | 9.895 | 10.566 | 10.892 | 7.536 | 8.142 | 9.214 | 9.976 | 7.044 | 7.576 |
| 0.94–0.97 | 149,349 | 32.000 | 61.259 | 21.972 | 10.083 | 11.858 | 11.853 | 12.177 | 11.959 | 8.389 | 9.275 | 10.604 | 11.345 | 7.890 | 8.430 |
| 0.97–1.00 | 191,533 | 34.389 | 59.000 | 23.415 | 11.467 | 12.966 | 13.287 | 13.647 | 13.221 | 9.354 | 9.809 | 12.070 | 12.499 | 8.587 | 9.078 |
| 1.00–1.03 | 188,210 | 39.301 | 51.474 | 31.968 | 12.379 | 15.628 | 14.502 | 16.206 | 14.791 | 10.508 | 11.236 | 13.829 | 14.724 | 9.442 | 10.276 |
| 1.03–1.06 | 130,059 | 40.885 | 40.629 | 41.074 | 11.961 | 15.465 | 15.450 | 17.532 | 15.818 | 11.084 | 11.652 | 14.828 | 16.172 | 9.789 | 10.690 |
| >1.06 | 223,127 | 39.018 | 34.268 | 57.006 | 13.272 | 15.377 | 15.832 | 18.044 | 16.494 | 11.712 | 12.624 | 15.316 | 16.946 | 10.675 | 11.153 |

## RMSE by days to expiry ($)

| dte_bucket | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <30d | 240,361 | 16.964 | 14.569 | 10.858 | 6.029 | 7.853 | 6.992 | 6.648 | 6.810 | 5.841 | 5.369 | 6.303 | 6.376 | 5.416 | 5.437 |
| 30–90d | 500,729 | 28.906 | 30.598 | 21.766 | 8.751 | 9.716 | 9.489 | 9.787 | 9.737 | 7.955 | 7.811 | 8.907 | 9.387 | 7.310 | 7.250 |
| >90d | 573,270 | 47.077 | 71.256 | 48.667 | 14.279 | 17.209 | 17.059 | 19.118 | 17.813 | 11.760 | 13.169 | 16.124 | 17.578 | 10.708 | 11.832 |

## RMSE by volatility regime ($)

| vix_regime | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VIX<15 | 217,437 | 41.983 | 38.890 | 19.435 | 8.084 | 7.605 | 7.276 | 7.901 | 7.999 | 4.783 | 4.587 | 7.738 | 7.644 | 4.458 | 4.730 |
| VIX 15–25 | 742,092 | 29.202 | 52.194 | 25.754 | 9.643 | 11.044 | 10.316 | 11.029 | 10.128 | 5.515 | 6.442 | 9.454 | 9.912 | 5.266 | 6.286 |
| VIX>25 | 354,831 | 45.729 | 55.172 | 54.372 | 15.085 | 19.052 | 19.374 | 21.516 | 20.594 | 16.070 | 16.915 | 18.310 | 20.245 | 14.503 | 14.968 |

## RMSE by option type ($)

| cp_flag | n | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 558,379 | 36.951 | 47.470 | 40.204 | 10.365 | 13.072 | 12.785 | 14.311 | 13.142 | 8.307 | 8.992 | 12.042 | 13.092 | 7.378 | 8.244 |
| P | 755,981 | 36.292 | 53.605 | 30.877 | 11.727 | 13.436 | 13.233 | 14.261 | 13.805 | 10.329 | 11.017 | 12.458 | 13.380 | 9.563 | 10.009 |

## IV RMSE by year (vol points)

| year | BS 20% vol | BS realized vol | BS VIX | Ad hoc BS (DFW) | MLP (no memory) | LSTM w/o skew, kurt | LSTM (bounded) | LSTM raw + clamp | LSTM + smile, w/o skew | LSTM + smile, with skew | LSTM w/o skew, kurt (3 seed avg) | LSTM bounded (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | LSTM + smile, with skew (3 seed avg) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 6.26 | 9.00 | 5.56 | 1.80 | 2.09 | 1.72 | 1.56 | 4.09 | 1.02 | 1.05 | 1.41 | 1.37 | 1.10 | 1.09 |
| 2020 | 13.75 | 13.49 | 9.63 | 4.32 | 5.53 | 5.47 | 5.89 | 7.24 | 5.27 | 5.04 | 5.30 | 5.80 | 4.78 | 4.71 |
| 2021 | 6.78 | 12.37 | 6.70 | 2.15 | 2.60 | 2.29 | 2.11 | 4.36 | 1.23 | 1.27 | 1.98 | 1.86 | 1.26 | 1.26 |
| 2022 | 7.17 | 8.56 | 6.07 | 2.10 | 2.81 | 2.41 | 2.53 | 5.13 | 1.59 | 1.62 | 2.10 | 2.13 | 1.60 | 1.62 |
| 2023 | 5.73 | 9.05 | 5.38 | 1.65 | 2.02 | 1.74 | 1.71 | 4.69 | 1.00 | 1.01 | 1.44 | 1.48 | 1.06 | 1.10 |

## Random seeds ($)

The two LSTMs retrained from different random starting points.

| model | seed | RMSE | RMSE outside COVID window |
|---|---|---|---|
| LSTM w/o skew, kurt | 42 | 13.04 | 11.12 |
| LSTM w/o skew, kurt | 1 | 12.77 | 10.52 |
| LSTM w/o skew, kurt | 2 | 11.94 | 10.09 |
| LSTM w/o skew, kurt | average of seeds | 12.28 | 10.25 |
| LSTM (bounded) | 42 | 14.28 | 11.94 |
| LSTM (bounded) | 1 | 13.47 | 10.63 |
| LSTM (bounded) | 2 | 12.85 | 10.25 |
| LSTM (bounded) | average of seeds | 13.26 | 10.62 |
| LSTM + smile, w/o skew | 42 | 9.52 | 6.29 |
| LSTM + smile, w/o skew | 1 | 9.20 | 6.27 |
| LSTM + smile, w/o skew | 2 | 8.37 | 6.47 |
| LSTM + smile, w/o skew | average of seeds | 8.70 | 5.98 |
| LSTM + smile, with skew | 42 | 10.21 | 7.18 |
| LSTM + smile, with skew | 1 | 9.31 | 6.95 |
| LSTM + smile, with skew | 2 | 9.53 | 7.69 |
| LSTM + smile, with skew | average of seeds | 9.30 | 6.92 |

## No arbitrage checks

Bound violations are per quote. Monotonicity and convexity are checked on neighbouring strikes of the same expiry (convexity tolerance 0.001 in slope).

| series | below lower bound % | above upper bound % | monotonicity in K violated % | convexity in K violated % |
|---|---|---|---|---|
| LSTM raw before clamp | 3.07 | 0.00 |  |  |
| Market mid |  |  | 0.03 | 11.30 |
| BS 20% vol |  |  | 0.00 | 0.00 |
| BS realized vol |  |  | 0.00 | 0.00 |
| BS VIX |  |  | 0.00 | 0.00 |
| Ad hoc BS (DFW) |  |  | 0.04 | 0.00 |
| MLP (no memory) |  |  | 0.42 | 13.44 |
| LSTM w/o skew, kurt |  |  | 0.19 | 16.55 |
| LSTM (bounded) |  |  | 0.10 | 16.59 |
| LSTM raw + clamp |  |  | 3.80 | 21.05 |
| LSTM + smile, w/o skew |  |  | 0.15 | 18.00 |
| LSTM + smile, with skew |  |  | 0.12 | 16.22 |
| LSTM w/o skew, kurt (3 seed avg) |  |  | 0.08 | 13.87 |
| LSTM bounded (3 seed avg) |  |  | 0.04 | 16.73 |
| LSTM + smile, w/o skew (3 seed avg) |  |  | 0.04 | 17.02 |
| LSTM + smile, with skew (3 seed avg) |  |  | 0.06 | 17.17 |

## Diebold Mariano tests

Daily mean squared $ error, Newey West with 5 lags. Below -1.96: first model significantly better; above 1.96: significantly worse.

| model | vs | DM all | DM outside COVID window |
|---|---|---|---|
| LSTM (bounded) | BS 20% vol | -17.63 | -24.69 |
| LSTM (bounded) | BS realized vol | -17.23 | -20.20 |
| LSTM (bounded) | BS VIX | -8.40 | -13.67 |
| LSTM (bounded) | Ad hoc BS (DFW) | 2.18 | 3.93 |
| LSTM (bounded) | MLP (no memory) | 1.39 | 0.68 |
| LSTM (bounded) | LSTM w/o skew, kurt | 1.96 | 1.58 |
| LSTM (bounded) | LSTM raw + clamp | 2.09 | 3.91 |
| LSTM (bounded) | LSTM + smile, w/o skew | 8.63 | 10.86 |
| LSTM (bounded) | LSTM + smile, with skew | 7.07 | 11.08 |
| LSTM bounded (3 seed avg) | LSTM w/o skew, kurt (3 seed avg) | 1.63 | 0.51 |
| LSTM w/o skew, kurt (3 seed avg) | Ad hoc BS (DFW) | 1.38 | 1.16 |
| LSTM bounded (3 seed avg) | Ad hoc BS (DFW) | 1.53 | 1.48 |
| MLP (no memory) | Ad hoc BS (DFW) | 2.61 | 5.27 |
| LSTM + smile, w/o skew (3 seed avg) | Ad hoc BS (DFW) | -2.16 | -13.02 |
| LSTM + smile, with skew (3 seed avg) | Ad hoc BS (DFW) | -1.85 | -10.57 |
| LSTM + smile, with skew (3 seed avg) | LSTM + smile, w/o skew (3 seed avg) | 4.05 | 7.86 |
| LSTM + smile, w/o skew (3 seed avg) | LSTM w/o skew, kurt (3 seed avg) | -10.32 | -11.87 |
