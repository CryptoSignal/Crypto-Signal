"""
Klinger Oscillator
The Klinger oscillator was developed by Stephen Klinger to determine the long-term trend of money flow
while remaining sensitive enough to detect short-term fluctuations. The indicator compares the volume
flowing through a security with the security's price movements and then converts the result into an oscillator.
The Klinger oscillator shows the difference between two moving averages which are based on more than price.
Traders watch for divergence on the indicator to signal potential price reversals.
Like other oscillators, a signal line can be added to provide additional trade signals.
"""

import os

import numpy
import pandas

from analyzers.utils import IndicatorUtils


class Klinger_oscillator(IndicatorUtils):
    def analyze(self, historical_data, ema_short_period, ema_long_period, signal_period, signal=['kvo, kvo_signal'], hot_thresh=None, cold_thresh=None):
        """Performs a Klinger Oscillator analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to kvo and kvo_signal.
            ema_short_period (int, optional): Short ema for Volume Force
            ema_long_period (int, optional): Long ema for Volume Force
            signal_period (int, optional): Ema for KVO signal line
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        ===============================================================================================================
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
        -----
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
            'vf': [numpy.nan] * dataframe.index.shape[0],
            'vf_ema_short': [numpy.nan] * dataframe.index.shape[0],
            'vf_ema_long': [numpy.nan] * dataframe.index.shape[0],
            'kvo': [numpy.nan] * dataframe.index.shape[0],
            'kvo_signal': [numpy.nan] * dataframe.index.shape[0]
        }

        klinger_values = pandas.DataFrame(klinger_columns,
                                          index=dataframe.index
                                          )

        klinger_values['mean'] = dataframe[[
            'high', 'low', 'close']].mean(axis=1)
        for index in range(1, (klinger_values.shape[0])):
            klinger_values['dm'] = dataframe['high'][index] - \
                dataframe['low'][index]
            if klinger_values['mean'][index] > klinger_values['mean'][index-1]:
                klinger_values['trend'][index] = 1
            else:
                klinger_values['trend'][index] = -1

        for index in range(0, (klinger_values.shape[0])):
            klinger_values['cm_a'] = klinger_values['dm'][index] + \
                klinger_values['dm'][index-1]
            if klinger_values['trend'][index] == klinger_values['trend'][index-1]:
                klinger_values['cm'][index] = klinger_values['cm'][index -
                                                                   1] + klinger_values['dm'][index]
            else:
                klinger_values['cm'][index] = klinger_values['dm'][index] + \
                    klinger_values['dm'][index-1]

        klinger_values['vf'] = dataframe['volume'] * abs(
            2*((klinger_values['dm']/klinger_values['cm'])-1)) * klinger_values['trend'] * 100
        klinger_values['vf_ema_short'] = klinger_values['vf'].ewm(
            span=ema_short_period, min_periods=0, adjust=False, ignore_na=True).mean()
        klinger_values['vf_ema_long'] = klinger_values['vf'].ewm(
            span=ema_long_period, min_periods=0, adjust=False, ignore_na=True).mean()
        klinger_values['kvo'] = klinger_values['vf_ema_short'] - \
            klinger_values['vf_ema_long']
        klinger_values['kvo_signal'] = klinger_values['kvo'].ewm(
            span=signal_period, min_periods=0, adjust=False, ignore_na=True).mean()

        klinger_values['is_hot'] = False
        klinger_values['is_cold'] = False

        for index in range(1, klinger_values.shape[0]):
            ## might want to change mean index-1 to longer period and not just last candle ##
            if klinger_values['kvo_signal'][index] > 0 and klinger_values['mean'][index] > klinger_values['mean'][index-1]:
                klinger_values['is_hot'][index] = True
            elif klinger_values['kvo_signal'][index] <= 0 and klinger_values['mean'][index] < klinger_values['mean'][index-1]:
                klinger_values['is_cold'][index]

        return klinger_values
