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
Factor Selection: Use "Revenue YoY Growth" as the core stock-selection factor (IC = 0.62, validated as effective);
Stock Selection Rule: Select the top 10 SOX constituents by YoY growth;
Rebalancing Frequency: Every 63 trading days (~1 quarter);
Capital Allocation: Max 10% capital per ticker to diversify risk.

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
