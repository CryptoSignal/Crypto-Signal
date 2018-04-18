""" Crossover analysis indicator
"""

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class CrossOver(IndicatorUtils):
    def analyze(self, key_indicator, key_signal, crossed_indicator, crossed_signal):
        combined_data = pandas.concat([key_indicator, crossed_indicator], axis=1)

        combined_data['is_hot'] = combined_data[key_signal] > combined_data[crossed_signal]
        combined_data['is_cold'] = combined_data[key_signal] < combined_data[crossed_signal]

        return combined_data
