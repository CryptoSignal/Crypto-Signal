"""
Calculates the Moving Averages for a coin pair
"""

import structlog
from strategies.strategy_utils import Utils

class MovingAverages():
    """
    Calculates the Moving Averages for a coin pair
    """
    def __init__(self):
        self.logger = structlog.get_logger()
        self.utils = Utils()


    def get_sma_value(self, period_count, historical_data):
        """
        Returns the Simple Moving Average for a coin pair
        """
        total_closing = sum(self.utils.get_closing_prices(historical_data))

        return total_closing / period_count


    def get_ema_value(self, period_count, historical_data):
        """
        Returns the Exponential Moving Average for a coin pair
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        previous_ema = self.get_sma_value(period_count, historical_data)
        period_constant = 2 / (1 + period_count)
        current_ema = (closing_prices[-1] * period_constant) \
                    + (previous_ema * (1 - period_constant))

        return current_ema


    def is_sma_trending(self, sma_value, sma_threshold):
        return bool(sma_threshold and sma_value >= sma_threshold)


    def is_ema_trending(self, ema_value, ema_threshold):
        return bool(ema_threshold and ema_value >= ema_threshold)
