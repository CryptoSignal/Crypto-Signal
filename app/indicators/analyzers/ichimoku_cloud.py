"""Runs the ichimoku strategy over the market data
"""

import structlog
from indicators.analyzers.utils import StrategyUtils


class IchimokuCloud(StrategyUtils):
    """Runs the ichimoku strategy over the market data
    """

    def __init__(self):
        """Initializes IchimokuCloud class
        """

        self.logger = structlog.get_logger()


    def get_kijunsen(self, historical_data):
        """Calculates (26 period high + 26 period low) / 2. Also known as the "Kijun-sen" line

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The Kijun-sen line value of ichimoku.
        """

        period_high = max(self.get_high_prices(historical_data))
        period_low = min(self.get_low_prices(historical_data))

        return (period_high + period_low) / 2


    def get_tenkansen(self, historical_data):
        """Calculates (9 period high + 9 period low) / 2. Also known as the "Tenkan-sen" line

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The Tenkan-sen line value of ichimoku.
        """

        period_high = max(self.get_high_prices(historical_data))
        period_low = min(self.get_low_prices(historical_data))

        return (period_high + period_low) / 2


    def get_senkou_span_a(self, kijunsen_data, tenkansen_data):
        """Calculates (Conversion Line + Base Line) / 2. Also known as the "Senkou Span A" line

        Args:
            kijunsen_data (float): The Kijun-sen line value of ichimoku.
            tenkansen_data (float): The Tenkan-sen line value of ichimoku.

        Returns:
            float: The Senkou span A value of ichimoku.
        """

        kijunsen_line = self.get_kijunsen(kijunsen_data)
        tenkansen_line = self.get_tenkansen(tenkansen_data)

        return (kijunsen_line + tenkansen_line) / 2


    def get_senkou_span_b(self, historical_data):
        """Calculates (52 period high + 52 period low) / 2. Also known as the "Senkou Span B" line

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The Senkou span B value of ichimoku.
        """

        period_high = max(self.get_high_prices(historical_data))
        period_low = min(self.get_low_prices(historical_data))

        return (period_high + period_low) / 2
