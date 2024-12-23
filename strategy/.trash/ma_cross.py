from strategy import Strategy


class MaCrossStrategy(Strategy):

    def __init__(self):
        ma_fast = self._bt.ind.EMA(period=50, plotname="EMA50")
        ma_slow = self._bt.ind.EMA(period=200, plotname="EMA200")

        self.crossover = self._bt.ind.CrossOver(ma_fast, ma_slow)

    def next(self):
        grows = 0
        if self.position:
            grows = (1 - (self.position.price / self.data.close)) * 100

        if self.crossover > 0 or grows <= -20:
            self.buy()
        else:
            if (self.crossover < 0 and self.position.price < self.data.close) or grows >= 10:
                self.close()
