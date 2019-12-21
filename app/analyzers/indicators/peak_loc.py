""" ADX Indicator
"""

import scipy
import scipy.signal as scipySignal
import numpy as np

from analyzers.utils import IndicatorUtils

class Peak_Loc(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['peak_loc'], hot_thresh=None, cold_thresh=None):
        
        dataframe = self.convert_to_dataframe(historical_data)
        maxValues = list(map(lambda x, y: x if (x > y) else y, dataframe['close'], dataframe['open']))
        peaks = scipySignal.argrelextrema(np.asarray(maxValues), np.greater)[0]
        peak_loc_id = np.append(peaks, np.zeros(len(maxValues) - len(peaks)))

        peak_loc = dataframe.copy()
        peak_loc['peak_loc'] = peak_loc_id
        peak_loc.dropna(how='all', inplace=True)
        peak_loc.rename(columns={0: 'peak_loc'}, inplace=True)

        if peak_loc[signal[0]].shape[0]:
            peak_loc['is_hot'] = peak_loc[signal[0]] < hot_thresh
            peak_loc['is_cold'] = peak_loc[signal[0]] > cold_thresh

        return peak_loc.astype(int)