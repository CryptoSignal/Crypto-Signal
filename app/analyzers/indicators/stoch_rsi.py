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

        rsi = abstract.RSI(dataframe, period_count)

        stochrsi  = (rsi - rsi.rolling(period_count).min()) / (rsi.rolling(period_count).max() - rsi.rolling(period_count).min())
        stochrsi_K = stochrsi.rolling(3).mean()
        stochrsi_D = stochrsi_K.rolling(3).mean()

        kd_values = pandas.DataFrame([stochrsi, stochrsi_K, stochrsi_D]).T.rename(
            columns={0: "stoch_rsi", 1: "slow_k", 2: "slow_d"}).copy()

        kd_values['stoch_rsi'] = kd_values['stoch_rsi'].multiply(100)
        kd_values['slow_k'] = kd_values['slow_k'].multiply(100)
        kd_values['slow_d'] = kd_values['slow_d'].multiply(100)

        stoch_rsi = pandas.concat([dataframe, kd_values], axis=1)
        stoch_rsi.dropna(how='all', inplace=True)

        if stoch_rsi[signal[0]].shape[0]:
            stoch_rsi['is_hot'] = stoch_rsi[signal[0]] < hot_thresh
            stoch_rsi['is_cold'] = stoch_rsi[signal[0]] > cold_thresh

        return stoch_rsi
