
""" 
Bollinger Bands indicator
"""

import math

import pandas
from talib import BBANDS

from analyzers.utils import IndicatorUtils


class Bollinger(IndicatorUtils):

    def analyze(self, historical_data, signal=['close'], hot_thresh=None, cold_thresh=None, period_count=20, std_dev=2):
        """Check when close price cross the Upper/Lower bands.

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 20. The number of data points to consider for the BB bands indicator.
            signal (list, optional): Defaults to close. Unused in this indicator
            std_dev (int, optional): number of std dev to use. Common values are 2 or 1

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        # Required to avoid getting same values for low, middle, up
        dataframe['close_10k'] = dataframe['close'] * 10000

        up_band, mid_band, low_band = BBANDS(
            dataframe['close_10k'], timeperiod=period_count, nbdevup=std_dev, nbdevdn=std_dev, matype=0)

        bollinger = pandas.concat(
            [dataframe, up_band, mid_band, low_band], axis=1)
        bollinger.rename(
            columns={0: 'up_band', 1: 'mid_band', 2: 'low_band'}, inplace=True)

        old_up, old_low = bollinger.iloc[-2]['up_band'], bollinger.iloc[-2]['low_band']
        cur_up, cur_low = bollinger.iloc[-1]['up_band'], bollinger.iloc[-1]['low_band']

        old_close = bollinger.iloc[-2]['close_10k']
        cur_close = bollinger.iloc[-1]['close_10k']

        bollinger['is_hot'] = False
        bollinger['is_cold'] = False

        bollinger['is_hot'].iloc[-1] = old_low < old_close and cur_low > cur_close
        bollinger['is_cold'].iloc[-1] = old_up > old_close and cur_up < cur_close

        bollinger['up_band'] = bollinger['up_band'] / 10000
        bollinger['mid_band'] = bollinger['mid_band'] / 10000
        bollinger['low_band'] = bollinger['low_band'] / 10000

        return bollinger
