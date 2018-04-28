""" Crossover analysis indicator
"""

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class CrossOver(IndicatorUtils):
    def analyze(self, key_indicator, key_signal, crossed_indicator, crossed_signal):
        """ Tests for key_indicator crossing over the crossed_indicator.

        Args:
            key_indicator (pandas.DataFrame): A dataframe containing the results of the analysis
                for the selected key indicator.
            key_signal (str): The name of the key indicator.
            crossed_indicator (pandas.DataFrame): A dataframe containing the results of the
                analysis for the selected indicator to test for a cross.
            crossed_signal (str): The name of the indicator expecting to be crossed.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        key_indicator_name = key_signal + '_key'
        key_indicator.rename(columns={key_signal: key_indicator_name}, inplace=True)

        crossed_indicator_name = crossed_signal + '_crossed'
        crossed_indicator.rename(columns={crossed_signal: crossed_indicator_name}, inplace=True)

        combined_data = pandas.concat([key_indicator, crossed_indicator], axis=1)
        combined_data.dropna(how='any', inplace=True)

        combined_data['is_hot'] = combined_data[key_indicator_name] > combined_data[crossed_indicator_name]
        combined_data['is_cold'] = combined_data[key_indicator_name] < combined_data[crossed_indicator_name]

        return combined_data
