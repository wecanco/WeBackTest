import backtrader as bt


class MaCrossStrategy(bt.Strategy):

    def __init__(self):
        ma_fast = bt.ind.SMA(period=50, plotname="SMA50")
        ma_slow = bt.ind.SMA(period=200, plotname="SMA200")

        self.crossover = bt.ind.CrossOver(ma_fast, ma_slow)

    def next(self):
        grows = 0
        if self.position:
            grows = (1 - (self.position.price / self.data.close)) * 100

        if self.crossover > 0 or grows <= -20:
            self.buy()
        else:
            if (self.crossover < 0 and self.position.price < self.data.close) or grows >= 10:
                self.close()
