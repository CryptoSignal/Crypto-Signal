""" RSI Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.informants.lrsi import LRSI
from analyzers.utils import IndicatorUtils


class RSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['rsi'], hot_thresh=None, cold_thresh=None,  lrsi_filter=None):
        """Performs an RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our RSI.
            signal (list, optional): Defaults to rsi. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        if lrsi_filter and 'gamma' in lrsi_filter:
            lrsi = LRSI()
            dataframe['lrsi'] = dataframe.close.apply(
                lambda x: lrsi.apply_filter(x, lrsi_filter['gamma']))

        rsi_values = abstract.RSI(dataframe, period_count).to_frame()
        rsi_values.dropna(how='all', inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)

        if rsi_values[signal[0]].shape[0]:
            rsi_values['is_hot'] = rsi_values.rsi.apply(
                lambda x: x > 20 and x < hot_thresh)
            rsi_values['is_cold'] = rsi_values[signal[0]] > cold_thresh

            if lrsi_filter and 'lower_values' in lrsi_filter:
                lower_min = lrsi_filter['lower_values']['min']
                lower_max = lrsi_filter['lower_values']['max']

                idx = dataframe['lrsi'].apply(
                    lambda x: x < lower_min or x > lower_max)
                rsi_values.loc[idx & (
                    rsi_values['is_hot'] == True), 'is_hot'] = False

        return rsi_values
