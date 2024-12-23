from strategy import Strategy


# استراتژی پرایس اکشن (Price Action Strategy):
# این استراتژی با استفاده از الگوهای کندل استیک برای شناسایی نقاط ورود و خروج به معامله می‌پردازد.

class PriceActionStrategy(Strategy):
    def next(self):
        if not self.position:
            if self.data.close[0] > self.data.open[0] and self.data.close[-1] < self.data.open[-1]:
                self.buy()
        elif self.data.close[0] < self.data.open[0] and self.data.close[-1] > self.data.open[-1]:
            self.sell()
