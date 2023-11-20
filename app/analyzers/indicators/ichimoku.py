""" Ichimoku Indicator
"""

import math

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils
from importlib import import_module


class Ichimoku(IndicatorUtils):
    def analyze(self, historical_data, tenkansen_period, kijunsen_period, senkou_span_b_period, custom_strategy=None,
                signal=['tenkansen', 'kijunsen'], hot_thresh=None, cold_thresh=None, chart=None):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to tenkansen and kijunsen. The indicator
                line to check hot/cold against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            tenkansen_period (int, optional)
            kijunsen_period (int, optional)
            senkou_span_b_period (int, optional)
            custom_strategy (string, optional): Defaults to None. Name of the custom strategy. The file name and class name 
                should have the same name as the custom strategy. 

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        ichimoku_columns = {
            'tenkansen': [numpy.nan] * dataframe.index.shape[0],
            'kijunsen': [numpy.nan] * dataframe.index.shape[0],
            'leading_span_a': [numpy.nan] * dataframe.index.shape[0],
            'leading_span_b': [numpy.nan] * dataframe.index.shape[0],
            'chikou_span' : [numpy.nan] * dataframe.index.shape[0]
        }

        ichimoku_values = pandas.DataFrame(ichimoku_columns,
                                           index=dataframe.index
                                           )
        # value calculations
        low_tenkansen = dataframe['low'].rolling(window=tenkansen_period).min()
        low_kijunsen = dataframe['low'].rolling(window=kijunsen_period).min()
        low_senkou = dataframe['low'].rolling(
            window=senkou_span_b_period).min()
        high_tenkansen = dataframe['high'].rolling(
            window=tenkansen_period).max()
        high_kijunsen = dataframe['high'].rolling(window=kijunsen_period).max()
        high_senkou = dataframe['high'].rolling(
            window=senkou_span_b_period).max()

        chikou_span_delay = 26
        ichimoku_values['chikou_span'] = dataframe['close'].shift(-chikou_span_delay)
        ichimoku_values['tenkansen'] = (low_tenkansen + high_tenkansen) / 2
        ichimoku_values['kijunsen'] = (low_kijunsen + high_kijunsen) / 2
        ichimoku_values['leading_span_a'] = (
            (ichimoku_values['tenkansen'] + ichimoku_values['kijunsen']) / 2)
        ichimoku_values['leading_span_b'] = (high_senkou + low_senkou) / 2

        ichimoku_values['is_hot'] = False
        ichimoku_values['is_cold'] = False

        try:
            # add time period for cloud offset
            ## if cloud discplacement changed the ichimuko plot will be off ##
            cloud_displacement = 26
            last_time = dataframe.index[-1]
            timedelta = dataframe.index[1] - dataframe.index[0]
            newindex = pandas.date_range(last_time + timedelta,
                                         freq=timedelta,
                                         periods=cloud_displacement)
            ichimoku_values = ichimoku_values.append(
                pandas.DataFrame(index=newindex))
            # cloud offset
            ichimoku_values['leading_span_a'] = ichimoku_values['leading_span_a'].shift(
                cloud_displacement)
            ichimoku_values['leading_span_b'] = ichimoku_values['leading_span_b'].shift(
                cloud_displacement)
    
            if chart == None:
                if custom_strategy == None:
                    leading_span_hot = False
                    leading_span_cold = False
                    tk_cross_hot = False
                    tk_cross_cold = False
                    tk_cross_enabled = (('tenkansen' and 'kijunsen') in signal)
                    leading_span_enabled = (('leading_span_a' and 'leading_span_b') in signal)
                    date = dataframe.index[-1]
                    leading_span_date = ichimoku_values.index[-1]

                    if tk_cross_enabled:
                        tk_cross_hot = ichimoku_values['tenkansen'][date] > ichimoku_values['kijunsen'][date]
                        tk_cross_cold = ichimoku_values['tenkansen'][date] < ichimoku_values['kijunsen'][date]

                    if leading_span_enabled:
                        leading_span_hot = ichimoku_values['leading_span_a'][leading_span_date] > ichimoku_values['leading_span_b'][leading_span_date]
                        leading_span_cold = ichimoku_values['leading_span_a'][leading_span_date] < ichimoku_values['leading_span_b'][leading_span_date]

                    if hot_thresh:
                        ichimoku_values.at[date, 'is_hot'] = tk_cross_hot or leading_span_hot

                    if cold_thresh:
                        ichimoku_values.at[date, 'is_cold'] = tk_cross_cold or leading_span_cold
                else:
                    module = import_module("user_data.strategies." + custom_strategy)
                    attr = getattr(module, custom_strategy)  

                    custom_hot, custom_cold = attr.analyze(ichimoku_values, dataframe)
                    date = dataframe.index[-1]

                    if hot_thresh:
                        ichimoku_values.at[date, 'is_hot'] = custom_hot

                    if cold_thresh:
                        ichimoku_values.at[date, 'is_cold'] = custom_cold

                # Undo shifting in order to have the values aligned for displaying
                ichimoku_values['chikou_span'] = dataframe['close']
                ichimoku_values['leading_span_a'] = ichimoku_values['leading_span_a'].shift(-cloud_displacement)
                ichimoku_values['leading_span_b'] = ichimoku_values['leading_span_b'].shift(-cloud_displacement)
  
                ichimoku_values.dropna(how='any', inplace=True)

        except Exception as e:
            print('Error running ichimoku analysis: {}'.format(e))

        return ichimoku_values
