import pathlib
import re
import sys

import backtrader as bt
import os.path
import yfinance as yf
import pandas as pd
from datetime import date, timedelta, datetime
from importlib import util, import_module
import logging


# تعریف تحلیلگر سفارشی برای محاسبه وین ریت
class WinRateAnalyzer(bt.Analyzer):
    def __init__(self):
        self.wins = 0
        self.losses = 0
        self.pnls = list()
        self.durations = list()

    def notify_trade(self, trade):
        if trade.isclosed:
            self.pnls.append(trade.pnl)
            self.durations.append(trade.barlen)
            if trade.pnl > 0:
                self.wins += 1
            elif trade.pnl < 0:
                self.losses += 1

    def get_analysis(self):
        total_trades = self.wins + self.losses
        win_rate = (self.wins / total_trades) * 100 if total_trades > 0 else 0
        return {'win_rate': win_rate, 'wins': self.wins, 'losses': self.losses, 'pnls': self.pnls,
                'durations': self.durations}


def get_strategies_from_files():
    _all_strategies = {}
    directory = pathlib.Path(__file__).parent.resolve().__str__() + '/strategy/'
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding="utf8") as f:
                    content = f.read()
                    class_name = re.findall(r"class\s*([^:]*)\s*\(Strategy", content)
                    if len(class_name) > 0:
                        _all_strategies[class_name[0]] = file_path
    return _all_strategies


if __name__ == '__main__':
    all_strategies = get_strategies_from_files()
    # دریافت ورودی‌ها
    symbol = input("Enter Currency [like BTC]: ")
    timeframe = input("Enter Timeframe [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]: ")
    start_date = input("Enter Start Date [like 2023-01-01]: ")
    end_date = input("Enter End Date [like 2024-01-01]: ")
    balance = input("Account Balance ($): ")
    margin_percent = input("Percent of Asset Per Order(%): ")
    commission = input("Broker Commission (%): ")
    __all_strategies_s = "\n\t".join(all_strategies.keys())
    strategy = input(f"Select Strategy [\n\t{__all_strategies_s}\n]: ")
    print("\n\t ====> ")

    if not strategy:
        strategy = 'MaCrossStrategy'

    # Load Strategy Class
    if strategy not in all_strategies:
        print("Strategy not found! add your strategy to `strategy` folder.")
        exit()

    file_path = all_strategies[strategy]
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = util.spec_from_file_location(file_name, file_path)
    module_name = util.module_from_spec(spec)
    sys.modules[file_name] = module_name
    spec.loader.exec_module(module_name)
    strategyClass = getattr(module_name, strategy)

    if not balance:
        balance = 1000
    balance = int(balance)

    if not commission:
        commission = 0.001
    commission = float(commission)

    if not margin_percent:
        margin_percent = 5
    margin_percent = float(margin_percent)

    if not symbol:
        symbol = 'BTC'
    symbol = symbol.upper()

    if not timeframe:
        timeframe = '1h'

    if not end_date:
        end_date = date.today() - timedelta(days=1)
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    if not start_date:
        start_date = end_date - timedelta(
            days=365 * 10 if ('d' in timeframe or 'w' in timeframe or 'mo' in timeframe) else 120)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    print_data = f"Currency: {symbol} | Start Date: {start_date.strftime('%Y-%m-%d')} | " \
                 f"End Date: {end_date.strftime('%Y-%m-%d')} | Balance: ${balance} | margin percent: {margin_percent}"

    # logging.info(print_data)
    print(print_data)

    # دانلود داده‌ها
    file_name = f"./data/{symbol}-USD_{timeframe}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
    if os.path.isfile(file_name):
        data = pd.read_csv(file_name, index_col='Datetime', parse_dates=True)
    else:
        data = yf.download(f"{symbol}-USD", start=start_date, end=end_date, interval=timeframe)
        if not data.empty:
            data.to_csv(file_name, index_label="Datetime")

    if data.empty:
        print("\t no data found!")
        exit()

    # تبدیل داده‌ها به فرمت مناسب برای backtrader
    data_feed = bt.feeds.PandasData(dataname=data)

    # ایجاد نمونه از Cerebro
    cerebro = bt.Cerebro()

    # اضافه کردن داده‌ها و استراتژی
    cerebro.adddata(data_feed)
    cerebro.addstrategy(strategyClass)

    cerebro.addsizer(bt.sizers.PercentSizer, percents=margin_percent)

    # تنظیم سرمایه اولیه و کمیسیون
    cerebro.broker.setcash(balance)
    cerebro.broker.setcommission(commission=commission)

    # اضافه کردن آنالیزورها
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(WinRateAnalyzer, _name='win_rate')

    # اجرای بک تست
    results = cerebro.run()

    # چاپ نتایج
    strategy = results[0]
    win_rate_analysis = strategy.analyzers.win_rate.get_analysis()
    print("\t => ")
    total_pnls = sum(win_rate_analysis['pnls'])
    total_duration = sum(win_rate_analysis['durations'])
    grows_percent = (float((balance + total_pnls) / balance) - 1.00) * 100
    print(f"Initial Balance: ${balance:.2f}")
    print(f"Final Portfolio Value: ${cerebro.broker.getvalue():.2f}")
    # print(f"Sharpe Ratio: {strategy.analyzers.sharpe_ratio.get_analysis()['sharperatio']:.2f}")
    print(f"Max Drawdown: {strategy.analyzers.drawdown.get_analysis()['max']['drawdown']:.2f}%")
    # print(f"Total Return: {strategy.analyzers.returns.get_analysis()['rtot']:.2f}%")
    print(f"Win Rate: {win_rate_analysis['win_rate']:.2f}%")
    print(f"Wins: {win_rate_analysis['wins']}")
    print(f"Losses: {win_rate_analysis['losses']}")
    print(f"PNLs($): {win_rate_analysis['pnls']}")
    print(f"durations({timeframe}): {win_rate_analysis['durations']}")
    print(f"Total PNL($): {sum(win_rate_analysis['pnls'])}")
    print(f"Total Duration({timeframe}): {total_duration}")
    print(f"Final Balance: ${(balance + total_pnls):.2f}")
    print(f"Grows Percent: {grows_percent}")

    print("=====================")

    # نمایش نمودار
    cerebro.plot(style='candlestick', barup='green', bardown='red')
