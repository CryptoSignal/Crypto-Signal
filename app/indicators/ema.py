""" EMA Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class EMA(IndicatorUtils):
    def analyze(self, historical_data, period_count=15, hot_thresh=None, cold_thresh=None, all_data=None):
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

        # List of 2-tuples containing the ema value and closing price respectively
        analyzed_data = [(r[1]['ema_value'], r[1]['close']) for r in combined_data.iterrows()]

        return self.analyze_results(analyzed_data,
                                    is_hot=lambda v, c: c > v * hot_thresh if hot_thresh else False,
                                    is_cold=lambda v, c: c < v * cold_thresh if cold_thresh else False,
                                    all_data=all_data)
