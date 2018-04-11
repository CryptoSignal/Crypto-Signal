""" Bollinger Bands Indicator
"""

import math

from talib import abstract

from analyzers.utils import IndicatorUtils


class Bollinger(IndicatorUtils):
    def analyze(self, historical_data, period_count=21):
        """Performs a bollinger band analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            all_data (bool, optional): Defaults to False. If True, we return the BB's associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        bollinger_data = abstract.BBANDS(dataframe, period_count)
        bollinger_data.dropna(how='all', inplace=True)

        return bollinger_data
