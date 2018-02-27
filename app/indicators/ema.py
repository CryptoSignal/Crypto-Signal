""" EMA Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class EMA(IndicatorUtils):
    def analyze(self, historical_data, period_count=15, hot_thresh=False, cold_thresh=None, all_data=None):
        """Performs an EMA analysis on the historical data

		Args:
			historical_data (list): A matrix of historical OHCLV data.
			period_count (int, optional): Defaults to 15. The number of data points to consider for
				our exponential moving average.
			hot_thresh (float, optional): Defaults to None. The threshold at which this might be
				good to purchase.
			cold_thresh (float, optional): Defaults to None. The threshold at which this might be
				good to sell.
			all_data (bool, optional): Defaults to False. If True, we return the EMA associated
				with each data point in our historical dataset. Otherwise just return the last one.

		Returns:
			dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
				indication.
		"""

        dataframe = self.convert_to_dataframe(historical_data)
        ema_values = abstract.EMA(dataframe, period_count)
        combined_data = pandas.concat([dataframe, ema_values], axis=1)
        combined_data.rename(columns={0: 'ema_value'}, inplace=True)

        ema_result_data = []
        for ema_row in combined_data.iterrows():
            if math.isnan(ema_row[1]['ema_value']):
                continue

            is_hot = False
            if hot_thresh is not None:
                threshold = ema_row[1]['ema_value'] * hot_thresh
                is_hot = ema_row[1]['close'] > threshold

            is_cold = False
            if cold_thresh is not None:
                threshold = ema_row[1]['ema_value'] * cold_thresh
                is_cold = ema_row[1]['close'] < threshold

            data_point_result = {
                'values': (ema_row[1]['ema_value'],),
                'is_cold': is_cold,
                'is_hot': is_hot
            }

            ema_result_data.append(data_point_result)

        if all_data:
            return ema_result_data
        else:
            try:
                return ema_result_data[-1]
            except IndexError:
                return ema_result_data
