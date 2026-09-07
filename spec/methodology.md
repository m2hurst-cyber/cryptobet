% Macro Model v1.0 Methodology
% Roland George Investments Program
% 2026-09-06

# 1. Objective and scope
Macro Model v1.0 is a forward-only, live sector-rotation model. It converts five observable macro factors into relative scores for the eleven Select Sector SPDR ETFs. It intentionally ships without an historical strategy backtest; evaluation begins prospectively at inception.

# 2. Universe and rebalance rule
Universe: XLK, XLF, XLE, XLI, XLV, XLY, XLP, XLU, XLB, XLRE, XLC. Rebalance frequency is weekly. Signals publish Sunday 21:00 UTC for the next market open. The benchmark is the equal-weight basket of all eleven sectors. Top three scores are Overweight, bottom three Underweight, middle five Neutral; exact ties are alphabetical by ticker.

# 3. Factor definitions
**Growth:** mean of rolling z-scores of PAYEMS change, INDPRO YoY, and RSAFS YoY, each over 60 monthly observations.

**Inflation:** mean of rolling z-scores of CPILFESL YoY, PCEPILFE YoY, and T5YIFR level forward-filled monthly, each over 60 monthly observations.

**Rates:** z-score of DGS10 level over trailing 1,260 trading days; positive means higher rates.

**Credit stress:** mean of z-scores of BAMLH0A0HYM2 and BAMLC0A0CM over trailing 1,260 trading days; positive means wider spreads/more stress.

**Curve steepness:** z-score of T10Y2Y over trailing 1,260 trading days; positive means steeper.

If any underlying series has fewer than 90% of expected observations, its factor is stale and the model publishes no call for that date.

# 4. Exposure matrix
|Ticker|Growth|Inflation|Rates|Credit stress|Curve steepness|
|---|---:|---:|---:|---:|---:|
|XLK|0.5|-0.3|-1.0|-0.5|0.2|
|XLF|0.5|0.3|0.8|-0.8|1.0|
|XLE|0.3|1.0|0.2|-0.3|0.3|
|XLI|1.0|0.2|0.2|-0.5|0.5|
|XLV|-0.2|-0.2|-0.3|0.3|-0.2|
|XLY|0.8|-0.3|-0.5|-0.8|0.3|
|XLP|-0.5|0.2|-0.3|0.5|-0.3|
|XLU|-0.5|-0.5|-1.0|0.5|-0.5|
|XLB|0.7|0.7|0.2|-0.5|0.5|
|XLRE|-0.3|-0.3|-1.0|-0.5|-0.3|
|XLC|0.3|-0.2|-0.5|-0.3|0.1|

Loadings are frozen first-principles priors: cyclicals receive positive Growth exposure; duration-sensitive sectors negative Rates exposure; lenders positive curve exposure; Energy/Materials higher Inflation exposure; financing-sensitive sectors negative Credit-stress exposure. The matrix is not estimated from historical ETF returns.

## Loading rationale by sector

Each sentence below explains all five frozen loadings in row order: Growth, Inflation, Rates, Credit stress, Curve steepness. These are economic priors, not fitted coefficients.

- **XLK (0.5, -0.3, -1.0, -0.5, 0.2):** moderate Growth exposure reflects cyclical enterprise/consumer technology demand; negative Inflation reflects margin and valuation pressure from persistent price growth; the -1.0 Rates loading reflects long-duration cash-flow valuation sensitivity; negative Credit stress reflects risk-premium and funding sensitivity; modest positive Curve exposure reflects some benefit from improved nominal-growth expectations without making curve shape a primary driver.
- **XLF (0.5, 0.3, 0.8, -0.8, 1.0):** positive Growth supports loan demand and credit formation; modest positive Inflation can support nominal revenues; positive Rates can lift asset yields; negative Credit stress captures deterioration in borrower quality/funding markets; +1.0 Curve steepness reflects the first-principles importance of maturity transformation and net-interest economics.
- **XLE (0.3, 1.0, 0.2, -0.3, 0.3):** modest Growth supports energy demand; +1.0 Inflation reflects direct commodity-price exposure; Rates are only a small positive nominal-growth proxy; Credit stress is mildly adverse through capital intensity/risk appetite; a steeper Curve modestly aligns with stronger nominal activity.
- **XLI (1.0, 0.2, 0.2, -0.5, 0.5):** +1.0 Growth reflects orders, production and capital-spending cyclicality; mild Inflation can accompany pricing power; Rates have a small positive nominal-demand loading but are not dominant; Credit stress impairs financing/capex; Curve steepening is a moderate pro-cyclical signal.
- **XLV (-0.2, -0.2, -0.3, 0.3, -0.2):** defensive demand produces slightly negative Growth beta; higher Inflation is mildly adverse to cost structures/payer economics; lower Rates modestly help valuation; positive Credit-stress loading reflects defensive relative demand; flatter/inverted curves are modestly associated with defensive leadership.
- **XLY (0.8, -0.3, -0.5, -0.8, 0.3):** high Growth exposure reflects household discretionary demand; Inflation erodes real purchasing power; higher Rates pressure financed purchases and duration-sensitive valuations; Credit stress directly weakens household/company financing; a steeper Curve modestly signals better cyclical conditions.
- **XLP (-0.5, 0.2, -0.3, 0.5, -0.3):** defensive staples demand yields negative Growth sensitivity; modest Inflation loading reflects some pricing pass-through; lower Rates support bond-like valuations; positive Credit-stress exposure reflects defensive relative performance; flatter curves align modestly with defensive regimes.
- **XLU (-0.5, -0.5, -1.0, 0.5, -0.5):** defensive regulated demand yields negative Growth sensitivity; Inflation raises operating/capital costs subject to regulatory lag; -1.0 Rates captures long-duration and capital-intensive sensitivity; positive Credit-stress exposure reflects defensive demand; flatter curves modestly align with defensive leadership.
- **XLB (0.7, 0.7, 0.2, -0.5, 0.5):** strong Growth exposure reflects industrial/construction demand; strong positive Inflation reflects commodity/input-price leverage; Rates are a small nominal-growth proxy; Credit stress weighs on cyclical financing/demand; Curve steepening is a moderate pro-cyclical signal.
- **XLRE (-0.3, -0.3, -1.0, -0.5, -0.3):** property demand has mixed cyclicality but the sector is highly financing-sensitive; Inflation can pressure real financing costs/cap rates despite rent pass-through; -1.0 Rates reflects discount-rate and debt-cost sensitivity; Credit stress is adverse to refinancing and transactions; flatter curves modestly align with weaker credit creation.
- **XLC (0.3, -0.2, -0.5, -0.3, 0.1):** modest Growth reflects advertising/media/communications cyclicality; Inflation is mildly adverse to real demand and valuation; Rates matter through duration-sensitive platform valuations; Credit stress is modestly adverse; curve steepness receives only a small positive cyclical loading.

# 5. Ranking rule
For sector i: `Score_i = Σ_j Exposure_ij × Factor_j`. Rank descending; top 3 OW, bottom 3 UW, middle 5 Neutral. There is no discretionary override.

# 6. Metrics
Weekly hit rate is the share of eligible weeks in which equal-weight OW return exceeds equal-weight UW return; hidden until 8 weeks. Long-short cumulative return compounds weekly OW-minus-UW returns. Information Coefficient is the Spearman correlation between weekly sector scores and 5-trading-day forward sector returns; hidden until 12 weeks. Turnover is additions to OW divided by three plus additions to UW divided by three, averaged; hidden until 4 weeks.

# 7. Known limitations
No strategy backtest; loadings are first-principles rather than estimated; five factors omit sector-specific shocks and valuation dispersion; FRED releases have mixed frequency and revisions; public price interfaces can fail; early samples are small. This is a research model, not personalized investment advice.

# 8. Change log
|Version|Date|Change|Inception|
|---|---|---|---|
|1.0|2026-09-06|Initial frozen specification|Planned public call 2026-09-20 21:00 UTC pending human review|

Any change to factors, formulas, exposure matrix, or ranking rule requires a new major version and separate log.

# References
Federal Reserve Economic Data (FRED); Select Sector SPDRs; Spearman (1904) for rank correlation; Grinold & Kahn, *Active Portfolio Management*, for information-coefficient terminology.
