# AGENT BRIEF — Macro Model v1.0

This repository implements the frozen Macro Model v1.0 contract. The controlling machine-readable/model details live in `/spec/v1.0-spec.md`, `/spec/factor-definitions.md`, and `/spec/exposure-matrix.csv`; `/spec/decisions.md` is append-only.

## Product objective

Ship one web product with two view modes: Daily Macro Pulse and RGIP Macro Dashboard. It must show the daily-computed sector ranking, the frozen weekly sector call and accumulating live track record, interactive primary-source drill-downs, and public methodology.

## Frozen rules

- Universe: XLK, XLF, XLE, XLI, XLV, XLY, XLP, XLU, XLB, XLRE, XLC.
- Weekly implementation only. Official signal freezes Sunday 21:00 UTC for the next market open.
- Rank by frozen composite score; top 3 OW, bottom 3 UW, middle 5 Neutral; exact ties alphabetical by ticker.
- Benchmark: equal-weight basket of all 11 sectors; never SPY.
- Five frozen factors: Growth, Inflation, Rates, Credit Stress, Curve Steepness.
- Exposure matrix is frozen in `/spec/exposure-matrix.csv`.
- `data/model_log.jsonl` and `data/weekly_signal_log.jsonl` are append-only. Signal fields are immutable; only `forward_returns` may be backfilled.
- `public_live` ships OFF. Human review of the first 10 days of commits is required before manually flipping `spec/public_live.txt`.
- Any factor, formula, exposure, or ranking-rule change requires v2.0 with a new inception date and separate log.

## Build contract

Production data come from FRED and sector ETF market prices. Missing/stale data suppress the call rather than being fabricated. Scheduled workflows run weekdays at 21:15 UTC and Sundays at 21:00 UTC. Public methodology is generated from `/spec/methodology.md` to `/site/assets/methodology.pdf`. `scripts/verify.py` is the acceptance gate.

## Out of scope for v1.0

No strategy backtest, discretionary override, multiple versions in parallel, accounts/authentication, payments, email/push alerts, portfolio overlays, or external API product.

Do not optimize, refactor, or extend v1.0 after all acceptance gates pass. The next work item is human review of the accumulating live log.
