from strategy import Strategy


# استراتژی اسکالپینگ (Scalping Strategy):
# در این استراتژی، از میانگین متحرک ساده (SMA) با دوره‌های کوتاه‌مدت و بلندمدت برای شناسایی فرصت‌های معاملاتی استفاده می‌شود

class ScalpingStrategy(Strategy):
    params = (
        ('short_period', 5),
        ('long_period', 20),
    )

    def __init__(self):
        self.sma_short = self._bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        self.sma_long = self._bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)

    def next(self):
        if not self.position:
            if self.sma_short > self.sma_long:
                self.buy()
        elif self.sma_short < self.sma_long:
            self.sell()
