""" MACD Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class MACD(IndicatorUtils):
    def analyze(self, historical_data, signal='macd', hot_thresh=None, cold_thresh=None):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (string, optional): Defaults to macd. The indicator line to check hot/cold
                against.
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
        macd_values.dropna(how='all', inplace=True)

        if macd_values[signal].shape[0]:
            macd_values['is_hot'] = macd_values[signal] > hot_thresh
            macd_values['is_cold'] = macd_values[signal] < cold_thresh

        return macd_values
