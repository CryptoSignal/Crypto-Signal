""" Bollinger Bands Indicator
"""

import math

from talib import abstract

from indicators.utils import IndicatorUtils


class BollingerIndicator(IndicatorUtils):
    def analyze(self, historical_data, period_count=21, all_data=False):
        """Performs a bollinger band analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            all_data (bool, optional): Defaults to False. If True, we return the BB's associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        bollinger_data = abstract.BBANDS(dataframe, period_count)

        bb_result_data = []
        for bb_row in bollinger_data.iterrows():
            if math.isnan(bb_row[1]['upperband']) or \
                    math.isnan(bb_row[1]['middleband']) or \
                    math.isnan(bb_row[1]['lowerband']):
                continue

            data_point_result = {
                'values': (
                    bb_row[1]['upperband'],
                    bb_row[1]['middleband'],
                    bb_row[1]['lowerband']
                ),
                'is_hot': False,
                'is_cold': False
            }

            bb_result_data.append(data_point_result)

        if all_data:
            return bb_result_data
        else:
            try:
                return bb_result_data[-1]
            except IndexError:
                return bb_result_data
