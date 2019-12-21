""" ADX Indicator
"""

import scipy.signal as scipySignal
import numpy as np

from analyzers.utils import IndicatorUtils

class Valley_Loc(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['valley_loc'], hot_thresh=None, cold_thresh=None):

        dataframe = self.convert_to_dataframe(historical_data)
        minValues = list(map(lambda x, y: x if (x < y) else y, dataframe['close'], dataframe['open']))
        minValues = list(map(lambda x: -x, minValues))
        valleys = scipySignal.argrelextrema(np.asarray(minValues), np.greater)[0]
        valley_loc_id = np.append(valleys, np.zeros(len(minValues) - len(valleys)))

        valley_loc = dataframe.copy()
        valley_loc['valley_loc'] = valley_loc_id
        valley_loc.dropna(how='all', inplace=True)
        valley_loc.rename(columns={0: 'valley_loc'}, inplace=True)

        if valley_loc[signal[0]].shape[0]:
            valley_loc['is_hot'] = valley_loc[signal[0]] < hot_thresh
            valley_loc['is_cold'] = valley_loc[signal[0]] > cold_thresh

        return valley_loc.astype(int)