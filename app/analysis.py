"""
Executes the trading strategies and analyzes the results.
"""

from datetime import datetime, timedelta, timezone

import structlog
import pandas
from stockstats import StockDataFrame

from strategies.breakout import Breakout
from strategies.ichimoku_cloud import IchimokuCloud

class StrategyAnalyzer():
    """
    Handles trading strategies for breakouts, rsi, moving averages,
    and ichimoku clouds. All methods are asynchronous.

    Attributes:
       _exchange_interface: asynchronous interface used to communicate with exchanges.
    """

    def __init__(self, exchange_interface):
        self.__exchange_interface = exchange_interface
        self.logger = structlog.get_logger()
        self.day_historical_data = []
        self.minute_historical_data = []


    def get_historical_data(self, market_pair, exchange, time_unit, max_days=100):
        # The data_start_date timestamp must be in milliseconds hence * 1000.
        data_start_date = datetime.now() - timedelta(days=max_days)
        data_start_date = data_start_date.replace(tzinfo=timezone.utc).timestamp() * 1000
        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            time_unit=time_unit,
            start_date=data_start_date
        )

        return historical_data

    def __convert_to_dataframe(self, historical_data):
        dataframe = pandas.DataFrame(historical_data)
        dataframe.transpose()
        dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        dataframe['datetime'] = dataframe.timestamp.apply(
            lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )
        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)
        return dataframe


    def analyze_macd(self, historial_data, hot_thresh=0, cold_thresh=0):

        dataframe = self.__convert_to_dataframe(historial_data)
        stock_dataframe = StockDataFrame.retype(dataframe)
        macd_value = stock_dataframe.get('macd').iloc[-1]

        macd_data = {
            'values': (macd_value,),
            'is_hot': False,
            'is_cold': False
        }

        return macd_data


    def analyze_breakout(self, historial_data, hot_thresh=0, cold_thresh=0):
        breakout_analyzer = Breakout()

        period_count = 5

        breakout_historical_data = historial_data[0:period_count]

        breakout_value = breakout_analyzer.get_breakout_value(breakout_historical_data)
        is_breaking_out = breakout_value >= hot_thresh

        breakout_data = {
            'values': (breakout_value,),
            'is_hot': is_breaking_out,
            'is_cold': False
        }

        return breakout_data


    def analyze_rsi(self, historial_data, hot_thresh=0, cold_thresh=0):
        period_count = 14

        dataframe = self.__convert_to_dataframe(historial_data)
        stock_dataframe = StockDataFrame.retype(dataframe)
        rsi_method = 'rsi_' + str(period_count)
        rsi_value = stock_dataframe.get(rsi_method).iloc[-1]

        is_cold = rsi_value >= cold_thresh
        is_hot = rsi_value <= hot_thresh

        rsi_data = {
            'values': (rsi_value,),
            'is_cold': is_cold,
            'is_hot': is_hot
        }

        return rsi_data


    def analyze_sma(self, historial_data, hot_thresh=0, cold_thresh=0):
        period_count = 15

        dataframe = self.__convert_to_dataframe(historial_data)
        stock_dataframe = StockDataFrame.retype(dataframe)
        sma_method = 'close_' + str(period_count) + '_sma'
        sma_value = stock_dataframe.get(sma_method).iloc[-1]

        is_hot = sma_value >= hot_thresh
        is_cold = sma_value <= cold_thresh

        sma_data = {
            'values': (sma_value,),
            'is_hot': is_hot,
            'is_cold': is_cold
        }

        return sma_data


    def analyze_ema(self, historial_data, hot_thresh=0, cold_thresh=0):
        period_count = 15

        dataframe = self.__convert_to_dataframe(historial_data)
        stock_dataframe = StockDataFrame.retype(dataframe)
        ema_method = 'close_' + str(period_count) + '_ema'
        ema_value = stock_dataframe.get(ema_method).iloc[-1]

        is_hot = ema_value >= hot_thresh
        is_cold = ema_value <= cold_thresh

        ema_data = {
            'values': (ema_value,),
            'is_hot': is_hot,
            'is_cold': is_cold
        }

        return ema_data


    def analyze_ichimoku_cloud(self, historial_data, hot_thresh=0, cold_thresh=0):
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


    def analyze_bollinger_bands(self, historial_data, std_dev=2.):
        period_count = 21

        dataframe = self.__convert_to_dataframe(historial_data)
        stock_dataframe = StockDataFrame.retype(dataframe)
        upper_band = stock_dataframe.get('boll_ub').iloc[-1]
        lower_band = stock_dataframe.get('boll_lb').iloc[-1]

        bb_data = {
            'values': (upper_band, lower_band),
            'is_hot': False,
            'is_cold': False
        }

        return bb_data
