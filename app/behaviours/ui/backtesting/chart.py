import json
from time import time

import matplotlib.pyplot as plt

from exchange import ExchangeInterface
from behaviours.ui.backtesting.indicators import BacktestingIndicators
from behaviours.ui.backtesting.candlestick import Candlestick

"""
A Chart class encompassing functionality for a set of historical data in a time-series domain
"""
class Chart(object):
    def __init__(self, pair, period, exchange_name, exchange_interface, start_time=time() - 2000000):

        self.pair = pair
        self.period = period

        self.start_time = start_time

        self.data = []

        # Query the data to fill our chart truncate it to 'length' elements
        rawdata = exchange_interface.get_historical_data(pair, exchange_name, period, start_time*1000)

        for i in range(len(rawdata)):
            datum = rawdata[i]
            stick = Candlestick(open=datum[1], high=datum[2], low=datum[3], close=datum[4], price_average=(datum[2] + datum[3])/2.)
            stick.time = i
            self.data.append(stick)

    def get_points(self):
        return self.data

    '''
    Returns the indicators specified in the **kwargs dictionary as a json-serializable dictionary
    '''
    def get_indicators(self, **kwargs):

        # Indicators are hardcoded for now. Will be updated to accommodate variable-sized MA's
        response = {
            'bollinger_upper': [],
            'bollinger_lower': [],
            'movingaverage9': [],
            'movingaverage15': []
        }

        # Get closing historical datapoints
        closings = list(map(lambda x: x.close, self.data))

        # The 'bollinger' keyword argument takes in a period, i.e. bollinger=21
        if "bollinger" in kwargs:
            period = kwargs["bollinger"]
            assert type(period) is int

            bbupper, bblower = BacktestingIndicators.historical_bollinger_bands(closings)
            response['bollinger_lower'] = list(bblower)
            response['bollinger_upper'] = list(bbupper)

        # The 'movingaverage' keyword argument takes in a list of periods, i.e. movingaverage=[9,15,21]
        if "movingaverage" in kwargs:
            periods = kwargs["movingaverage"]
            assert type(periods) is list

            for period in periods:
                response['movingaverage' + str(period)] = list(BacktestingIndicators.historical_moving_average(closings, period=period))

        return response

    '''
    Plots the specified indicators on a matplotlib plot
    '''
    def plot_indicators(self, **kwargs):

        # Get closing historical datapoints and plot them first
        closings = list(map(lambda x: x.close, self.data))
        plt.plot(closings)

        # The 'bollinger' keyword argument takes in a period, i.e. bollinger=21
        if "bollinger" in kwargs:
            period = kwargs["bollinger"]
            assert type(period) is int

            bbupper, bblower = BacktestingIndicators.historical_bollinger_bands(closings)
            plt.plot(np.arange(period, len(closings)), bbupper[period:], 'g--')
            plt.plot(np.arange(period, len(closings)), bblower[period:], 'b--')

        # The 'movingaverage' keyword argument takes in a list of periods, i.e. movingaverage=[9,15,21]
        if "movingaverage" in kwargs:
            periods = kwargs["movingaverage"]
            assert type(periods) is list

            for period in periods:
                plt.plot(BacktestingIndicators.historical_moving_average(closings, period=period))

    '''
    Plots each buy trade as a green 'x', and each sell trade as a red 'x'
    '''
    def plot_trades(self, buys, sells):
        for timestamp, price in buys:
            plt.plot(timestamp, price, 'gx')

        for timestamp, price in sells:
            plt.plot(timestamp, price, 'rx')



