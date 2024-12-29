import backtrader as bt
import collections


class TradePositionObserver(bt.Observer):
    lines = ('long_entry', 'long_exit', 'short_entry', 'short_exit',)
    plotinfo = dict(plot=True, subplot=False)

    plotlines = dict(
        long_entry=dict(marker='^', markersize=8.0, color='lime', fillstyle='full'),
        long_exit=dict(marker='v', markersize=8.0, color='red', fillstyle='full'),
        short_entry=dict(marker='v', markersize=8.0, color='red', fillstyle='full'),
        short_exit=dict(marker='^', markersize=8.0, color='lime', fillstyle='full')
    )

    def __init__(self):
        super(TradePositionObserver, self).__init__()
        self.trades = []
        self.trade_history = []

    def next(self):
        # تنظیم مقادیر پیش‌فرض
        self.lines.long_entry[0] = float('nan')
        self.lines.long_exit[0] = float('nan')
        self.lines.short_entry[0] = float('nan')
        self.lines.short_exit[0] = float('nan')

        # بررسی پوزیشن فعلی
        position = self._owner.position
        if position:
            trade = position.size
            if trade > 0:  # Long position
                if len(self.trades) == 0 or self.trades[-1] <= 0:
                    self.lines.long_entry[0] = self.data.close[0]
                    self.trades.append(trade)
            elif trade < 0:  # Short position
                if len(self.trades) == 0 or self.trades[-1] >= 0:
                    self.lines.short_entry[0] = self.data.close[0]
                    self.trades.append(trade)
        else:
            if len(self.trades) > 0:
                last_trade = self.trades[-1]
                if last_trade > 0:  # Long position closed
                    self.lines.long_exit[0] = self.data.close[0]
                elif last_trade < 0:  # Short position closed
                    self.lines.short_exit[0] = self.data.close[0]
                self.trades = []


class TradePnLObserver(bt.Observer):
    lines = ('pnl',)
    plotinfo = dict(plot=True, subplot=True)

    plotlines = dict(
        pnl=dict(marker='o', markersize=6.0, color='blue', fillstyle='full')
    )

    def next(self):
        self.lines.pnl[0] = float('nan')
        if self._owner.position.size == 0:  # اگر پوزیشن بسته شد
            if hasattr(self._owner, '_trade_history'):
                trades = self._owner._trade_history
                if trades:
                    last_trade = trades[-1]
                    if hasattr(last_trade, 'pnl'):
                        self.lines.pnl[0] = last_trade.pnl


class PositionBoxObserver(bt.Observer):
    lines = ('long_box', 'short_box',)
    plotinfo = dict(plot=True, subplot=False)

    plotlines = dict(
        long_box=dict(
            _plotskip=False,
            ls='-',  # خط پیوسته
            color='#90EE9080',  # سبز نیمه شفاف
            fillstyle='full'
        ),
        short_box=dict(
            _plotskip=False,
            ls='-',  # خط پیوسته
            color='#FF634780',  # قرمز نیمه شفاف
            fillstyle='full'
        ),
    )

    def __init__(self):
        super(PositionBoxObserver, self).__init__()
        self.trades = collections.defaultdict(list)
        self.current_trade = None
        self.entry_price = None
        self.position_type = None

    def next(self):
        # مقادیر پیش‌فرض برای خطوط
        self.lines.long_box[0] = float('nan')
        self.lines.short_box[0] = float('nan')

        position = self._owner.position
        close_price = self.data.close[0]

        # بررسی پوزیشن جدید
        if position.size != 0 and self.current_trade is None:
            self.current_trade = position.size
            self.entry_price = position.price
            self.position_type = 'long' if position.size > 0 else 'short'

        # آپدیت پوزیشن فعلی
        if self.current_trade is not None:
            if position.size == 0:  # پوزیشن بسته شده
                self.current_trade = None
                self.entry_price = None
                self.position_type = None
            else:  # پوزیشن هنوز باز است
                if self.position_type == 'long':
                    self.lines.long_box[0] = close_price
                else:
                    self.lines.short_box[0] = close_price
