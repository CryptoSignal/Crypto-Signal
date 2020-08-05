""" Ichimoku Indicator
"""

import math

import numpy
import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class Ichimoku(IndicatorUtils):
    def analyze(self, historical_data, tenkansen_period, kijunsen_period, senkou_span_b_period,
                signal=['leading_span_a', 'leading_span_b'], hot_thresh=None, cold_thresh=None, chart=None):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to leading_span_a and leading_span_b. The indicator
                line to check hot/cold against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            tenkansen_period (int, optional)
            kijunsen_period (int, optional)
            senkou_span_b_period (int, optional)

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        ichimoku_columns = {
            'tenkansen': [numpy.nan] * dataframe.index.shape[0],
            'kijunsen': [numpy.nan] * dataframe.index.shape[0],
            'leading_span_a': [numpy.nan] * dataframe.index.shape[0],
            'leading_span_b': [numpy.nan] * dataframe.index.shape[0]
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

            for index in range(0, ichimoku_values.index.shape[0]):
                date = ichimoku_values.index[index]

                if date <= dataframe.index[-1]:
                    span_hot = ichimoku_values['leading_span_a'][date] > ichimoku_values['leading_span_b'][date]
                    close_hot = dataframe['close'][date] > ichimoku_values['leading_span_a'][date]
                    if hot_thresh:
                        ichimoku_values.at[date,
                                           'is_hot'] = span_hot and close_hot
                    span_cold = ichimoku_values['leading_span_a'][date] < ichimoku_values['leading_span_b'][date]
                    close_cold = dataframe['close'][date] < ichimoku_values['leading_span_a'][date]
                    if cold_thresh:
                        ichimoku_values.at[date,
                                           'is_cold'] = span_cold and close_cold
                else:
                    pass

        except Exception as e:
            print('Error running ichimoku analysis: {}'.format(e))

        if chart == None:
            ichimoku_values.dropna(how='any', inplace=True)

        return ichimoku_values
