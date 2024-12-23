from strategy import Strategy


# استراتژی محدوده نوسان (Range Trading Strategy):
# در این استراتژی، از سطوح حمایت و مقاومت برای شناسایی نقاط خرید و فروش استفاده می‌شود.
class RangeTradingStrategy(Strategy):
    params = (
        ('support', 100),
        ('resistance', 200),
    )

    def next(self):
        if not self.position:
            if self.data.close[0] < self.params.support:
                self.buy()
        elif self.data.close[0] > self.params.resistance:
            self.sell()
