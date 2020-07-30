""" MFI Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class MFI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['mfi'], hot_thresh=None, cold_thresh=None):
        """Performs MFI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our MFI.
            signal (list, optional): Defaults to mfi. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        mfi_values = abstract.MFI(dataframe, period_count).to_frame()
        mfi_values.dropna(how='all', inplace=True)
        mfi_values.rename(columns={0: 'mfi'}, inplace=True)

        if mfi_values[signal[0]].shape[0]:
            mfi_values['is_hot'] = mfi_values[signal[0]] < hot_thresh
            mfi_values['is_cold'] = mfi_values[signal[0]] > cold_thresh

        return mfi_values
