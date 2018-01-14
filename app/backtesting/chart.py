import json
from time import time

import matplotlib.pyplot as plt

from exchange import ExchangeInterface
from backtesting.indicators import *
from backtesting.candlestick import Candlestick


class Chart(object):
    def __init__(self, pair, period, exchange_name, exchange_config, start_time=time() - 2000000, length=9999999):

        self.exchange_name = exchange_name
        self.pair = pair
        self.period = period
        self.length = length

        self.start_time = start_time

        self.data = []

        exchange = ExchangeInterface(exchange_config)

        # Query the data to fill our chart truncate it to 'length' elements
        rawdata = exchange.get_historical_data(pair, exchange_name, period, start_time*1000)[:length]

        for i in range(len(rawdata)):
            datum = rawdata[i]
            stick = Candlestick(open=datum[1], high=datum[2], low=datum[3], close=datum[4], price_average=(datum[2] + datum[3])/2.)
            stick.time = i
            self.data.append(stick)

    def get_points(self):
        return self.data

    def get_current_price(self):
        # If we are using bittrex, then self.connv1 will be defined (this check is pure stupidity
        # as Bittrex removed the get_ticker API route from V2.0 -___-
        if self.connv1:
            current_values = self.connv1.get_ticker(self.pair)
        else:
            current_values = self.conn.get_ticker(self.pair)
        last_pair_price = current_values['result']["Last"]
        return last_pair_price

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

    def plot_trades(self, buys, sells):
        for timestamp, price in buys:
            plt.plot(timestamp, price, 'gx')

        for timestamp, price in sells:
            plt.plot(timestamp, price, 'rx')



