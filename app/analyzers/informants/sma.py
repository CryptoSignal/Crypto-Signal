""" SMA Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class SMA(IndicatorUtils):
    def analyze(self, historical_data, period_count=15):
        """Performs a SMA analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our simple moving average.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        sma_values = abstract.SMA(dataframe, period_count).to_frame()
        sma_values.dropna(how='all', inplace=True)
        sma_values.rename(columns={0: 'sma'}, inplace=True)

        return sma_values
