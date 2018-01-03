"""
Runs the ichimoku strategy over the market data
"""

import structlog
from strategies.strategy_utils import Utils

class IchimokuCloud():
    """
    Runs the ichimoku strategy over the market data
    """
    def __init__(self):
        self.logger = structlog.get_logger()
        self.utils = Utils()

    def get_base_line(self, historical_data):
        """
        Calculates (26 period high + 26 period low) / 2
        Also known as the "Kijun-sen" line
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)
        return (period_high + period_low) / 2

    def get_conversion_line(self, historical_data):
        """
        Calculates (9 period high + 9 period low) / 2
        Also known as the "Tenkan-sen" line
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)
        return (period_high + period_low) / 2

    def get_leading_span_a(self, base_line_data, conversion_line_data):
        """
        Calculates (Conversion Line + Base Line) / 2
        Also known as the "Senkou Span A" line
        """
        base_line = self.get_base_line(base_line_data)
        conversion_line = self.get_conversion_line(conversion_line_data)
        return (base_line + conversion_line) / 2

    def get_leading_span_b(self, historical_data):
        """
        Calculates (52 period high + 52 period low) / 2
        Also known as the "Senkou Span B" line
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)
        return (period_high + period_low) / 2

    def is_ichimoku_trending(self, ichimoku_threshold):
        return False
