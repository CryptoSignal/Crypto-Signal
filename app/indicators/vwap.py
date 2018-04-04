""" VWAP Indicator
"""

import math

import numpy as np
import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class VWAP(IndicatorUtils):
    def analyze(self, historical_data, period_count=15,
                    hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a VWAP analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our simple moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the VWAP associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        dataframe['vwap'] = np.cumsum(dataframe.volume*(dataframe.high+dataframe.low)/2) / np.cumsum(dataframe.volume)

        analyzed_data = [(r[1]['vwap'], 0) for r in dataframe.iterrows()]

        return self.analyze_results(
            analyzed_data,
            is_hot=lambda v, c: c > v * hot_thresh if hot_thresh else False,
            is_cold=lambda v, c: c < v * cold_thresh if cold_thresh else False,
            all_data=all_data
        )


