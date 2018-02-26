""" Ichimoku Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils
from indicators.analyzers.ichimoku_cloud import IchimokuCloud


class Ichimoku(IndicatorUtils):
    def analyze(self, historical_data, hot_thresh=False, cold_thresh=False):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to False. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to False. The threshold at which this might be
                good to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        ic_analyzer = IchimokuCloud()

        tenkansen_period = 9
        kijunsen_period = 26
        senkou_span_b_period = 52

        tenkansen_historical_data = historical_data[-tenkansen_period:]
        kijunsen_historical_data = historical_data[-kijunsen_period:]
        senkou_span_b_historical_data = historical_data[-senkou_span_b_period:]

        tenkan_sen = ic_analyzer.get_tenkansen(tenkansen_historical_data)
        kijun_sen = ic_analyzer.get_kijunsen(kijunsen_historical_data)

        leading_span_a = ic_analyzer.get_senkou_span_a(
            kijunsen_historical_data,
            tenkansen_historical_data
        )

        leading_span_b = ic_analyzer.get_senkou_span_b(senkou_span_b_historical_data)

        is_hot = False
        if leading_span_a > leading_span_b and hot_thresh is not False:
            if historical_data[-1][4] > leading_span_a:
                is_hot = True

        is_cold = False
        if leading_span_a < leading_span_b and cold_thresh is not False:
            if historical_data[-1][4] < leading_span_b:
                is_cold = True

        if math.isnan(tenkan_sen):
            tenkan_sen = None

        if math.isnan(kijun_sen):
            kijun_sen = None

        ichimoku_data = {
            'values': (tenkan_sen, kijun_sen),
            'is_hot': is_hot,
            'is_cold': is_cold
        }

        return ichimoku_data
