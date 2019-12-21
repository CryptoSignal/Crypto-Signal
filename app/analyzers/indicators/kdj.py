""" KDJ Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils
from analyzers.indicators.stoch_rsi import StochasticRSI

import heapq

import numpy as np

class KDJ(IndicatorUtils):
    
    def __init__(self):
        self.stoch_rsi = StochasticRSI()
    
    def analyze(self, historical_data, signal=['kdj'], hot_thresh=None, cold_thresh=None):
        """Performs a kdj analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to kdj. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

#         dataframe = self.convert_to_dataframe(historical_data)
#         kdj_values = self.stoch_rsi.analyze(historical_data)
#         kdj_values.dropna(how='all', inplace=True)
#         kdj_values['slow_j'] = (3 * kdj_values["slow_d"]) - (2 *  kdj_values["slow_k"])
#         kdj_values['kdj'] = kdj_values['slow_k']
#         if kdj_values[signal[0]].shape[0]:
#             kdj_values['is_hot'] = kdj_values[signal[0]] > hot_thresh
#             kdj_values['is_cold'] = kdj_values[signal[0]] < cold_thresh
#         return kdj_values
        
        dataframe = self.convert_to_dataframe(historical_data)
        kdjValue = self.kdjIndicator(dataframe)
        dataframe.rename(columns={0: 'kdj'}, inplace=True)
        dataframe['k'] = kdjValue[0];
        dataframe['d'] = kdjValue[1];
        dataframe['j'] = kdjValue[2];
        if dataframe['open'].shape[0]:
            dataframe['is_hot'] = dataframe['open'] < hot_thresh
            dataframe['is_cold'] = dataframe['open'] > cold_thresh
            
        return dataframe
        
    def kdjIndicator(self, prices, l=9, m=3, n=3):
        kdj_indicator = []
        heap_high = []
        heap_low = []
        for i in range(len(prices)):
            heapq.heappush(heap_high, -prices['high'][i])
            heapq.heappush(heap_low, prices['low'][i])
            if i>=l:
                heap_high.remove(-prices['high'][i-l])
                heap_low.remove(prices['low'][i-l])
                heapq.heapify(heap_high)
                heapq.heapify(heap_low)
                while len(heap_high)<l:
                    heap_high.heappush(-prices['high'][i-l])
                while len(heap_low)<l:
                    heap_low.heappush(prices['low'][i-l])
            rsvt = 0
            if -heap_high[0] > heap_low[0]:
                rsvt = (prices['close'][i] - heap_low[0])*100./(-heap_high[0]-heap_low[0])
            if i>0:
                kt = rsvt/m + (m-1)*kdj_indicator[i-1][0]/m
                dt = kt/n + (n-1)*kdj_indicator[i-1][1]/n
                jt = 3*kt - 2*dt
            else:
                kt = rsvt*1.0
                dt = kt
                jt = rsvt
            kdj_indicator.append([kt, dt ,jt])
            
        len_row = len(kdj_indicator)
        len_col = 3
        return np.array(kdj_indicator).T
            
