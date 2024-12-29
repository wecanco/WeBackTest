import datetime
from strategy import Strategy


class TestStrategy(Strategy):
    params = (
        ('period', 200),
    )

    def __init__(self):
        self.ema = self._bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.period)

    def next(self):
        pos = self.getposition()

        if pos.size == 0:
            diff = (1 - (self.ema[0] / self.data.close[0])) * 100
            if diff <= -5:
                self.buy()
            elif diff >= 5:
                self.sell()

        else:
            # pos.pnl
            current_price = self.data.close[0]
            position_size = abs(pos.size)
            entry_price = pos.price

            if pos.size > 0:  # is buy position
                unrealized_pnl = (current_price - entry_price) * position_size
                pnl_percentage = ((current_price / entry_price) - 1) * 100

                if pnl_percentage <= -5:
                    self.buy()
                elif pnl_percentage >= 2:
                    self.close()
            else:
                unrealized_pnl = (entry_price - current_price) * position_size
                pnl_percentage = ((entry_price / current_price) - 1) * 100

                if pnl_percentage <= -5:
                    self.sell()
                elif pnl_percentage >= 2:
                    self.close()
