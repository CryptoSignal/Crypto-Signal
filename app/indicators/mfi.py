""" Momentum Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class MFI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                hot_thresh=None, cold_thresh=None, all_data=False):

        dataframe = self.convert_to_dataframe(historical_data)
        mom_values = abstract.MFI(dataframe, period_count)

        analyzed_data = [(value,) for value in mom_values]

        return self.analyze_results(analyzed_data,
                                    is_hot=lambda v: v > hot_thresh if hot_thresh else False,
                                    is_cold=lambda v: v < cold_thresh if cold_thresh else False,
                                    all_data=all_data)

