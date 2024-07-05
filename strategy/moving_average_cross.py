import backtrader as bt


# تعریف استراتژی با اضافه کردن نقاط خرید و فروش
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
        # size = self.broker.get_cash() / self.data.close[0]
        if self.crossover > 0:
            if not self.position:
                self.buy()
        elif self.crossover < 0:
            if self.position:
                self.sell()
