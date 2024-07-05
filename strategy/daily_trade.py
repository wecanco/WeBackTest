import backtrader as bt
import random


class DailyTradeStrategy(bt.Strategy):
    params = (
        ('trades_per_day', 10),
        ('target_profit', 0.001),  # 0.1%
        ('fee', 0.001),  # 0.1% fee
    )

    def __init__(self):
        self.order = None
        self.buy_price = None
        self.trade_count = 0
        self.last_trade_time = None

    def next(self):
        current_time = self.data.datetime.datetime(0)

        # Check if we are in the market
        if not self.position:
            # If we're not in a trade and it's a new day, reset trade count
            if current_time.date() != self.data.datetime.datetime(-1).date():
                self.trade_count = 0

            # Check if we can make a new trade
            if self.trade_count < self.params.trades_per_day:
                # Random wait between 0 to 60 minutes
                if self.last_trade_time is None or \
                        (current_time.timestamp() - self.last_trade_time.timestamp()) > random.randint(0, 3600):
                    self.buy()
        else:
            # If we are in the market, check if we've reached our target
            if self.data.close[0] >= self.buy_price * (1 + self.params.target_profit + self.params.fee):
                self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                self.last_trade_time = bt.num2date(order.executed.dt)
            elif order.issell():
                self.trade_count += 1

        self.order = None

    # def stop(self):
    #     print('(Trades: %d) (Final Portfolio Value: %.2f)' %
    #           (self.trade_count, self.broker.getvalue()))
