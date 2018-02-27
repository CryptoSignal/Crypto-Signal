""" Momentum Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class Momentum(IndicatorUtils):
    def analyze(self, historical_data, period_count=10,
                hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs momentum analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 10. The number of data points to consider for
                our simple moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the momentum
                associated with each data point in our historical dataset. Otherwise just return
                the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        mom_values = abstract.MOM(dataframe, period_count)

        mom_result_data = []
        for mom_value in mom_values:
            if math.isnan(mom_value):
                continue

            is_hot = False
            if hot_thresh is not None:
                is_hot = mom_value > hot_thresh

            is_cold = False
            if cold_thresh is not None:
                is_cold = mom_value < cold_thresh

            data_point_result = {
                'values': (mom_value,),
                'is_cold': is_cold,
                'is_hot': is_hot
            }

            mom_result_data.append(data_point_result)

        if all_data:
            return mom_result_data
        else:
            try:
                return mom_result_data[-1]
            except IndexError:
                return mom_result_data
