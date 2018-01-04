import structlog
from strategies.strategy_utils import Utils
import pandas as pd

class MovingAvgConvDiv():
    def __init__(self):
        self.logger = structlog.get_logger()
        self.utils = Utils()

    def get_12_day_EMA(self, frame):
        twelve_day_EMA = frame.ewm(span=12)
        return list(twelve_day_EMA.mean()["Prices"])

    def get_26_day_EMA(self, frame):
        twenty_six_day_EMA = frame.ewm(span=26)
        return list(twenty_six_day_EMA.mean()["Prices"])

    def calculate_MACD_line(self, historical_data):
        closing_prices = self.utils.get_closing_prices(historical_data)
        emadict = {"Prices": closing_prices}
        frame = pd.DataFrame(emadict)
        twelve_day_EMA = self.get_12_day_EMA(frame)
        twenty_six_day_EMA = self.get_26_day_EMA(frame)
        macd = []
        for i in range(len(twelve_day_EMA)):
            macd.append(twelve_day_EMA[i] - twenty_six_day_EMA[i])
        return macd

    def calculate_signal_line(self, macd):
        signaldata = []
        for i in macd:
            signaldata.append(i)
        signal_dict = {"Prices": signaldata}
        signal = pd.DataFrame(signal_dict)
        signal = signal.ewm(span=9)
        signal = list(signal.mean()["Prices"])
        return signal

    def calculate_MACD_delta(self, historical_data):
        MACD_line = self.calculate_MACD_line(historical_data)
        signal_line = self.calculate_signal_line(MACD_line)
        length = len(MACD_line)
        # Returns the difference between the last items in MACD and signal line
        return MACD_line[length-1] - signal_line[length-1]
