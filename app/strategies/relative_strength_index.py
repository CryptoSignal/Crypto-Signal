"""
Runs the RSI strategy over the market data
"""

import structlog
from strategies.strategy_utils import Utils

class RelativeStrengthIndex():
    """
    Runs the RSI strategy over the market data
    """
    def __init__(self):
        self.logger = structlog.get_logger()
        self.utils = Utils()

    # Improvemnts to calculate_rsi are courtesy of community contributor "pcartwright81"
    def get_rsi_value(self, historical_data, period_count):
        """
        Calculates the Relative Strength Index for a coin_pair

        RSI = 100 - ( 100 / ( 1 + RS ) )

        RS = Average Gains / Average Losses

        Average Gains
            1st avg gain = sum of gains over past n period_count / n
            Everything after = (Prev Avg Gain * (n-1) + current gain) / n

        Average Loss
            1st avg loss = sum of losses over past n period / n
            Everything after = (Prev Avg Gain * (n-1) + current loss) / n

        Args:
            historical_data: Data used to find price changes used for RSI calc.
            period_count: period_count used tocalculate avg gains & avg losses.

        Returns:
            The RSI of market.
        """

        closing_prices = self.utils.get_closing_prices(historical_data)

        if period_count > len(closing_prices):
            period_count = len(closing_prices) 

        advances = []
        declines = []

        # Sort initial price changes from [first, period)
        # IE Orders [1, 14) [1, 13]
        for order_index in range(1, period_count):
            # subtract new from old
            change = closing_prices[order_index] - closing_prices[order_index - 1]

            # sort
            advances.append(change) if change > 0 else declines.append(abs(change))
    
        avg_gain = sum(advances) / period_count
        avg_loss = sum(declines) / period_count

        # Process orders period_count to end.
        # IE [14, length) [14, length-1]
        for order_index in range(period_count, len(closing_prices)):
            change = closing_prices[order_index] - closing_prices[order_index - 1]

            # sort
            gain = change if change > 0 else 0
            loss = abs(change) if change < 0 else 0

            # Smooth RSI
            avg_gain = (avg_gain * (period_count - 1) + gain) / period_count
            avg_loss = (avg_loss * (period_count - 1) + loss) / period_count

        if avg_loss > 0:
            rs = avg_gain / avg_loss
        else:
            # No losses, prevents ZeroDivision Exception
            rs = 100

        rsi = 100 - (100 / (1 + rs))
        return rsi

    def is_overbought(self, rsi_value, overbought_threshold):
        if overbought_threshold:
            if rsi_value >= overbought_threshold:
                return True
        return False

    def is_oversold(self, rsi_value, oversold_threshold):
        if oversold_threshold:
            if rsi_value <= oversold_threshold:
                return True
        return False
