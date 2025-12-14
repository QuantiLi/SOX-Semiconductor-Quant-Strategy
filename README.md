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


## Environment Dependencies
1. Install Python 3.8+;
2. Install required packages:
   ```bash
   pip install pandas yfinance backtrader matplotlib
