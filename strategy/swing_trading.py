from strategy import Strategy


# استراتژی سوئینگ تریدینگ (Swing Trading Strategy):
# این استراتژی از شاخص قدرت نسبی (RSI) برای شناسایی شرایط خرید و فروش بیش از حد استفاده می‌کند.
class SwingTradingStrategy(Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
    )

    def __init__(self):
        self.rsi = self._bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_oversold:
                self.buy()
        elif self.rsi > self.params.rsi_overbought:
            self.sell()
