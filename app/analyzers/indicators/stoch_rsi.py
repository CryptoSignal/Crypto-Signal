""" Stochastic RSI Indicator
"""

import math

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class StochasticRSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['stoch_rsi'], hot_thresh=None, cold_thresh=None):
        """Performs a Stochastic RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our Stochastic RSI.
            signal (list, optional): Defaults to stoch_rsi. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        rsi_period_count = period_count * 2
        rsi_values = abstract.RSI(dataframe, rsi_period_count).to_frame()
        rsi_values.dropna(how='all', inplace=True)
        rsi_values.rename(columns={0: 'rsi'}, inplace=True)

        rsi_values = rsi_values.assign(stoch_rsi=numpy.nan)
        for index in range(period_count, rsi_values.shape[0]):
            start_index = index - period_count
            last_index = index + 1
            rsi_min = rsi_values['rsi'].iloc[start_index:last_index].min()
            rsi_max = rsi_values['rsi'].iloc[start_index:last_index].max()
            stoch_rsi = (100 * ((rsi_values['rsi'][index] - rsi_min) / (rsi_max - rsi_min)))
            rsi_values['stoch_rsi'][index] = stoch_rsi

        rsi_values['slow_k'] = rsi_values['stoch_rsi'].rolling(window=3).mean()
        rsi_values['slow_d'] = rsi_values['slow_k'].rolling(window=3).mean()
        rsi_values.dropna(how='any', inplace=True)

        if rsi_values[signal[0]].shape[0]:
            rsi_values['is_hot'] = rsi_values[signal[0]] < hot_thresh
            rsi_values['is_cold'] = rsi_values[signal[0]] > cold_thresh

        return rsi_values
