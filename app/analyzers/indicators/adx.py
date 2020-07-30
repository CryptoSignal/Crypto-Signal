
"""
Average Directional Index indicator
"""

import numpy
import pandas

from analyzers.utils import IndicatorUtils


class Adx(IndicatorUtils):
    def analyze(self, historical_data, signal=["adx"], period_count=14, hot_thresh=None, cold_thresh=None):
        """
        strength of a trend
        ADX > 25 = strength
        ADX < 20 = weak or trendless
        ------
        0-25    absent or weak trend
        25-50   strong trend
        50-75   very strong trend
        75-100  extremely strong trend
        """

        dataframe = self.convert_to_dataframe(historical_data)

        adx_columns = {
            'tr': [numpy.nan] * dataframe.index.shape[0],
            'atr': [numpy.nan] * dataframe.index.shape[0],
            'pdm': [numpy.nan] * dataframe.index.shape[0],
            'ndm': [numpy.nan] * dataframe.index.shape[0],
            'pdm_smooth': [numpy.nan] * dataframe.index.shape[0],
            'ndm_smooth': [numpy.nan] * dataframe.index.shape[0],
            'ndi': [numpy.nan] * dataframe.index.shape[0],
            'pdi': [numpy.nan] * dataframe.index.shape[0],
            'dx': [numpy.nan] * dataframe.index.shape[0],
            'adx': [numpy.nan] * dataframe.index.shape[0]
        }

        adx_values = pandas.DataFrame(adx_columns,
                                      index=dataframe.index
                                      )

        adx_values['tr'] = self.TR(dataframe['high'],
                                   dataframe['low'],
                                   dataframe['close'],
                                   adx_values['tr']
                                   )
        adx_values['pdm'], adx_values['ndm'] = self.DM(dataframe['high'],
                                                       dataframe['low'],
                                                       adx_values['pdm'],
                                                       adx_values['ndm']
                                                       )
        adx_values['pdm_smooth'], adx_values['ndm_smooth'] = self.DMsmooth(adx_values['pdm'],
                                                                           adx_values['ndm'],
                                                                           adx_values['pdm_smooth'],
                                                                           adx_values['ndm_smooth'],
                                                                           period_count
                                                                           )
        adx_values['pdi'], adx_values['ndi'] = self.DI(adx_values['pdm_smooth'],
                                                       adx_values['ndm_smooth'],
                                                       adx_values['tr'],
                                                       adx_values['pdi'],
                                                       adx_values['ndi']
                                                       )
        adx_values['atr'] = self.ATR(adx_values['tr'],
                                     adx_values['atr'],
                                     period_count
                                     )
        adx_values['dx'], adx_values['adx'] = self.ADX(adx_values['pdi'],
                                                       adx_values['ndi'],
                                                       adx_values['dx'],
                                                       adx_values['adx'],
                                                       period_count
                                                       )
        adx_values['is_hot'] = False
        adx_values['is_cold'] = False

        for index in range(0, adx_values.index.shape[0]):
            if adx_values['adx'][index] < cold_thresh:
                adx_values['is_cold'][index] = True
            elif adx_values['adx'][index] >= hot_thresh:
                adx_values['is_hot'][index] = True

        return adx_values

    def TR(self, high, low, close, tr):
        """
        Calculates TR (True Range)
        :param high: high from candles
        :param low: low from candles
        :param close: close from candles
        :param tr: true range
        :return: tr
        """

        tr[0] = abs(high[0] - low[0])
        for index in range(1, tr.shape[0]):
            x = high[index] - close[index]
            y = abs(high[index] - close[index - 1])
            z = abs(low[index] - close[index - 1])
            tr[index] = max(x, y, z)

        return tr

    def DM(self, high, low, pdm, ndm):
        """
        Calculates DM (Directional Movement)
        :param high: high from candles
        :param low: low from candles
        :param pdm: positive directional movement, nan dataframe
        :param ndm: negative directional movement, nan dataframe
        :return: pdm, ndm
        """

        for index in range(1, high.shape[0]):
            up_move = high[index] - high[index-1]
            down_move = low[index-1] - low[index]

            if up_move > down_move and up_move > 0:
                pdm[index] = up_move
            else:
                pdm[index] = 0
            if down_move > up_move and down_move > 0:
                ndm[index] = down_move
            else:
                ndm[index] = 0

        return pdm, ndm

    def DMsmooth(self, pdm, ndm, pdm_smooth, ndm_smooth, period_count):
        """
        Smoothing positive and negative directional movement
        :param pdm: positive directional movement
        :param ndm: negative directional movement
        :param pdm_smooth: positive directional movement smoothed
        :param ndm_smooth: negative directional movement smoothed
        :param period_count: time period_count
        :return: pdm_smooth, ndm_smooth
        """

        pdm_smooth[period_count-1] = pdm[0:period_count].sum() / period_count
        ndm_smooth[period_count - 1] = ndm[0:period_count].sum() / period_count
        for index in range(period_count, pdm.shape[0]):
            pdm_smooth[index] = (
                pdm[index-1] - (pdm_smooth[index-1]/period_count)) + pdm_smooth[index-1]
            ndm_smooth[index] = (
                ndm[index - 1] - (ndm_smooth[index-1] / period_count)) + ndm_smooth[index-1]

        return pdm_smooth, ndm_smooth

    def DI(self, pdm_smooth, ndm_smooth, tr, pdi, ndi):
        """
        Calculates DI (Directional Movement Indicator)
        :param pdm_smooth: positive directional movement smoothed
        :param ndm_smooth: negative directional movement smoothed
        :param tr: true range
        :param pdi: positive directional index, nan dataframe
        :param ndi: negative directional index, nan dataframe
        :return: pdi, ndi
        """

        for index in range(0, tr.shape[0]):
            pdi[index] = (pdm_smooth[index] / tr[index]) * 100
            ndi[index] = (ndm_smooth[index] / tr[index]) * 100

        return pdi, ndi

    def ATR(self, tr, atr, period_count):
        """
        Calculates ATR (Average True Range)
        Uses WILDER'S SMOOTHING METHOD
        ATR = a*TR + (1-a)* ATR_1
        a = (1/n)
        :param tr: true range
        :param atr: average true range, nan dataframe
        :param period_count: time period_count
        :return: atr
        """

        atr[period_count-1] = tr[0:period_count].sum() / period_count
        for index in range(period_count, tr.shape[0]):
            atr[index] = ((atr[index-1] * (period_count - 1)) +
                          tr[index]) / period_count

        return atr

    def ADX(self, pdi, ndi, dx, adx, period_count):
        """
        Calculates DX (Directional index) and ADX (Average Directional Index)
        :param pdi: positive directional index
        :param ndi: negative directional index
        :param dx: directional index, nan dataframe
        :param adx: average directional index, nan dataframe
        :param period_count: time period_count
        :return: dx, adx
        """

        for index in range(0, pdi.shape[0]):
            dx[index] = ((abs(pdi[index] - ndi[index])) /
                         (abs(pdi[index] + ndi[index]))) * 100

        period_count2 = period_count*2
        adx[period_count2-1] = dx[period_count:period_count2].sum() / \
            period_count
        for index in range(period_count2, dx.shape[0]):
            adx[index] = ((adx[index-1] * (period_count - 1)) +
                          dx[index]) / period_count

        return dx, adx
