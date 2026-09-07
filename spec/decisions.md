# Macro Model v1.0 — Append-only decisions

## 2026-09-06 — Repository target
No RGIP macro repository exists in the connected GitHub account. Use the empty writable repository `m2hurst-cyber/cryptobet` and do not modify the unrelated `ClaudeHurst` CRM repository.

## 2026-09-06 — Existing RGIP dashboard source
No reusable RGIP Macro Dashboard source code was found in connected GitHub or user files. Preserve Daily Macro Pulse UX patterns and implement a separate RGIP Dashboard view mode without claiming to extend unavailable code.

## 2026-09-06 — FRED verification count inconsistency
The frozen v1.0 factor definition references 10 distinct FRED series, not “50+”. Verify every referenced v1.0 series exactly; do not invent additional series because that would change v1.0.

## 2026-09-06 — Daily compute vs weekly rebalance
Compute and append sector scores/ranks on trading days for diagnostics; freeze the official implementation signal only on Sunday at 21:00 UTC from the latest completed trading-day row. This preserves daily computation with weekly rebalance frequency.

## 2026-09-06 — Weekly metric timing
Measure frozen Sunday signal performance from the first trading-day close after publication to the first trading-day close of the following week. This implements Monday-to-Monday scoring while handling holiday Mondays without synthesizing prices. IC remains score versus 5-trading-day forward return.

## 2026-09-06 — External heatmap category
Frozen v1.0 has no External factor. Display External as context/not scored with zero model impact rather than inventing a factor; adding one requires v2.0.

## 2026-09-06 — Offline verification
Production scripts are live-data-only. Deterministic fixtures are used only inside verification and are never read by scheduled production runs.

## 2026-09-06 — Official weekly publication ledger
The daily `model_log.jsonl` records computed trading-day ranks but does not prove that a Sunday signal was actually published. Add `data/weekly_signal_log.jsonl` as a separate append-only publication ledger. `weekly_signal.py` appends the exact frozen Sunday call; reruns are idempotent and cannot overwrite a published signal. Weekly hit rate, long-short return, IC, and turnover use only this publication ledger. This adds audit evidence without changing factors, exposures, formulas, ranking, or rebalance frequency.

## Verification failure log — 2026-09-07
- 6_site_render: local container lacked Playwright's bundled Chromium. CI installs it before verification.
- 9_actionlint: local container lacked actionlint. CI installs it before verification.

## 2026-09-07 — Offline fixture implementation clarification
Final v1.0 verification generates deterministic fixtures ephemerally inside `verify.py` and restores all production data/site files byte-for-byte after the end-to-end check. No synthetic observation files are committed or available to scheduled production workflows.
