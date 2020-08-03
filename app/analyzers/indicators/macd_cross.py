""" MACD Cross
"""

import math

import pandas
import talib

from analyzers.utils import IndicatorUtils


class MACDCross(IndicatorUtils):

    def analyze(self, historical_data, signal=['macd'], hot_thresh=None, cold_thresh=None):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to macd
            hot_thresh (float, optional): Unused for this indicator
            cold_thresh (float, optional): Unused for this indicator

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        macd, macdsignal, macdhist = talib.MACD(
            dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)

        macd_values = pandas.DataFrame([macd, macdsignal]).T.rename(
            columns={0: "macd", 1: "signal"})

        macd_cross = pandas.concat([dataframe, macd_values], axis=1)
        macd_cross.dropna(how='all', inplace=True)

        previous_macd, previous_signal = macd_cross.iloc[-2]['macd'], macd_cross.iloc[-2]['signal']
        current_macd, current_signal = macd_cross.iloc[-1]['macd'], macd_cross.iloc[-1]['signal']

        macd_cross['is_hot'] = False
        macd_cross['is_cold'] = False

        macd_cross['is_cold'].iloc[-1] = previous_macd > previous_signal and current_macd < current_signal
        macd_cross['is_hot'].iloc[-1] = previous_macd < previous_signal and current_macd > current_signal

        return macd_cross
