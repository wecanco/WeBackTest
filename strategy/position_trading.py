from strategy import Strategy


# استراتژی پوزیشن تریدینگ (Position Trading Strategy):
# در این استراتژی، از تقاطع میانگین متحرک نمایی (EMA) با دوره‌های مختلف برای تعیین روند بلندمدت استفاده می‌شود.
class PositionTradingStrategy(Strategy):
    params = (
        ('ema_short_period', 50),
        ('ema_long_period', 200),
    )

    def __init__(self):
        self.ema_short = self._bt.indicators.ExponentialMovingAverage(self.data.close,
                                                                      period=self.params.ema_short_period)
        self.ema_long = self._bt.indicators.ExponentialMovingAverage(self.data.close,
                                                                     period=self.params.ema_long_period)

    def next(self):
        if not self.position:
            if self.ema_short > self.ema_long:
                self.buy()
        elif self.ema_short < self.ema_long:
            self.sell()
