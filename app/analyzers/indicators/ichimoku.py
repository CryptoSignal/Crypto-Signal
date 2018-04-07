""" Ichimoku Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class Ichimoku(IndicatorUtils):
    def analyze(self, historical_data, hot_thresh=None, cold_thresh=None):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        tenkansen_period = 9
        kijunsen_period = 26
        senkou_span_b_period = 52

        tenkansen_historical_data = historical_data[-tenkansen_period:]
        kijunsen_historical_data = historical_data[-kijunsen_period:]
        senkou_span_b_historical_data = historical_data[-senkou_span_b_period:]

        tenkan_sen = self.get_tenkansen(tenkansen_historical_data)
        kijun_sen = self.get_kijunsen(kijunsen_historical_data)

        leading_span_a = self.get_senkou_span_a(
            kijunsen_historical_data,
            tenkansen_historical_data
        )

        leading_span_b = self.get_senkou_span_b(senkou_span_b_historical_data)

        is_hot = False
        if leading_span_a > leading_span_b and hot_thresh is not None:
            if historical_data[-1][4] > leading_span_a:
                is_hot = True

        is_cold = False
        if leading_span_a < leading_span_b and cold_thresh is not None:
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


    def get_kijunsen(self, historical_data):
        """Calculates (26 period high + 26 period low) / 2. Also known as the "Kijun-sen" line

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The Kijun-sen line value of ichimoku.
        """

        period_high = max(self.get_high_prices(historical_data))
        period_low = min(self.get_low_prices(historical_data))

        return (period_high + period_low) / 2


    def get_tenkansen(self, historical_data):
        """Calculates (9 period high + 9 period low) / 2. Also known as the "Tenkan-sen" line

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The Tenkan-sen line value of ichimoku.
        """

        period_high = max(self.get_high_prices(historical_data))
        period_low = min(self.get_low_prices(historical_data))

        return (period_high + period_low) / 2


    def get_senkou_span_a(self, kijunsen_data, tenkansen_data):
        """Calculates (Conversion Line + Base Line) / 2. Also known as the "Senkou Span A" line

        Args:
            kijunsen_data (float): The Kijun-sen line value of ichimoku.
            tenkansen_data (float): The Tenkan-sen line value of ichimoku.

        Returns:
            float: The Senkou span A value of ichimoku.
        """

        kijunsen_line = self.get_kijunsen(kijunsen_data)
        tenkansen_line = self.get_tenkansen(tenkansen_data)

        return (kijunsen_line + tenkansen_line) / 2


    def get_senkou_span_b(self, historical_data):
        """Calculates (52 period high + 52 period low) / 2. Also known as the "Senkou Span B" line

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The Senkou span B value of ichimoku.
        """

        period_high = max(self.get_high_prices(historical_data))
        period_low = min(self.get_low_prices(historical_data))

        return (period_high + period_low) / 2
