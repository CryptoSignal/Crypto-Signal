""" Custom Indicator Increase In  Volume
"""

import numpy as np
import pandas
import talib
from scipy import stats

from analyzers.utils import IndicatorUtils


class MARibbon(IndicatorUtils):

    # Exponential Moving Average
    def EMA(self, df, n, field='close'):
        return pandas.Series(talib.EMA(df[field].astype('f8').values, n), name='EMA_' + field.upper() + '_' + str(n), index=df.index)

    def MA_RIBBON(self, df, ma_series):
        ma_array = np.zeros([len(df), len(ma_series)])
        ema_list = []
        for idx, ma_len in enumerate(ma_series):
            ema_i = self.EMA(df, n=ma_len, field='close')
            ma_array[:, idx] = ema_i
            ema_list.append(ema_i)
        corr = np.empty([len(df)])
        pval = np.empty([len(df)])
        dist = np.empty([len(df)])
        corr[:] = np.NAN
        pval[:] = np.NAN
        dist[:] = np.NAN
        max_n = max(ma_series)

        for idy in range(len(df)):
            if idy >= max_n - 1:
                corr[idy], pval[idy] = stats.spearmanr(
                    ma_array[idy, :], range(len(ma_series), 0, -1))
                dist[idy] = max(ma_array[idy, :]) - min(ma_array[idy, :])

        corr_ts = pandas.Series(corr*100, index=df.index,
                                name="MARIBBON_CORR").round(2)
        pval_ts = pandas.Series(pval*100, index=df.index,
                                name="MARIBBON_PVAL").round(2)
        dist_ts = pandas.Series(dist, index=df.index, name="MARIBBON_DIST")

        return pandas.concat([corr_ts, pval_ts, dist_ts] + ema_list, join='outer', axis=1)

    def analyze(self, historical_data, pval_th, ma_series, signal=['ma_ribbon'],
                hot_thresh=10, cold_thresh=-10):
        """Performs an analysis about the increase in volumen on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to ma_ribbon. The indicator line to check hot against.
            pval_th (integer):
            hot_thresh (integer):
            cold_thresh (integer):
            ma_series (list): 

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        ma_ribbon = self.MA_RIBBON(dataframe, ma_series)

        ma_ribbon.rename(
            columns={'MARIBBON_PVAL': 'pval', 'MARIBBON_CORR': 'corr'}, inplace=True)

        ribbon_pval = ma_ribbon['pval'][-1]
        ribbon_corr = ma_ribbon['corr'][-1]
        ribbon_prev_corr = ma_ribbon['corr'][-2]

        ma_ribbon['is_hot'] = False
        ma_ribbon['is_cold'] = False

        if ribbon_pval < pval_th:
            if ribbon_corr >= hot_thresh and ribbon_corr > ribbon_prev_corr:
                ma_ribbon['is_hot'].iloc[-1] = True
            if ribbon_corr <= cold_thresh and ribbon_prev_corr > ribbon_corr:
                ma_ribbon['is_cold'].iloc[-1] = True

        return ma_ribbon
