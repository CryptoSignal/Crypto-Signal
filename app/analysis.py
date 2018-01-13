"""
Executes the trading strategies and analyzes the results.
"""

import structlog

from datetime import datetime, timedelta, timezone

from strategies.breakout import Breakout
from strategies.ichimoku_cloud import IchimokuCloud
from strategies.moving_averages import MovingAverages
from strategies.relative_strength_index import RelativeStrengthIndex
from strategies.moving_avg_convergence_divergence import MovingAvgConvDiv
from strategies.bollinger_bands import BollingerBands

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

        for data_point in historical_data:
            new_time = data_point[0] / 1000
            the_time = datetime.fromtimestamp(
                new_time
            ).strftime('%c')

        return historical_data


    def analyze_macd(self, historial_data, hot_thresh=0, cold_thresh=0):
        macd_analyzer = MovingAvgConvDiv()

        period_count = 26

        macd_historical_data = historial_data[0:period_count]

        macd_value = macd_analyzer.calculate_MACD_delta(macd_historical_data)

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
        rsi_analyzer = RelativeStrengthIndex()

        period_count = 14

        rsi_historical_data = historial_data[0:period_count]

        rsi_value = rsi_analyzer.get_rsi_value(rsi_historical_data, period_count)

        is_overbought = rsi_value >= cold_thresh
        is_oversold = rsi_value <= hot_thresh

        rsi_data = {
            'values': (rsi_value,),
            'is_cold': is_overbought,
            'is_hot': is_oversold
        }

        return rsi_data


    def analyze_sma(self, historial_data, hot_thresh=0, cold_thresh=0):
        ma_analyzer = MovingAverages()

        period_count = 15

        sma_historical_data = historial_data[0:period_count]

        sma_value = ma_analyzer.get_sma_value(period_count, sma_historical_data)

        is_sma_trending = ma_analyzer.is_sma_trending(sma_value, hot_thresh)

        sma_data = {
            'values': (sma_value,),
            'is_hot': is_sma_trending,
            'is_cold': False
        }

        return sma_data


    def analyze_ema(self, historial_data, hot_thresh=0, cold_thresh=0):
        ma_analyzer = MovingAverages()

        period_count = 15

        ema_historical_data = historial_data[0:period_count]

        ema_value = ma_analyzer.get_ema_value(period_count, ema_historical_data)

        is_ema_trending = ma_analyzer.is_ema_trending(ema_value, hot_thresh)

        ema_data = {
            'values': (ema_value,),
            'is_hot': is_ema_trending,
            'is_cold': False
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
        bollingers = BollingerBands()

        period_count = 21

        bb_historical_data = historial_data[0:period_count]

        upper_band, lower_band = bollingers.get_bollinger_bands(
            bb_historical_data,
            period=period_count,
            k=std_dev
        )

        bb_data = {
            'values': (upper_band, lower_band),
            'is_hot': False,
            'is_cold': False
        }

        return bb_data
