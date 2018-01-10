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

    def get_kijunsen(self, historical_data):
        """
        Calculates (26 period high + 26 period low) / 2
        Also known as the "Kijun-sen" line
        """

        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)

        return (period_high + period_low) / 2

    def get_tenkansen(self, historical_data):
        """
        Calculates (9 period high + 9 period low) / 2
        Also known as the "Tenkan-sen" line
        """

        closing_prices = self.utils.get_closing_prices(historical_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)

        return (period_high + period_low) / 2

    def get_senkou_span_a(self, kijunsen_data, tenkansen_data):
        """
        Calculates (Conversion Line + Base Line) / 2
        Also known as the "Senkou Span A" line
        """

        kijunsen_line = self.get_kijunsen(kijunsen_data)
        tenkansen_line = self.get_tenkansen(tenkansen_data)

        return (kijunsen_line + tenkansen_line) / 2

    def get_senkou_span_b(self, senkou_span_b_data):
        """
        Calculates (52 period high + 52 period low) / 2
        Also known as the "Senkou Span B" line
        """
        
        closing_prices = self.utils.get_closing_prices(senkou_span_b_data)
        period_high = max(closing_prices)
        period_low = min(closing_prices)

        return (period_high + period_low) / 2
