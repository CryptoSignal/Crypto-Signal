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

    def calculate_sma(self, period_count, historical_data):
        """
        Returns the Simple Moving Average for a coin pair
        """
        total_closing = sum(self.utils.get_closing_prices(historical_data))
        return total_closing / period_count

    def calculate_ema(self, period_count, historical_data):
        """
        Returns the Exponential Moving Average for a coin pair
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        previous_ema = self.calculate_sma(period_count, historical_data)
        period_constant = 2 / (1 + period_count)
        current_ema = (closing_prices[-1] * period_constant) \
                    + (previous_ema * (1 - period_constant))
        return current_ema
