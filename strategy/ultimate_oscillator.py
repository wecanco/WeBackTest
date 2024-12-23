from strategy import Strategy

# استراتژی سیگنال نهایی (Ultimate Oscillator Strategy):
# این استراتژی از اسیلاتور نهایی برای شناسایی شرایط خرید و فروش بیش از حد استفاده می‌کند.
# pip install TA-Lib

class UltimateOscillatorStrategy(Strategy):
    params = (
        ('uo_period1', 7),
        ('uo_period2', 14),
        ('uo_period3', 28),
        ('uo_overbought', 70),
        ('uo_oversold', 30),
    )

    def __init__(self):
        # تعریف اندیکاتور Ultimate Oscillator
        self.uo = self._bt.talib.ULTOSC(
            self.data.high,
            self.data.low,
            self.data.close,
            timeperiod1=self.params.uo_period1,
            timeperiod2=self.params.uo_period2,
            timeperiod3=self.params.uo_period3,
        )

    def next(self):
        # ورود به معامله در حالت اشباع فروش
        if not self.position and self.uo < self.params.uo_oversold:
            self.buy()
        # خروج از معامله در حالت اشباع خرید
        elif self.position and self.uo > self.params.uo_overbought:
            self.sell()
