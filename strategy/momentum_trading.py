from strategy import Strategy


# استراتژی مومنتوم تریدینگ (Momentum Trading Strategy):
# این استراتژی از اندیکاتور مکدی (MACD) برای شناسایی تغییرات مومنتوم در بازار استفاده می‌کند.
class MomentumTradingStrategy(Strategy):
    def __init__(self):
        self.macd = self._bt.indicators.MACD(self.data.close)

    def next(self):
        if not self.position:
            if self.macd.macd > self.macd.signal:
                self.buy()
        elif self.macd.macd < self.macd.signal:
            self.sell()
