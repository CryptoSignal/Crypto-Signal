""" VWAP Indicator
"""

import math

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class VWAP(IndicatorUtils):
    def analyze(self, historical_data, period_count=15):
        """Performs a VWAP analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our simple moving average.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        vwap_values = pandas.DataFrame(numpy.nan, index=dataframe.index, columns=['vwap'])

        for index in range(period_count, vwap_values.shape[0]):
            start_index = index - period_count
            last_index = index + 1

            total_volume = dataframe['volume'].iloc[start_index:last_index].sum()
            total_high = dataframe['high'].iloc[start_index:last_index].sum()
            total_low = dataframe['low'].iloc[start_index:last_index].sum()

            total_average_price = total_volume * (total_high + total_low) / 2

            vwap = total_average_price / total_volume
            vwap_values['vwap'][last_index-1] = vwap

        vwap_values.dropna(how='all', inplace=True)

        return vwap_values


