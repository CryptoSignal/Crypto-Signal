""" MACD Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class MACD(IndicatorUtils):
    def analyze(self, historical_data, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the MACD associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        macd_values = abstract.MACD(dataframe).iloc[:, 0]

        analyzed_data = [(value,) for value in macd_values]

        return self.analyze_results(analyzed_data,
                                    is_hot=lambda v: v > hot_thresh if hot_thresh else False,
                                    is_cold=lambda v: v < cold_thresh if cold_thresh else False,
                                    all_data=all_data)


    def analyze_sl(self, historical_data, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a macd analysis on the historical data using signal line for alerting

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the MACD associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        macd_values = abstract.MACD(dataframe).iloc[:]

        # List of 2-tuples containing the ema value and closing price respectively
        analyzed_data = [(r[1]['macd'], r[1]['macdsignal']) for r in macd_values.iterrows()]

        return self.analyze_results(analyzed_data,
                                    is_hot=lambda v, s: v > s if hot_thresh else False,
                                    is_cold=lambda v, s: v < s if cold_thresh else False,
                                    all_data=all_data)
