import json
from time import time

import matplotlib.pyplot as plt

from exchange import ExchangeInterface
from analysis import StrategyAnalyzer
from behaviours.ui.backtesting.candlestick import Candlestick

"""
A Chart class encompassing functionality for a set of historical data in a time-series domain
"""
class Chart(object):
    def __init__(self, pair, period, exchange_name, exchange_interface, start_time=time() - 2000000):

        self.pair = pair
        self.period = period

        self.start_time = start_time
        self.indicators = StrategyAnalyzer()

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
        from math import isnan

        # Indicators are hardcoded for now. Will be updated to accommodate variable-sized MA's
        response = {
            'bollinger_upper': [],
            'bollinger_lower': [],
            'sma9': [],
            'sma15': []
        }

        # Get closing historical datapoints
        closings = [[0, 0, 0, 0, x.close, 0] for x in self.data]

        # The 'bollinger' keyword argument takes in a period, i.e. bollinger=21
        if "bollinger" in kwargs:
            period = kwargs["bollinger"]
            assert type(period) is int

            # Offset each band by "period" data points
            bbupper = [(i + period, datum["values"][0]) for i, datum in enumerate(self.indicators.analyze_bollinger_bands(closings, all_data=True))]
            bblower = [(i + period, datum["values"][2]) for i, datum in enumerate(self.indicators.analyze_bollinger_bands(closings, all_data=True))]

            response['bollinger_upper'] = bbupper
            response['bollinger_lower'] = bblower


        # The 'sma' keyword argument takes in a list of periods, i.e. sma=[9,15,21]
        if "sma" in kwargs:
            periods = kwargs["sma"]
            assert type(periods) is list

            for period in periods:
                # Offset each sma by "period" data points
                response['sma' + str(period)] = [(i + period, datum["values"][0]) for i, datum in
                                                 enumerate(self.indicators.analyze_sma(closings, period_count=period, all_data=True))]

        return response

    '''
    ####################################################################
    ### THIS FUNCTION IS DEPRECATED. PLOT IS NOW DISPLAYED ON THE UI ###
    ####################################################################
    
    Plots the specified indicators on a matplotlib plot
    '''
    def plot_indicators(self, **kwargs):
        import numpy as np

        # Get closing historical datapoints
        closings = [[0, 0, 0, 0, x.close, 0] for x in self.data]
        plt.plot([x.close for x in self.data])

        # The 'bollinger' keyword argument takes in a period, i.e. bollinger=21
        if "bollinger" in kwargs:
            period = kwargs["bollinger"]
            assert type(period) is int

            bbupper = [np.nan_to_num(datum["values"][0]) for datum in self.indicators.analyze_bollinger_bands(closings, all_data=True)]
            bblower = [np.nan_to_num(datum["values"][2]) for datum in self.indicators.analyze_bollinger_bands(closings, all_data=True)]
            plt.plot(np.arange(period, len(closings)), bbupper[period:], 'g--')
            plt.plot(np.arange(period, len(closings)), bblower[period:], 'b--')

        # The 'sma' keyword argument takes in a list of periods, i.e. sma=[9,15,21]
        if "sma" in kwargs:
            periods = kwargs["sma"]
            assert type(periods) is list

            for period in periods:
                plt.plot([np.nan_to_num(datum["values"][0]) for datum in self.indicators.analyze_sma(closings, period_count=period, all_data=True)])

    '''
    Plots each buy trade as a green 'x', and each sell trade as a red 'x'
    '''
    def plot_trades(self, buys, sells):
        for timestamp, price in buys:
            plt.plot(timestamp, price, 'gx')

        for timestamp, price in sells:
            plt.plot(timestamp, price, 'rx')



