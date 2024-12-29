import numpy as np

from strategy import Strategy


class BollingerBandsStrategy(Strategy):
    params = (
        ('period', 20),  # دوره محاسبه باند بولینجر
        ('devfactor', 2),  # ضریب انحراف معیار
        ('cooldown', 5),  # تعداد روزهای انتظار بین معاملات
    )

    def __init__(self):
        # محاسبه باندهای بولینجر
        self.boll = self._bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.period,
            devfactor=self.params.devfactor
        )

        # ذخیره خط‌های باند بولینجر
        self.mid_line = self.boll.mid
        self.top_line = self.boll.top
        self.bot_line = self.boll.bot

        # برای کنترل تعداد معاملات
        self.last_trade = 0  # شمارنده روزها از آخرین معامله

    def next(self):
        # افزایش شمارنده روزها
        self.last_trade += 1

        # اگر هنوز دوره کولداون تموم نشده، صبر می‌کنیم
        if self.last_trade < self.params.cooldown:
            return

        # شرط‌های معامله
        if not self.position:
            if self.data.close[0] <= self.bot_line[0]:
                self.buy()
                self.last_trade = 0  # ریست کردن شمارنده
        else:
            entry_price = self.position.price
            if self.data.close[0] >= self.mid_line[0] and self.data.close[0] > entry_price:
                self.sell()
                self.last_trade = 0  # ریست کردن شمارنده