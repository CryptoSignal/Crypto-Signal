
"""
Aroon Oscillator
"""

import numpy
import pandas

from analyzers.utils import IndicatorUtils


class Aroon_oscillator(IndicatorUtils):
    def analyze(self, historical_data, sma_vol_period, period_count=25, signal=["aroon"], hot_thresh=None, cold_thresh=None):
        """Performs an aroon oscillator analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to aroon. The indicator
                line to check hot/cold against.
            period_count (int, optional): Defaults to 25.
            sma_count (int, optional): Defaults to 50 (used of hot/cold check)
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """
        dataframe = self.convert_to_dataframe(historical_data)

        aroon_columns = {
            'aroon': [numpy.nan] * dataframe.index.shape[0],
            'aroon_up': [numpy.nan] * dataframe.index.shape[0],
            'aroon_down': [numpy.nan] * dataframe.index.shape[0]
        }

        aroon_values = pandas.DataFrame(aroon_columns,
                                        index=dataframe.index
                                        )

        for index in range(0, dataframe.shape[0]-24):
            id = dataframe.shape[0]-index
            id_period = id - period_count
            high_date = dataframe['high'].iloc[id_period:id].idxmax()
            low_date = dataframe['low'].iloc[id_period:id].idxmin()

            periods_since_high = id - dataframe.index.get_loc(high_date) - 1
            periods_since_low = id - dataframe.index.get_loc(low_date) - 1
            aroon_values['aroon_up'][id-1] = 100 * \
                ((25 - periods_since_high) / 25)

            aroon_values['aroon_down'][id-1] = 100 * \
                ((25 - periods_since_low) / 25)

        aroon_values['aroon'] = aroon_values['aroon_up'] - \
            aroon_values['aroon_down']

        aroon_values['is_hot'] = False
        aroon_values['is_cold'] = False

        aroon_values['sma_volume'] = dataframe.volume.rolling(
            sma_vol_period).mean()
        aroon = aroon_values['aroon'].iloc[-1]
        volume = dataframe['volume'].iloc[-1]
        volume_sma = aroon_values['sma_volume'].iloc[-1]

        if aroon > hot_thresh and volume > volume_sma:
            aroon_values['is_hot'].iloc[-1] = True
        elif aroon <= cold_thresh and volume > volume_sma:
            aroon_values['is_cold'].iloc[-1] = True

        return aroon_values
