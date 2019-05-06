"""
Klinger Oscillator
"""

import pandas
import os
import numpy
from talib import abstract

from analyzers.utils import IndicatorUtils


class Klinger_oscillator():
    def analyze(self, historical_data, signal=['ema_long, ema_short'], hot_tresh=None, cold_tresh=None):
        """
        Klinger Oscillator = 34 period EMA of VF - 55 period EMA of VF
            LEADING INDICATOR
            USE WITH STOCHASTIC OSCILLATOR
        -----
        VF (volume force) = volume* ABS(Temp) *trend*100
        Temp = 2*((dm/cm)-1)
        
        if (high+low+close)/3 > (high_1+low_1+close_1)/3
            Trend = +1 
        if < or =
            Trend = -1        
        
        dm = high - low
        
        
        CM[today] =     / CM[yesterday] + DM[today] IF  trend[today]==trend[yesterday]
                        \ DM[yesterday] + DM[today] IF  trend[today]!=trend[yesterday]
        
        if Trend = Trend_1
            cm = cm_1 + dm 
        if Trend =/= Trend_1
            cm = dm_1 + dm 
        -----
        EMA = (c*A)+(E*B)
        C = current period's VF
        A = 2/(X+1) where C is the moving average period(34 or 55)
        E = prior period's EMA
        B = 1-A
        ------
        chart
        KVO line = (fast EMA  - flow EMA) = 32periodEMA(vf) - 55periodEMA(vf)
            green
        signal line = 13 period EMA of KVO line
            red
        ====
        dm = daily measurement
        cm = cumulative measurement
        vf = volume force
        
        """
        dataframe = self.convert_to_dataframe(historical_data)

        klinger_columns = {
            'mean': [numpy.nan] * dataframe.index.shape[0],
            'trend': [numpy.nan] * dataframe.index.shape[0],
            'dm': [numpy.nan] * dataframe.index.shape[0],
            'cm': [numpy.nan] * dataframe.index.shape[0],
            'volumeforce': [numpy.nan] * dataframe.index.shape[0],
            'ema_short': [numpy.nan] * dataframe.index.shape[0],
            'ema_long': [numpy.nan] * dataframe.index.shape[0],
            'kvo': [numpy.nan] * dataframe.index.shape[0],
            'vf': [numpy.nan] * dataframe.index.shape[0],
            'vfema': [numpy.nan] * dataframe.index.shape[0]
        }

        klinger_values = pandas.DataFrame(klinger_columns,
                                           index=dataframe.index
                                           )

        klinger_values['mean'] = dataframe[['high', 'low', 'close']].mean(axis=1)
        for index in range(1, (klinger_values.shape[0])):
            klinger_values['dm'] = dataframe['high'][index] - dataframe['low'][index]
            if klinger_values['mean'][index] > klinger_values['mean'][index-1]:
                klinger_values['trend'][index] = 1
            else:
                klinger_values['trend'][index] = -1

        for index in range(0, (klinger_values.shape[0])):
            klinger_values['cm_a'] = klinger_values['dm'][index] + klinger_values['dm'][index-1]
            if klinger_values['trend'][index] == klinger_values['trend'][index-1]:
                klinger_values['cm'][index] = klinger_values['cm'][index-1] + klinger_values['dm'][index]
            else:
                klinger_values['cm'][index] = klinger_values['dm'][index] + klinger_values['dm'][index-1]
        abstract.EMA(dataframe, period_count).to_frame()

        ema_short_period = 32
        ema_long_period = 55
        ema_vf_period = 13

        klinger_values['volumeforce'] = dataframe['volume'] * abs(2*((klinger_values['dm']/klinger_values['cm'])-1)) * klinger_values['trend'] * 100
        klinger_values['ema_short'] = abstract.EMA(klinger_values['volumeforce'], ema_short_period).to_frame()
        klinger_values['ema_long'] = abstract.EMA(klinger_values['volumeforce'], ema_long_period).to_frame()
        klinger_values['kvo'] = klinger_values['ema_short'] - klinger_values['ema_long']
        klinger_values['vf'] = klinger_values['ema_short'] - klinger_values['ema_long']
        klinger_values['vfema'] = abstract.EMA(klinger_values['vf'], ema_vf_period).to_frame()

        return klinger_values
