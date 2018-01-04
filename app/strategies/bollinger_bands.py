"""
Computes the Bollinger Bands over a series of historical data points
"""

from strategy_utils import Utils
from moving_averages import MovingAverages
import structlog
import numpy as np


class BollingerBands(object):
    """
    Bollinger Bands
    """

    def __init__(self):
        self.logger = structlog.get_logger()
        self.utils = Utils()
        self.sma = MovingAverages()

    '''
    Retrieves the upper and lower bollinger bands for the given parameters:

    :param historical_data: A list of historical data points for a coin pair
    :param period: The period of the moving average to be used in bollinger calculation (defaults to 21)
    :param k: The number of standard deviations away from the 'period'-length moving average
              to place the upper and lower band (defaults to 2)

    :returns A 2-element tuple containing the upper and lower band, respectively.
    '''

    def get_bollinger_bands(self, historical_data, period=21, k=2):
        sma = self.sma.calculate_sma(period, historical_data)
        closing_prices = self.utils.get_closing_prices(historical_data)
        std_dev = np.std(closing_prices[-period:])

        return sma + k * std_dev, sma - k * std_dev
