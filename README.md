# RGIP Macro Model v1.0

Forward-only sector-rotation research product for the Roland George Investments Program.

**Public live: OFF.** Production shows “Model spinning up — first live call 2026-09-20 21:00 UTC. Methodology available now.” until a human reviews the first 10 days of commits and flips the live flag.

## Production setup
Add GitHub Actions secret `FRED_API_KEY`. Connect the repo to Cloudflare Pages (output `/site`) or configure Netlify secrets `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID`. Scheduled Actions require `contents: write`.

## Daily pipeline
Weekdays 21:15 UTC: `python scripts/daily_runner.py`. Order: backfill eligible forward returns → fetch FRED → fetch sector prices → compute factors → score/rank → append immutable daily row → compute metrics → memo → site.

## Weekly signal
Sunday 21:00 UTC: freeze the latest completed trading-day ranking via `python scripts/weekly_signal.py`; append the official publication to `data/weekly_signal_log.jsonl`; rebuild metrics, memo, and site. Implementation frequency is always weekly.

## How to add a factor
Do not add a factor to v1.0. Any factor/formula/loading/ranking change requires v2.0, new inception, separate log, and side-by-side display.

## How to flip public_live
After human review of the first 10 days of commits, change `spec/public_live.txt` from `false` to `true` and commit. Never edit historical log rows. The next generated row records the new flag; the next Sunday signal becomes public.

## How to troubleshoot cron failures
Check the first failed Action step. Missing FRED key → restore `FRED_API_KEY`. yfinance failure → Stooq fallback is automatic; if both fail, keep run failed. Stale factor → inspect FRED coverage; do not impute. Commit failure → check `contents: write` and branch protection. Deployment failure → check hosting credentials. Log any output-affecting issue to `spec/decisions.md`.

## Verification
`python scripts/verify.py --live-resolution` checks every frozen FRED ID, all 11 ETFs through yfinance, the 11×5 exposure matrix, a deterministic end-to-end pipeline run, exact sample-size gates, headless-browser rendering, PDF build, public-live OFF, actionlint, and README operations. The end-to-end fixture is generated ephemerally inside verification, restored immediately, and can never enter the production log.

## Immutability
`data/model_log.jsonl` is append-only. `backfill_returns.py` may alter only `forward_returns`; signal fields are immutable. `data/weekly_signal_log.jsonl` is also append-only and records only signals actually frozen by the Sunday publication workflow.
