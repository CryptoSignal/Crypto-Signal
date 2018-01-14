import time
import structlog

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

    def tick(self, price):
        self.current = float(price)
        if self.open is None:
            self.open = self.current

        if self.high is None or self.current > self.high:
            self.high = self.current

        if self.low is None or self.current < self.low:
            self.low = self.current

        if time.time() >= self.start_time + self.period:
            self.close = self.current
            self.price_average = (self.high + self.low + self.close) / float(3)

        self.output.info("Open: "+str(self.open)+" Close: "+str(self.close)+" High: "+str(self.high)+" Low: "+str(self.low)+" Current: "+str(self.current))

    def is_closed(self):
        return self.close is not None

