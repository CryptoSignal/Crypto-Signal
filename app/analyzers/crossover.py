""" Crossover analysis indicator
"""

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class CrossOver(IndicatorUtils):
    def analyze(self, key_indicator, key_signal, key_indicator_index,
                crossed_indicator, crossed_signal, crossed_indicator_index):
        """ Tests for key_indicator crossing over the crossed_indicator.

        Args:
            key_indicator (pandas.DataFrame): A dataframe containing the results of the analysis
                for the selected key indicator.
            key_signal (str): The name of the key indicator.
            key_indicator_index (int): The configuration index of the key indicator to use.
            crossed_indicator (pandas.DataFrame): A dataframe containing the results of the
                analysis for the selected indicator to test for a cross.
            crossed_signal (str): The name of the indicator expecting to be crossed.
            crossed_indicator_index (int): The configuration index of the crossed indicator to use.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        key_indicator_name = '{}_{}'.format(key_signal, key_indicator_index)
        new_key_indicator = key_indicator.copy(deep=True)
        for column in new_key_indicator:
            column_indexed_name = '{}_{}'.format(column, key_indicator_index)
            new_key_indicator.rename(columns={column: column_indexed_name}, inplace=True)

        crossed_indicator_name = '{}_{}'.format(crossed_signal, crossed_indicator_index)
        new_crossed_indicator = crossed_indicator.copy(deep=True)
        for column in new_crossed_indicator:
            column_indexed_name = '{}_{}'.format(column, crossed_indicator_index)
            new_crossed_indicator.rename(columns={column: column_indexed_name}, inplace=True)

        combined_data = pandas.concat([new_key_indicator, new_crossed_indicator], axis=1)
        combined_data.dropna(how='any', inplace=True)

        combined_data['is_hot'] = combined_data[key_indicator_name] > combined_data[crossed_indicator_name]
        combined_data['is_cold'] = combined_data[key_indicator_name] < combined_data[crossed_indicator_name]

        return combined_data
