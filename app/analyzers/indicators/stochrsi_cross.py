""" MACD Cross
"""

import math
import pandas

from talib import abstract
from analyzers.utils import IndicatorUtils


class StochRSICross(IndicatorUtils):

    def analyze(self, historical_data, period_count=14, signal=['stoch_rsi'], smooth_k = 10, smooth_d = 3, hot_thresh=None, cold_thresh=None):
        """Performs a StochRSI cross analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to macd
            smooth_k (integer): number of periods to calculate the smooth K line
            smooth_d (integer): number of periods to calculate the smooth D line
            hot_thresh (float, optional): Unused for this indicator
            cold_thresh (float, optional): Unused for this indicator            

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        rsi = abstract.RSI(dataframe, period_count)
        stochrsi  = (rsi - rsi.rolling(period_count).min()) / (rsi.rolling(period_count).max() - rsi.rolling(period_count).min())
        stochrsi_K = stochrsi.rolling(smooth_k).mean()
        stochrsi_D = stochrsi_K.rolling(smooth_d).mean()

        kd_values = pandas.DataFrame([rsi, stochrsi, stochrsi_K, stochrsi_D]).T.rename(
            columns={0: "rsi", 1: "stoch_rsi", 2: "smooth_k", 3: "smooth_d"}).copy()

        kd_values['stoch_rsi'] = kd_values['stoch_rsi'].multiply(100)
        kd_values['smooth_k'] = kd_values['smooth_k'].multiply(100)
        kd_values['smooth_d'] = kd_values['smooth_d'].multiply(100)

        stoch_cross = pandas.concat([dataframe, kd_values], axis=1)
        stoch_cross.dropna(how='all', inplace=True)

        previous_k, previous_d = stoch_cross.iloc[-2]['smooth_k'], stoch_cross.iloc[-2]['smooth_d']
        current_k, current_d = stoch_cross.iloc[-1]['smooth_k'], stoch_cross.iloc[-1]['smooth_d']

        stoch_cross['is_hot'] = False
        stoch_cross['is_cold'] = False

        stoch_cross.at[stoch_cross.index[-1], 'is_cold'] = previous_k > previous_d and current_k < current_d
        stoch_cross.at[stoch_cross.index[-1], 'is_hot'] = previous_k < previous_d and current_k > current_d

        return stoch_cross
