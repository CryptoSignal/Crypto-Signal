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
            period_count (int, optional): Defaults to 21. The number of data points to consider for
                our bollinger bands.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        bollinger_data = abstract.BBANDS(dataframe, period_count)
        bollinger_data.dropna(how='all', inplace=True)

        return bollinger_data
