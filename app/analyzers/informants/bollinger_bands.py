""" Bollinger Bands Indicator
"""

import math

import numpy
import pandas
import tulipy

from analyzers.utils import IndicatorUtils


class Bollinger(IndicatorUtils):
    def analyze(self, historical_data, period_count=21):
        """Performs a bollinger band analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 21. The number of data points to consider for
                our bollinger bands.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        bb_columns = {
            'upperband': [numpy.nan] * dataframe.index.shape[0],
            'middleband': [numpy.nan] * dataframe.index.shape[0],
            'lowerband': [numpy.nan] * dataframe.index.shape[0]
        }

        bb_values = pandas.DataFrame(
            bb_columns,
            index=dataframe.index
        )

        bb_df_size = bb_values.shape[0]
        close_data = numpy.array(dataframe['close'])

        if close_data.size > period_count:
            bb_data = tulipy.bbands(close_data, period_count, 2)

            for index in range(period_count, bb_df_size):
                data_index = index - period_count
                bb_values['lowerband'][index] = bb_data[0][data_index]
                bb_values['middleband'][index] = bb_data[1][data_index]
                bb_values['upperband'][index] = bb_data[2][data_index]

        bb_values.dropna(how='all', inplace=True)

        return bb_values
