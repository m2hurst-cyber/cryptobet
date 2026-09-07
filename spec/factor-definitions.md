# Factor definitions — Macro Model v1.0

Five factors. Each factor value on any date T is a z-score computed over the trailing 5 years of that factor's history.

## F1 — Growth
Mean of z-scores of:
- `PAYEMS` change (`units=chg`, monthly)
- `INDPRO` YoY (`units=pc1`, monthly)
- `RSAFS` YoY (`units=pc1`, monthly)

## F2 — Inflation
Mean of z-scores of:
- `CPILFESL` YoY (`units=pc1`, monthly)
- `PCEPILFE` YoY (`units=pc1`, monthly)
- `T5YIFR` level (daily, forward-filled to monthly)

## F3 — Rates
Z-score of:
- `DGS10` level (daily)

Sign convention: positive z = higher rates.

## F4 — Credit stress
Mean of z-scores of:
- `BAMLH0A0HYM2` level (daily)
- `BAMLC0A0CM` level (daily)

Sign convention: positive z = wider spreads = more stress.

## F5 — Curve steepness
Z-score of:
- `T10Y2Y` level (daily)

Sign convention: positive z = steeper.

## Standardization window
Trailing 1,260 trading days (~5 years) for daily series; trailing 60 observations for monthly series. Rolling — recompute every run.

## Missing data
If any FRED series returns fewer than 90% of expected observations in the window, factor is marked `stale` and the model publishes “No call today — data quality flag” for that date. Do not fabricate values.
