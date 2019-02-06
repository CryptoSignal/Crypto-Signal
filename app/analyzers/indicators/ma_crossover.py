""" Custom Indicator Increase In  Volume
"""

from talib import abstract
import pandas
import math

from analyzers.utils import IndicatorUtils


class MACrossover(IndicatorUtils):

    def analyze(self, historical_data, signal=['close'], hot_thresh=None, cold_thresh=None, exponential = True, ma_fast = 10, ma_slow = 50):
        """Performs an analysis about the increase in volumen on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to close. Unused in this indicator
            exponential (boolean): flag to indicate is EMA is used
            ma_fast (integer): periods to use to calculate the fast MA
            ma_slow (integer): periods to use to calculate the slow MA

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        
        if exponential == True:
            ma_fast_values = abstract.EMA(dataframe, ma_fast)
            ma_slow_values = abstract.EMA(dataframe, ma_slow)
        else:
            ma_fast_values = abstract.SMA(dataframe, ma_fast)
            ma_slow_values = abstract.SMA(dataframe, ma_slow)

        ma_crossover = pandas.concat([dataframe, ma_fast_values, ma_slow_values], axis=1)
        ma_crossover.rename(columns={0: 'ma_value_one', 1: 'ma_value_two'}, inplace=True)

        o1, o2 = ma_crossover.iloc[-2]['ma_value_one'] , ma_crossover.iloc[-2]['ma_value_two']
        c1, c2 = ma_crossover.iloc[-1]['ma_value_one'] , ma_crossover.iloc[-1]['ma_value_two']

        ma_crossover['is_hot']  = False
        ma_crossover['is_cold'] = False

        ma_crossover['is_hot'].iloc[-1] = o1 < o2 and c1 > c2
        ma_crossover['is_cold'].iloc[-1] = o1 > o2 and c1 < c2

        return ma_crossover