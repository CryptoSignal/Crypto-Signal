
""" 
Bollinger Bands indicator
"""

import math

import pandas
from talib import BBANDS, abstract

from analyzers.utils import IndicatorUtils


class BBP(IndicatorUtils):

    def analyze(self, historical_data, signal=['bbp'], hot_thresh=0, cold_thresh=0.8, period_count=20, std_dev=2):
        """Check when close price cross the Upper/Lower bands.

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 20. The number of data points to consider for the BB bands indicator.
            signal (list, optional): Defaults bbp value.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to 0.8. The threshold at which this might be
                good to sell.            
            std_dev (int, optional): number of std dev to use. Common values are 2 or 1

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        mfi = abstract.MFI(dataframe, period_count=14)

        # Required to avoid getting same values for low, middle, up
        dataframe['close_10k'] = dataframe['close'] * 10000

        up_band, mid_band, low_band = BBANDS(
            dataframe['close_10k'], timeperiod=period_count, nbdevup=std_dev, nbdevdn=std_dev, matype=0)

        bbp = (dataframe['close_10k'] - low_band) / (up_band - low_band)

        bollinger = pandas.concat([dataframe, bbp, mfi], axis=1)
        bollinger.rename(columns={0: 'bbp', 1: 'mfi'}, inplace=True)

        bollinger['is_hot'] = False
        bollinger['is_cold'] = False

        bollinger['is_hot'].iloc[-1] = bollinger['bbp'].iloc[-2] <= hot_thresh and bollinger['bbp'].iloc[-2] < bollinger['bbp'].iloc[-1]
        bollinger['is_cold'].iloc[-1] = bollinger['bbp'].iloc[-1] >= cold_thresh

        return bollinger
