""" MACD Indicator
"""

import math

import pandas
from talib import abstract

from indicators.utils import IndicatorUtils


class MACD(IndicatorUtils):
    def analyze(self, historical_data, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the MACD associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        macd_values = abstract.MACD(dataframe).iloc[:, 0]

        macd_result_data = []
        for macd_value in macd_values:
            if math.isnan(macd_value):
                continue

            is_hot = False
            if hot_thresh is not None:
                is_hot = macd_value > hot_thresh

            is_cold = False
            if cold_thresh is not None:
                is_cold = macd_value < cold_thresh

            data_point_result = {
                'values': (macd_value,),
                'is_cold': is_cold,
                'is_hot': is_hot
            }

            macd_result_data.append(data_point_result)

        if all_data:
            return macd_result_data
        else:
            try:
                return macd_result_data[-1]
            except IndexError:
                return macd_result_data


    def analyze_sl(self, historical_data, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a macd analysis on the historical data using signal line for alerting

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            all_data (bool, optional): Defaults to False. If True, we return the MACD associated
                with each data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        macd_values = abstract.MACD(dataframe).iloc[:]

        macd_result_data = []
        for macd_row in macd_values.iterrows():
            if math.isnan(macd_row[1]['macd']) or math.isnan(macd_row[1]['macdsignal']):
                continue

            is_hot = False
            if hot_thresh is not None:
                is_hot = macd_row[1]['macd'] > macd_row[1]['macdsignal']

            is_cold = False
            if cold_thresh is not None:
                is_cold = macd_row[1]['macd'] < macd_row[1]['macdsignal']

            data_point_result = {
                'values': (macd_row[1]['macd'],),
                'is_cold': is_cold,
                'is_hot': is_hot
            }

            macd_result_data.append(data_point_result)

        if all_data:
            return macd_result_data
        else:
            try:
                return macd_result_data[-1]
            except IndexError:
                return macd_result_data
