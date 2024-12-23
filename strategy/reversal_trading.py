from strategy import Strategy


# استراتژی معاملات معکوس (Reversal Trading Strategy):
# در این استراتژی، از باندهای بولینگر برای شناسایی نقاط بازگشت قیمت استفاده می‌شود.
class ReversalTradingStrategy(Strategy):
    def __init__(self):
        self.bollinger = self._bt.indicators.BollingerBands(self.data.close)

    def next(self):
        if not self.position:
            if self.data.close[0] < self.bollinger.lines.bot:
                self.buy()
        elif self.data.close[0] > self.bollinger.lines.top:
            self.sell()
