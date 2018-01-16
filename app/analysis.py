"""Executes the trading strategies and analyzes the results.
"""

from datetime import datetime, timedelta, timezone

import structlog
import pandas
from talib import abstract
from stockstats import StockDataFrame

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


    def __convert_to_dataframe(self, historical_data):
        """Converts historical data matrix to a pandas dataframe.

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            pandas.DataFrame: Contains the historical data in a pandas dataframe.
        """

        dataframe = pandas.DataFrame(historical_data)
        dataframe.transpose()
        dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        dataframe['datetime'] = dataframe.timestamp.apply(
            lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )
        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)
        return dataframe


    def analyze_macd(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs a macd analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.__convert_to_dataframe(historial_data)
        macd_value = abstract.MACD(dataframe).iloc[-1, 0]

        macd_data = {
            'values': (macd_value,),
            'is_hot': False,
            'is_cold': False
        }

        return macd_data


    def analyze_breakout(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs a momentum analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        breakout_analyzer = Breakout()

        period_count = 5

        breakout_historical_data = historial_data[0:period_count]

        breakout_value = breakout_analyzer.get_breakout_value(breakout_historical_data)

        is_breaking_out = False
        if not hot_thresh is None:
            is_breaking_out = breakout_value >= hot_thresh

        is_cooling_off = False
        if not cold_thresh is None:
            is_cooling_off = breakout_value <= cold_thresh

        breakout_data = {
            'values': (breakout_value,),
            'is_hot': is_breaking_out,
            'is_cold': is_cooling_off
        }

        return breakout_data


    def analyze_rsi(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs an RSI analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        period_count = 14

        dataframe = self.__convert_to_dataframe(historial_data)
        rsi_value = abstract.RSI(dataframe, period_count).iloc[-1]

        is_hot = False
        if not hot_thresh is None:
            is_hot = rsi_value <= hot_thresh

        is_cold = False
        if not cold_thresh is None:
            is_cold = rsi_value >= cold_thresh


        rsi_data = {
            'values': (rsi_value,),
            'is_cold': is_cold,
            'is_hot': is_hot
        }

        return rsi_data


    def analyze_sma(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs a SMA analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        period_count = 15

        dataframe = self.__convert_to_dataframe(historial_data)
        sma_value = abstract.SMA(dataframe, period_count).iloc[-1]

        is_hot = False
        if not hot_thresh is None:
            is_hot = sma_value >= hot_thresh

        is_cold = False
        if not cold_thresh is None:
            is_cold = sma_value <= cold_thresh

        sma_data = {
            'values': (sma_value,),
            'is_hot': is_hot,
            'is_cold': is_cold
        }

        return sma_data


    def analyze_ema(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs an EMA analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to sell.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        period_count = 15

        dataframe = self.__convert_to_dataframe(historial_data)
        ema_value = abstract.EMA(dataframe, period_count).iloc[-1]

        is_hot = False
        if not hot_thresh is None:
            is_hot = ema_value >= hot_thresh

        is_cold = False
        if not cold_thresh is None:
            is_cold = ema_value <= cold_thresh

        ema_data = {
            'values': (ema_value,),
            'is_hot': is_hot,
            'is_cold': is_cold
        }

        return ema_data


    def analyze_ichimoku_cloud(self, historial_data, hot_thresh=None, cold_thresh=None):
        """Performs an ichimoku cloud analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.
            hot_thresh (float, optional): Defaults to 0. The threshold at which this might be good
                to purchase.
            cold_thresh (float, optional): Defaults to 0. The threshold at which this might be good
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

        tankensen_historical_data = historial_data[0:tenkansen_period]
        kijunsen_historical_data = historial_data[0:kijunsen_period]
        senkou_span_b_historical_data = historial_data[0:senkou_span_b_period]

        leading_span_a = ic_analyzer.get_senkou_span_a(
            kijunsen_historical_data,
            tankensen_historical_data
        )

        leading_span_b = ic_analyzer.get_senkou_span_b(senkou_span_b_historical_data)

        ichimoku_data = {
            'values': (leading_span_a, leading_span_b),
            'is_hot': False,
            'is_cold': False
        }

        return ichimoku_data


    def analyze_bollinger_bands(self, historial_data):
        """Performs a bollinger band analysis on the historical data

        Args:
            historial_data (list): A matrix of historical OHCLV data.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        dataframe = self.__convert_to_dataframe(historial_data)
        upper_band, middle_band, lower_band = abstract.BBANDS(dataframe).iloc[-1]

        bb_data = {
            'values': (upper_band, middle_band, lower_band),
            'is_hot': False,
            'is_cold': False
        }

        return bb_data
