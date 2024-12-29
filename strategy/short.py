import datetime
from strategy import Strategy


class ShortStrategy(Strategy):
    params = (
        ('period', 20),
    )

    def __init__(self):
        self.sma = self._bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)

    def next(self):
        if not self.position:  # اگر پوزیشنی نداریم
            if self.data.close[0] < self.sma[0]:
                self.sell()  # باز کردن پوزیشن شورت
        else:
            if self.data.close[0] > self.sma[0]:
                self.close()  # بستن پوزیشن شورت