import pandas
import talib
from talib import abstract

from analyzers.utils import IndicatorUtils


class MainFilter(IndicatorUtils):
    def macd(self, historical_data, condition):
        """Performs a macd analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            condition (string, optional): Basic conditon to evalute

        Returns:
            boolean: True when MACD condtion is met
        """

        dataframe = self.convert_to_dataframe(historical_data)

        macd, macdsignal, macdhist = talib.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)

        macd_values = pandas.DataFrame([macd, macdsignal]).T.rename(
            columns={0: "macd", 1: "signal"})

        last_macd = macd_values['macd'].iloc[-1]
        last_signal = macd_values['signal'].iloc[-1]

        result  = False

        if condition == 'uptrend':
            result = last_macd > last_signal
        else:
            result = last_macd < last_signal

        if condition == 'downtrend':
            result = last_macd < last_signal
        else:
            result = last_macd > last_signal

        return result