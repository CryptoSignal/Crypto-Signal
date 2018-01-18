import time
import structlog

"""
A candlestick object, part of a time-series chart of historical data
"""
class Candlestick(object):
    def __init__(self, open=None, close=None, high=None, low=None, price_average=None):
        self.current = None
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.start_time = time.time()
        self.output = structlog.get_logger()
        self.price_average = price_average


