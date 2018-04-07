""" VWAP Indicator
"""

import math

import numpy as np
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class VWAP(IndicatorUtils):
    def analyze(self, historical_data, period_count=15):
        """Performs a VWAP analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our simple moving average.

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


