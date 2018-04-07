""" Stochastic RSI Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class StochasticRSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a Stochastic RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our simple moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the Stochastic RSI
                associated with each data point in our historical dataset. Otherwise just return
                the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        rsi_period_count = period_count * 2
        rsi_values = abstract.RSI(dataframe, rsi_period_count)
        rsi_values.dropna(how='all', inplace=True)

        analyzed_data = list()
        for index in range(period_count, rsi_values.shape[0]):
            start_index = index - period_count
            last_index = index + 1
            rsi_min = rsi_values.iloc[start_index:last_index].min()
            rsi_max = rsi_values.iloc[start_index:last_index].max()
            stoch_rsi = (100 * ((rsi_values[index] - rsi_min) / (rsi_max - rsi_min)))
            analyzed_data.append((stoch_rsi,))

        return self.analyze_results(
            analyzed_data,
            is_hot=lambda v: v < hot_thresh if hot_thresh else False,
            is_cold=lambda v: v > cold_thresh if cold_thresh else False,
            all_data=all_data
        )
