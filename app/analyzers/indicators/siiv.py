""" Custom Indicator Increase In  Volume
"""

import numpy as np
from scipy import stats

from analyzers.utils import IndicatorUtils

"""
name: ahmet aksoy
date: 2022-11-20
siiv: Signed Increase In Volume
"""
class SIIV(IndicatorUtils):
    def analyze(self, historical_data, signal=['siiv'], hot_thresh=10, cold_thresh=-10):
        """Performs an analysis about the increase in volumen on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to siiv. The indicator line to check hot against.
            hot_thresh (float, optional): Defaults to 10. 
            cold_thresh: Unused


        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        z = np.abs(stats.zscore(dataframe['volume']))
        filtered = dataframe.volume[(z < 3)]

        previous_mean = filtered.mean()
        price_change = dataframe.close[-1] - dataframe.close[-2]

        if price_change>=0:
            dataframe[signal[0]] = dataframe['volume'] / previous_mean
        else:
            dataframe[signal[0]] = -dataframe['volume'] / previous_mean

        dataframe['is_hot'] = False
        dataframe['is_cold'] = False
        dataframe['is_hot'] = dataframe[signal[0]] >= hot_thresh
        dataframe['is_cold'] = dataframe[signal[0]] <= cold_thresh

        return dataframe
