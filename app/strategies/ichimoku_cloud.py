"""
Runs the ichimoku strategy over the market data
"""

from strategies.strategy_utils import Utils

class IchimokuCloud():
    """
    Runs the ichimoku strategy over the market data
    """
    def __init__(self):
        self.utils = Utils()

    def calculate_base_line(self, historical_data):
        """
        Calculates (26 period high + 26 period low) / 2
        Also known as the "Kijun-sen" line
        """

        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)
        return (period_high + period_low) / 2

    def calculate_conversion_line(self, historical_data):
        """
        Calculates (9 period high + 9 period low) / 2
        Also known as the "Tenkan-sen" line
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)
        return (period_high + period_low) / 2

    def calculate_leading_span_a(self, historical_data):
        """
        Calculates (Conversion Line + Base Line) / 2
        Also known as the "Senkou Span A" line
        """

        base_line = self.calculate_base_line(historical_data)
        conversion_line = self.calculate_conversion_line(historical_data)
        return (base_line + conversion_line) / 2

    def calculate_leading_span_b(self, historical_data):
        """
        Calculates (52 period high + 52 period low) / 2
        Also known as the "Senkou Span B" line
        """
        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)
        return (period_high + period_low) / 2
