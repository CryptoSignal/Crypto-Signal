"""Executes the trading strategies and analyzes the results.
"""

from datetime import datetime, timedelta, timezone

import numpy as np
import structlog
import pandas
from talib import abstract

from strategies.breakout import Breakout
from strategies.ichimoku_cloud import IchimokuCloud

class StrategyAnalyzer():
    """Contains all the methods required for analyzing strategies.
    """

    def __init__(self, exchange_interface):
        """Initializes StrategyAnalyzer class

        Args:
            exchange_interface (ExchangeInterface): An instances of the ExchangeInterface class for
                interacting with exchanges.
        """

        self.__exchange_interface = exchange_interface
        self.logger = structlog.get_logger()

    def __threshold_data_generator(self, data_value, hot_thresh, cold_thresh):
        data_value = np.nan_to_num(data_value)

        is_hot = False
        if hot_thresh is not None:
            is_hot = data_value <= hot_thresh

        is_cold = False
        if cold_thresh is not None:
            is_cold = data_value >= cold_thresh

        return {
            'values': data_value,
            'is_cold': is_cold,
            'is_hot': is_hot
        }

    def __convert_to_dataframe(self, historical_data):
        """Converts historical data matrix to a pandas dataframe.

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            pandas.DataFrame: Contains the historical data in a pandas dataframe.
        """

        dataframe = pandas.DataFrame(historical_data)
        dataframe.transpose()

        dataframe = pandas.DataFrame(historical_data)
        dataframe.transpose()
        dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        dataframe['datetime'] = dataframe.timestamp.apply(
            lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)

        return dataframe

    def get_historical_data(self, market_pair, exchange, time_unit, max_days=100):
        """Fetches the historical data

        Args:
            market_pair (str): Contains the symbol pair to operate on i.e. BURST/BTC
            exchange (str): Contains the exchange to fetch the historical data from.
            time_unit (str): A string specifying the ccxt time unit i.e. 5m or 1d.
            max_days (int, optional): Defaults to 100. Maximum number of days to fetch data for.

        Returns:
            list: Contains a list of lists which contain timestamp, open, high, low, close, volume.
        """

        # The data_start_date timestamp must be in milliseconds hence * 1000.
        data_start_date = datetime.now() - timedelta(days=max_days)
        data_start_date = int(data_start_date.replace(tzinfo=timezone.utc).timestamp() * 1000)
        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            time_unit=time_unit,
            start_date=data_start_date
        )

        return historical_data


    def analyze_macd(self, historial_data, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a macd analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to sell.
            all_data (bool, optional): Defaults to False. If True, we return the MACD associated with each
                data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.__convert_to_dataframe(historial_data)
        macd_values = abstract.MACD(dataframe).iloc[:, 0]

        if all_data:
            return [self.__threshold_data_generator(value, hot_thresh=None, cold_thresh=None) for value in macd_values]

        else:
            macd_lastrow = macd_values.iloc[-1]

            return self.__threshold_data_generator(macd_lastrow, hot_thresh=None, cold_thresh=None)


    def analyze_breakout(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs a momentum analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        breakout_analyzer = Breakout()

        period_count = 5

        breakout_historical_data = historial_data[0:period_count]

        breakout_value = breakout_analyzer.get_breakout_value(breakout_historical_data)

        return self.__threshold_data_generator(breakout_value, hot_thresh=hot_thresh, cold_thresh=cold_thresh)


    def analyze_rsi(self, historial_data, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs an RSI analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to sell.
            all_data (bool, optional): Defaults to False. If True, we return the RSI associated with each
                data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        rsi_data_generator = lambda rsi_value: self.__threshold_data_generator(rsi_value, hot_thresh=hot_thresh, cold_thresh=cold_thresh)

        period_count = 14

        dataframe = self.__convert_to_dataframe(historial_data)
        rsi_values = abstract.RSI(dataframe, period_count)

        if all_data:
            return [rsi_data_generator(value) for value in rsi_values]
        else:
            return rsi_data_generator(rsi_values.iloc[-1])


    def analyze_sma(self, historial_data, period_count=15, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs a SMA analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our simple moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to sell.
            all_data (bool, optional): Defaults to False. If True, we return the SMA associated with each
                data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        sma_data_generator = lambda sma_value: self.__threshold_data_generator(sma_value, hot_thresh=hot_thresh, cold_thresh=cold_thresh)

        dataframe = self.__convert_to_dataframe(historial_data)
        sma_values = abstract.SMA(dataframe, period_count)

        if all_data:
            return [sma_data_generator(value) for value in sma_values]
        else:
            return sma_data_generator(sma_values.iloc[-1])


    def analyze_ema(self, historial_data, period_count=15, hot_thresh=None, cold_thresh=None, all_data=False):
        """Performs an EMA analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to consider for
                our exponential moving average.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to sell.
            all_data (bool, optional): Defaults to False. If True, we return the EMA associated with each
                data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        ema_data_generator = lambda ema_value: self.__threshold_data_generator(ema_value, hot_thresh=hot_thresh, cold_thresh=cold_thresh)

        dataframe = self.__convert_to_dataframe(historial_data)
        ema_values = abstract.EMA(dataframe, period_count)

        if all_data:
            return [ema_data_generator(value) for value in ema_values]
        else:
            return ema_data_generator(ema_values.iloc[-1])


    def analyze_ichimoku_cloud(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        ic_analyzer = IchimokuCloud()

        tenkansen_period = 9
        kijunsen_period = 26
        senkou_span_b_period = 52
        chikou_span_period = 26

        tenkansen_historical_data = historial_data[-tenkansen_period:]
        kijunsen_historical_data = historial_data[-kijunsen_period:]
        senkou_span_b_historical_data = historial_data[-senkou_span_b_period:]

        tenkan_sen = ic_analyzer.get_tenkansen(tenkansen_historical_data)
        kijun_sen = ic_analyzer.get_kijunsen(kijunsen_historical_data)
        leading_span_a = ic_analyzer.get_senkou_span_a(
            kijunsen_historical_data,
            tenkansen_historical_data
        )

        leading_span_b = ic_analyzer.get_senkou_span_b(senkou_span_b_historical_data)

        ichimoku_data = {
            'values': (tenkan_sen, kijun_sen),
            'is_hot': False,
            'is_cold': False
        }

        return ichimoku_data


    def analyze_bollinger_bands(self, historial_data, all_data=False):
        """Performs a bollinger band analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            all_data (bool, optional): Defaults to False. If True, we return the BB's associated with each
                data point in our historical dataset. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.__convert_to_dataframe(historial_data)
        ntn = np.nan_to_num

        # bb_values[0] = upper band
        # bb_values[1] = middle band (EMA I believe)
        # bb_values[2] = lower band

        bb_data_generator = lambda bb_values: {
            'values': (ntn(bb_values[0]), ntn(bb_values[1]), ntn(bb_values[2])),
            'is_hot': False,
            'is_cold': False
        }

        bollinger_data = abstract.BBANDS(dataframe)

        if all_data:
            return [bb_data_generator((u, m, l)) for u, m, l in zip(bollinger_data['upperband'],
                                    bollinger_data['middleband'], bollinger_data['lowerband'])]
        else:
            return bb_data_generator(bollinger_data.iloc[-1])
