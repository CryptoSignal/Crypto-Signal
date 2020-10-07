""" Ichimoku Indicator
"""

import math

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class Ichimoku(IndicatorUtils):
    def analyze(self, historical_data, signal=['leading_span_a', 'leading_span_b'], hot_thresh=None, cold_thresh=None):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to leading_span_a and leading_span_b. The indicator
                line to check hot/cold against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        tenkansen_period = 9
        kijunsen_period = 26
        leading_span_b_period = 52

        dataframe = self.convert_to_dataframe(historical_data)

        ichimoku_columns = {
            'tenkansen': [numpy.nan] * dataframe.index.shape[0],
            'kijunsen': [numpy.nan] * dataframe.index.shape[0],
            'leading_span_a': [numpy.nan] * dataframe.index.shape[0],
            'leading_span_b': [numpy.nan] * dataframe.index.shape[0]
        }

        ichimoku_values = pandas.DataFrame(
            ichimoku_columns,
            index=dataframe.index
        )

        ichimoku_df_size = ichimoku_values.shape[0]

        for index in range(tenkansen_period, ichimoku_df_size):
            start_index = index - tenkansen_period
            last_index = index + 1
            tankansen_min = dataframe['low'][start_index:last_index].min()
            tankansen_max = dataframe['high'][start_index:last_index].max()
            ichimoku_values['tenkansen'][index] = (tankansen_min + tankansen_max) / 2

        for index in range(kijunsen_period, ichimoku_df_size):
            start_index = index - kijunsen_period
            last_index = index + 1
            kijunsen_min = dataframe['low'][start_index:last_index].min()
            kijunsen_max = dataframe['high'][start_index:last_index].max()
            ichimoku_values['kijunsen'][index] = (kijunsen_min + kijunsen_max) / 2

        for index in range(leading_span_b_period, ichimoku_df_size):
            start_index = index - leading_span_b_period
            last_index = index + 1
            leading_span_b_min = dataframe['low'][start_index:last_index].min()
            leading_span_b_max = dataframe['high'][start_index:last_index].max()
            ichimoku_values['leading_span_b'][index] = (
                leading_span_b_min + leading_span_b_max
            ) / 2

        ichimoku_values['leading_span_a'] = (
            ichimoku_values['tenkansen'] + ichimoku_values['kijunsen']
        ) / 2

        ichimoku_values.dropna(how='any', inplace=True)
        ichimoku_df_size = ichimoku_values.shape[0]

        ichimoku_values['is_hot'] = False
        ichimoku_values['is_cold'] = False

        for index in range(0, ichimoku_df_size):
            span_hot = ichimoku_values['leading_span_a'][index] > ichimoku_values['leading_span_b'][index]
            close_hot = dataframe['close'][index] > ichimoku_values['leading_span_a'][index]
            if hot_thresh:
                ichimoku_values.at[ichimoku_values.index[index], 'is_hot'] = span_hot and close_hot

            span_cold = ichimoku_values['leading_span_a'][index] < ichimoku_values['leading_span_b'][index]
            close_cold = dataframe['close'][index] < ichimoku_values['leading_span_a'][index]
            if cold_thresh:
                ichimoku_values.at[ichimoku_values.index[index], 'is_cold'] = span_cold and close_cold

        return ichimoku_values
