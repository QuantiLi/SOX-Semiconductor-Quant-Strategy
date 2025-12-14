import backtrader as bt
import pandas as pd
import yfinance as yf
import warnings
import matplotlib.pyplot as plt
import numpy as np

warnings.filterwarnings('ignore')



class SafePandasData(bt.feeds.PandasData):

    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
    )

    def start(self):
        if not isinstance(self.p.dataname, pd.DataFrame):
            self.p.dataname = pd.DataFrame()
        else:

            self.p.dataname = self.p.dataname.astype(float)

            self.p.dataname.index = pd.DatetimeIndex(self.p.dataname.index).tz_localize(None)
        super().start()



class GrowthTop10Strategy(bt.Strategy):
    params = (
        ('rebalance_freq', 63),
        ('factor_path', 'SOX_top20_final_factor.csv'),
        ('commission_rate', 0.001),
        ('cash_ratio', 0.90),
        ('max_single_stock_ratio', 0.1),
    )

    def __init__(self):
        self.count = 0

        self.factor_data = pd.read_csv(self.params.factor_path)
        self.factor_data['Symbol'] = self.factor_data['Symbol'].astype(str).str.upper()
        # Sort first 10 stocks（Revenue_YoY）
        self.top10_stocks = self.factor_data.sort_values(
            'Revenue_YoY', ascending=False
        ).head(10)['Symbol'].tolist()

        self.symbol_data_map = {data._name.upper(): data for data in self.datas}
        # Filter no-data stocks
        self.top10_stocks = [s for s in self.top10_stocks if s in self.symbol_data_map]
        print(f" Initial 10 stocks：{self.top10_stocks}")

        self.first_trade_done = False
        self.nav_history = []
        self.date_history = []

    def update_top10_stocks(self):
        new_top10 = self.factor_data.sort_values('Revenue_YoY', ascending=False).head(10)['Symbol'].tolist()
        self.top10_stocks = [s for s in new_top10 if s in self.symbol_data_map]
        return self.top10_stocks

    def get_safe_price(self, data):

        # way1：
        current_close = data.lines.close[0]
        if not np.isnan(current_close) and current_close > 0:
            return current_close
        # way2:
        if hasattr(data, 'df') and not data.df.empty:
            valid_closes = data.df['Close'].dropna()
            if not valid_closes.empty:
                return valid_closes.iloc[-1]
        # Extremly situation
        return data.df['Close'].min() if (hasattr(data, 'df') and not data.df.empty) else 1.0

    def execute_trade(self):

        current_date = self.datas[0].datetime.date(0) if len(self.datas[0]) > 0 else "Initial day"
        print(f"\n Rebalancing day：{current_date}，choosing stocks：{self.top10_stocks}")

        # 1. Sell non-top 10 targets
        for data in self.datas:
            data_name = data._name.upper()
            pos_size = self.getposition(data).size
            if pos_size > 0 and data_name not in self.top10_stocks:
                self.sell(data=data, size=pos_size)
                print(f" Submit a sell order：{data_name}(Non-holding target), quantity：{pos_size}")

        # 2. Calculate the total funds available for trading
        total_cash = self.broker.getcash()
        total_pos_value = self.broker.get_value() - total_cash
        total_available = total_cash * self.params.cash_ratio
        max_single_stock_cash = total_available * self.params.max_single_stock_ratio
        print(
            f" Total Cash：{total_cash:.2f}，Markrt value：{total_pos_value:.2f}，available cash：{total_available:.2f}，Aavailable for single target：{max_single_stock_cash:.2f}")

        # 3. First, flatten the existing positions of the top 10 targets (sell all positions and then buy again to avoid position overlap)
        for symbol in self.top10_stocks:
            data = self.symbol_data_map[symbol]
            current_pos = self.getposition(data).size
            if current_pos > 0:
                self.sell(data=data, size=current_pos)
                print(f" Submit a sell order：{symbol}Original positions, quantity：{current_pos}")


        used_cash = 0
        for symbol in self.top10_stocks:
            data = self.symbol_data_map[symbol]

            close_price = self.get_safe_price(data)

            available_cash = min(max_single_stock_cash, total_available - used_cash)
            if available_cash <= 0:
                print(f" {symbol}：No available cash")
                continue
            # Calculate the number of shares that can be bought (considering commission)
            max_size = int(available_cash / (close_price * (1 + self.params.commission_rate)))
            if max_size <= 0:
                max_size = 1  #Minimum purchase of 1 share (only when funds are extremely limited)
                print(f"⚠️ {symbol}：Minimum purchase of 1 share (only when funds are extremely limited)")

            if max_size > 0:
                self.buy(data=data, size=max_size)

                actual_cost = max_size * close_price * (1 + self.params.commission_rate)
                used_cash += actual_cost
                print(
                    f" Submit a buy order：{symbol}，Price：{close_price:.2f}，quantity：{max_size}，Estimated cost：{actual_cost:.2f}，Accumulated used funds：{used_cash:.2f}")

    def next(self):

        current_value = self.broker.getvalue()
        current_value = current_value if not np.isnan(current_value) else (
            self.nav_history[-1] if self.nav_history else self.broker.getcash())
        self.nav_history.append(current_value)
        self.date_history.append(bt.num2date(self.datas[0].datetime[0]))

        # The first transaction is executed immediately
        if not self.first_trade_done:
            self.execute_trade()
            self.first_trade_done = True
        # Rebalance the portfolio every 63 days
        elif self.count % self.params.rebalance_freq == 0 and self.count > 0:
            self.update_top10_stocks()
            self.execute_trade()
        self.count += 1

    def notify_order(self, order):

        if order.status in [order.Submitted, order.Accepted]:
            return
        data_name = order.data._name.upper() if order.data else "未知"
        if order.status == order.Completed:
            if order.isbuy():
                cost = order.executed.size * order.executed.price
                commission = order.executed.comm
                print(
                    f" Purchase completed：{data_name}，quantity：{order.executed.size}，price：{order.executed.price:.2f}，commission：{commission:.2f}")
            else:
                proceeds = order.executed.size * order.executed.price
                commission = order.executed.comm
                print(
                    f" Sell completed：{data_name}，quantity：{order.executed.size}，price：{order.executed.price:.2f}，commission：{commission:.2f}")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print(f"Failed：{data_name}，status：{order.getstatusname()}")
            # Downgrade handling: Try to buy 1 share (minimum position to avoid being completely unable to trade)
            data = order.data
            if order.isbuy() and self.getposition(data).size == 0:
                self.buy(data=data, size=1)
                print(f" Degrade and retry：{data_name} Buy 1")

    def notify_trade(self, trade):

        if trade.isclosed:
            data_name = trade.data._name.upper()
            print(f"Trading profit and loss：{data_name}，Total profit and loss：{trade.pnl:.2f}，Net profit and loss：{trade.pnlcomm:.2f}")


#  Download Data
def safe_yf_download(symbol, start, end):
    try:

        data = yf.download(
            symbol,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
            timeout=10,
            threads=False
        )
        if data.empty:
            return pd.DataFrame()


        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
            data = data.loc[:, ~data.columns.duplicated()]

        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in required_cols if col in data.columns]
        data = data[available_cols]
        for col in required_cols:
            if col not in data.columns:
                data[col] = 0.0

        # Remove the time zone and force the index to be a timezone-naive DatetimeIndex
        data.index = pd.DatetimeIndex(data.index).tz_localize(None)

        data = data.astype(float)
        # Print data preview (confirm that columns and prices are correct)
        print(f" {symbol} Data preview：\n{data.head(1)}")
        return data
    except Exception as e:
        print(f" Download{symbol}Faild：{str(e)}")
        return pd.DataFrame()


#           Run
if __name__ == '__main__':

    factor_path = 'SOX_top20_final_factor.csv'
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    initial_cash = 100000.0


    try:
        factor_data = pd.read_csv(factor_path)
        factor_data['Symbol'] = factor_data['Symbol'].astype(str).str.upper()
        stock_list = factor_data['Symbol'].dropna().unique().tolist()
        print(f" Read from the factor file{len(stock_list)}stocks：{stock_list}")
    except Exception as e:
        print(f"Read faild：{e}")
        exit()


    cerebro = bt.Cerebro()
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=0.001)


    valid_stocks = []
    for symbol in stock_list:
        symbol_upper = symbol.upper()
        data = safe_yf_download(symbol_upper, start_date, end_date)
        if not data.empty and len(data) > 0:
            bt_data = SafePandasData(
                dataname=data,
                name=symbol_upper,
                datetime=None
            )
            cerebro.adddata(bt_data)
            valid_stocks.append(symbol_upper)
            print(f"Load{symbol_upper}data（{len(data)}）")
        else:
            print(f" skip{symbol_upper}The data is empty or invalid")

    if not valid_stocks:
        print("No valid underlying assets, exit backtesting")
        exit()

    # Run backtest
    print(f"\nInitial funds：{initial_cash:.2f}")
    cerebro.addstrategy(GrowthTop10Strategy)
    results = cerebro.run()


    final_value = cerebro.broker.getvalue()
    final_value = np.nan_to_num(final_value, nan=initial_cash)
    total_return = (final_value - initial_cash) / initial_cash * 100
    print(f"\nBacktest results：")
    print(f"Initial funds：{initial_cash:.2f}")
    print(f"Fianl funds：{final_value:.2f}")
    print(f"Total Return：{total_return:.2f}%")

    # Draw Curve
    try:
        strat = results[0]
        if len(strat.nav_history) > 0 and len(strat.date_history) > 0:

            nav_history = np.nan_to_num(strat.nav_history, nan=initial_cash)
            plt.figure(figsize=(12, 6))
            plt.plot(strat.date_history, nav_history, label='Strategy Net Value', color='blue')
            plt.axhline(y=initial_cash, color='red', linestyle='--', label='Initial Capital')
            plt.title('Strategy Net Value Curve (2024)')
            plt.xlabel('Date')
            plt.ylabel('Value ($)')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            print(f"\n Wrong：No data")
    except Exception as e:
        print(f"\n Wrong：{e}")