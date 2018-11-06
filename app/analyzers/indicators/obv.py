""" OBV Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class OBV(IndicatorUtils):
    def analyze(self, historical_data, signal=["obv"], hot_thresh=None, cold_thresh=None):
        """Performs OBV analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to obv. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        obv_values = abstract.OBV(dataframe).to_frame()

        obv_values.dropna(how="all", inplace=True)
        obv_values.rename(columns={obv_values.columns[0]: "obv"}, inplace=True)

        if obv_values[signal[0]].shape[0]:
            obv_values["is_hot"] = obv_values[signal[0]] > hot_thresh
            obv_values["is_cold"] = obv_values[signal[0]] < cold_thresh

        return obv_values
