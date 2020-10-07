""" RSI Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class RSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['rsi'], hot_thresh=None, cold_thresh=None):
        """Performs an RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our RSI.
            signal (list, optional): Defaults to rsi. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        rsi_values = abstract.RSI(dataframe, period_count).to_frame()
        rsi_values.dropna(how='all', inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)

        if rsi_values[signal[0]].shape[0]:
            rsi_values['is_hot'] = rsi_values[signal[0]] < hot_thresh
            rsi_values['is_cold'] = rsi_values[signal[0]] > cold_thresh

        return rsi_values
