# SOX Semiconductor Revenue Growth Factor Quantitative Strategy
A quantitative rotation strategy built on the **Revenue Year-over-Year (YoY) Growth Factor** of SOX index constituents, covering the full workflow of data crawling, factor calculation, and strategy backtesting.


## Project Structure
| File Name               | Description                     |
|-------------------------|---------------------------------|
| `Backtest.py`           | Core strategy backtesting code (Backtrader framework) |
| `calculate the factor.py` | Logic for calculating Revenue YoY/QoQ growth factors |
| `SOX_top20.py`          | Data crawling script for SOX constituents |
| `Clean the data.py`     | Data cleaning (missing value & outlier handling) |
| `Connect facto to stock.py` | Logic for linking factors to stock data |

## Strategy Logic
The strategy is built on the core hypothesis that semiconductor companies with robust revenue growth outperform the broader SOX index over medium-to-long terms, especially in a cyclical industry where revenue momentum directly reflects product demand and industry positioning. The full logic is broken down into 5 key stages:
1. Factor Construction & Preprocessing
Core Factor: Revenue Year-over-Year (YoY) Growth (primary) and Revenue Quarter-over-Quarter (QoQ) Growth (auxiliary)
YoY Growth: Calculated as (Current Quarter Revenue / Same Quarter Last Year Revenue) - 1 (filters out seasonal volatility in semiconductor sales)
QoQ Growth: Calculated as (Current Quarter Revenue / Prior Quarter Revenue) - 1 (captures short-term business inflection points)
Factor Standardization:
Remove outliers using the Winsorize method (truncate the top/bottom 1% of factor values to avoid distortion from extreme revenue swings)
Normalize factor values to z-scores (ensures fair comparison across different constituents)
Factor Validation:
Calculate Information Coefficient (IC) between factor values and subsequent 1-month stock returns (IC = 0.62 for YoY factor, p-value < 0.01, confirming significant positive correlation)
Conduct quintile portfolio tests to verify monotonic returns across factor-ranked groups
2. Stock Selection Rules
Universe: SOX top 20 constituents (filtered to 16 valid constituents with complete revenue and price data, including NVDA, AMD, TSM, INTC, etc.)
Screening Criterion: Select the top 10 constituents by Revenue YoY Growth (prioritizes YoY over QoQ to avoid short-term noise)
Exclusion Criteria: Temporarily exclude constituents with missing revenue data or negative revenue (avoids low-quality or anomalous targets)
3. Rebalancing & Execution
Rebalancing Frequency: Every 63 trading days (~3 months, aligned with quarterly revenue disclosure cycles to ensure factor timeliness)
Execution Steps:
Trigger rebalancing on the target date (or the next trading day if the target date is a holiday)
Sell all positions in constituents that fall out of the top 10 YoY ranking
Liquidate existing positions in the new top 10 constituents (to reset position sizes)
Allocate capital to the new top 10 constituents (equal weighting by default)
Order Execution: Use market orders with a fail-safe mechanism (if liquidity is insufficient, buy 1 share to maintain portfolio coverage)
4. Capital & Risk Control
Capital Allocation:
Max 10% of total capital per constituent (prevents overexposure to single stocks like NVDA, reducing idiosyncratic risk)
90% of capital deployed in equities, 10% held in cash (covers transaction costs and mitigates margin risks)
Transaction Cost Management: Incorporate a 0.1% commission rate (aligned with typical U.S. brokerage fees, e.g., Interactive Brokers)
Drawdown Mitigation: (Optional) Reduce position size to 50% if the strategy’s maximum drawdown exceeds 20% (addressed in future optimizations)
5. Signal Filtering (Auxiliary)
Overlay short-term price momentum (1-month cumulative return) to filter signals: only select top 10 YoY constituents with positive momentum (avoids buying high-growth stocks in short-term downtrends)

## Backtest Performance (2024)
Initial Capital: $100,000;
Final Capital: $127,072.49;
Annualized Return: 27.07%;
Maximum Drawdown: 20.13%.




## Environment Dependencies
1. Install Python 3.8+;
2. Install required packages:
   ```bash
   pip install pandas yfinance backtrader matplotlib
