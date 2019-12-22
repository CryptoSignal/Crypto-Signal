""" MFI Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class TD(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['td'], hot_thresh=None, cold_thresh=None):
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
        td_values = self.td_sequential(dataframe)
        td_values.dropna(how='all', inplace=True)
        td_values.rename(columns={0: 'td'}, inplace=True)

        if td_values[signal[0]].shape[0]:
            td_values['is_hot'] = td_values[signal[0]] < hot_thresh
            td_values['is_cold'] = td_values[signal[0]] > cold_thresh
        return td_values


    def td_sequential(self, dataframe):
        """
        TD Sequential
        :param dataframe: dataframe
        :return: TD Sequential:values -9 to +9
        """
        """
        TD Sequential
        """

        # Copy DF
        df = dataframe.copy()

        condv = (df['volume'] > 0)
        cond1 = (df['close'] > df['close'].shift(4))
        cond2 = (df['close'] < df['close'].shift(4))

        df['cond_tdb_a'] = (df.groupby((((cond1)[condv])).cumsum()).cumcount() % 10 == 0).cumsum()
        df['cond_tds_a'] = (df.groupby((((cond2)[condv])).cumsum()).cumcount() % 10 == 0).cumsum()
        df['cond_tdb_b'] = (df.groupby((((cond1)[condv])).cumsum()).cumcount() % 10 != 0).cumsum()
        df['cond_tds_b'] = (df.groupby((((cond2)[condv])).cumsum()).cumcount() % 10 != 0).cumsum()

        df['tdb_a'] = df.groupby(

            df['cond_tdb_a']

        ).cumcount()
        df['tds_a'] = df.groupby(

            df['cond_tds_a']

        ).cumcount()

        df['tdb_b'] = df.groupby(

            df['cond_tdb_b']

        ).cumcount()
        df['tds_b'] = df.groupby(

            df['cond_tds_b']

        ).cumcount()

        df['td'] = df['tds_a'] - df['tdb_a']
        df['td'] = df.apply((lambda x: x['tdb_b'] % 9 if x['tdb_b'] > 9 else x['td']), axis=1)
        df['td'] = df.apply((lambda x: (x['tds_b'] % 9) * -1 if x['tds_b'] > 9 else x['td']), axis=1)

        return df
