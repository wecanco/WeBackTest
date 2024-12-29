import backtrader as bt
import datetime
import pandas as pd


# تعریف استراتژی با اضافه کردن نقاط خرید و فروش برای ترید اسپات
class MovingAverageCrossStrategy(bt.Strategy):
    params = (
        ('fast', 50),
        ('slow', 200),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast, plotname="SMA50"
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow, plotname="SMA200"
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if self.crossover > 0 and not self.position:
            size = self.broker.get_cash() / self.data.close[0]
            if size > 0:
                self.buy(size=size)
                print(f'خرید در قیمت: {self.data.close[0]} - سرمایه باقی‌مانده: {self.broker.get_cash()} - ارزش کل: {self.broker.get_value()} - اندازه خرید: {size}')
        elif self.crossover < 0 and self.position:
            self.sell(size=self.position.size)
            print(f'فروش در قیمت: {self.data.close[0]} - سرمایه باقی‌مانده: {self.broker.get_cash()} - ارزش کل: {self.broker.get_value()} - اندازه فروش: {self.position.size}')


# ایجاد داده‌ها و اجرای بک‌تست
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MovingAverageCrossStrategy)


    # دانلود داده‌ها
    file_name = f"../data/BTC-USD_1d_2022-07-04_2024-07-03.csv"
    data = pd.read_csv(file_name, index_col='Datetime', parse_dates=True)

    # تبدیل داده‌ها به فرمت مناسب برای backtrader
    data_feed = bt.feeds.PandasData(dataname=data)

    cerebro.adddata(data_feed)
    cerebro.broker.set_cash(10000)
    cerebro.broker.setcommission(commission=0.001)
    initial_value = cerebro.broker.get_value()
    print(f'سرمایه اولیه: {initial_value}')

    cerebro.run()
    final_value = cerebro.broker.get_value()
    print(f'ارزش نهایی: {final_value}')
    cerebro.plot()
