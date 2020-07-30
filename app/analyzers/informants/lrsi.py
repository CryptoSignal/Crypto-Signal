""" 
    LaguerreRSI from  Backtrader
    https://github.com/backtrader/backtrader

    Defined by John F. Ehlers in `Cybernetic Analysis for Stock and Futures`,
    2004, published by Wiley. `ISBN: 978-0-471-46307-8`
    
    The Laguerre RSI tries to implements a better RSI by providing a sort of
    *Time Warp without Time Travel* using a Laguerre filter. 
    
    This provides for faster reactions to price changes
    ``gamma`` is meant to have values between ``0.2`` and ``0.8``, with the
    best balance found theoretically at the default of ``0.5``    
"""

import numpy as np

from analyzers.utils import IndicatorUtils


class LRSI(IndicatorUtils):
    l0, l1, l2, l3 = 0.0, 0.0, 0.0, 0.0

    def apply_filter(self, price, gamma):
        l0_1 = self.l0
        l1_1 = self.l1
        l2_1 = self.l2

        g = gamma  # avoid more lookups
        self.l0 = l0 = (1.0 - g) * price + g * l0_1
        self.l1 = l1 = -g * l0 + l0_1 + g * l1_1
        self.l2 = l2 = -g * l1 + l1_1 + g * l2_1
        self.l3 = l3 = -g * l2 + l2_1 + g * self.l3

        cu = 0.0
        cd = 0.0
        if l0 >= l1:
            cu = l0 - l1
        else:
            cd = l1 - l0

        if l1 >= l2:
            cu += l1 - l2
        else:
            cd += l2 - l1

        if l2 >= l3:
            cu += l2 - l3
        else:
            cd += l3 - l2

        den = cu + cd

        return 1.0 if not den else cu / den

    def analyze(self, historical_data, signal=['lrsi']):
        """Performs a better implementation of RSI

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to iiv. The indicator line to check hot against.
            hot_thresh (float, optional): Defaults to 0.2. The threshold at which this might be
                good to purchase.
            cold_thresh: Defaults to 0.8. The threshold at which this might be
                good to sell.


        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)

        dataframe['lrsi'] = dataframe.close.apply(
            lambda x: self.apply_filter(x, 0.4))

        return dataframe
