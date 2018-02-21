""" SMA Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class SMA(IndicatorUtils):
    def analyze(self, historical_data, period_count=15,
                    hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a SMA analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our simple moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the SMA associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        sma_values = abstract.SMA(dataframe, period_count)
        combined_data = pandas.concat([dataframe, sma_values], axis=1)
        combined_data.rename(columns={0: 'sma_value'}, inplace=True)

        sma_result_data = []
        for sma_row in combined_data.iterrows():
            if math.isnan(sma_row[1]['sma_value']):
                continue

            is_hot = False
            if hot_thresh is not None:
                threshold = sma_row[1]['sma_value'] * hot_thresh
                is_hot = sma_row[1]['close'] > threshold

            is_cold = False
            if cold_thresh is not None:
                threshold = sma_row[1]['sma_value'] * cold_thresh
                is_cold = sma_row[1]['close'] < threshold

            data_point_result = {
                'values': (sma_row[1]['sma_value'],),
                'is_cold': is_cold,
                'is_hot': is_hot
            }

            sma_result_data.append(data_point_result)

        if all_data:
            return sma_result_data
        else:
            try:
                return sma_result_data[-1]
            except IndexError:
                return sma_result_data
