""" RSI Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class RSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs an RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our simple moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the RSI associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        rsi_values = abstract.RSI(dataframe, period_count)

        analyzed_data = [(value,) for value in rsi_values]

        return self.analyze_results(
            analyzed_data,
            is_hot=lambda v: v < hot_thresh if hot_thresh else False,
            is_cold=lambda v: v > cold_thresh if cold_thresh else False,
            all_data=all_data
        )
