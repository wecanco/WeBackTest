import numpy as np

from strategy import Strategy


class RSIMALongStrategy(Strategy):
    params = (
        ('ma_period', 500),  # Moving Average period
        ('rsi_period', 9),  # RSI period
        ('rsi_threshold', 50),  # RSI threshold for buy signals
        ('support_lookback', 20),  # How many bars to look back for support
        ('support_touches', 2),  # Minimum number of touches to confirm support
        ('price_threshold', 0.003)  # 0.3% threshold for price cluster
    )

    def __init__(self):
        # Core indicators
        self.sma = self._bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.ma_period)
        self.rsi = self._bt.indicators.RSI(
            self.data.close, period=self.params.rsi_period)

        # For position management
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit1 = 0
        self.take_profit2 = 0
        self.position_size = 0
        self.reduced_position = False

    def find_support_level(self):
        """
        Find the nearest support level by identifying price clusters
        Returns the strongest recent support level below current price
        """
        price_clusters = []

        # Get recent low prices
        recent_lows = [self.data.low[-i] for i in range(self.params.support_lookback) if i > 0]

        # Find price clusters
        for base_price in recent_lows:
            cluster = []
            # Check how many prices are within threshold of base_price
            for price in recent_lows:
                if abs(price - base_price) / base_price <= self.params.price_threshold:
                    cluster.append(price)

            if len(cluster) >= self.params.support_touches:  # Minimum touches to confirm support
                avg_price = sum(cluster) / len(cluster)
                if avg_price not in [c[0] for c in price_clusters]:  # Avoid duplicate clusters
                    price_clusters.append((avg_price, len(cluster)))

        # Sort clusters by price (descending) to find nearest support below current price
        price_clusters.sort(reverse=True)
        current_price = self.data.close[0]

        # Find nearest support level below current price
        for support_price, touches in price_clusters:
            if support_price < current_price:
                return support_price

        # If no support found, use recent low as fallback
        return min(recent_lows)

    def next(self):
        # Entry Logic - Only for Long positions
        if not self.position:
            # Buy Conditions: Price above MA500 and RSI below 50
            if self.data.close[0] > self.sma[0] and self.rsi[0] >= self.params.rsi_threshold:
                self.entry_price = self.data.close[0]

                # Find nearest support level for stop loss
                self.stop_loss = self.find_support_level()
                risk = self.entry_price - self.stop_loss

                # Set take profit levels
                self.take_profit1 = self.entry_price + risk  # 1:1 RR
                self.take_profit2 = self.entry_price + (2 * risk)  # 1:2 RR

                # Calculate position size (2% risk)
                self.position_size = self.broker.getcash() * 0.02 / risk
                self.buy(size=self.position_size)
                self.reduced_position = False

        # Position Management
        elif self.position.size > 0:  # We have a long position
            # Stop Loss
            if self.data.low[0] <= self.stop_loss:
                self.close()

            # Take Profit 1 - Move to risk free and reduce position
            elif not self.reduced_position and self.data.high[0] >= self.take_profit1:
                self.sell(size=self.position_size / 2)  # Close half position
                self.stop_loss = self.entry_price  # Move stop to entry
                self.reduced_position = True

            # Take Profit 2
            elif self.data.high[0] >= self.take_profit2:
                self.close()  # Close remaining position