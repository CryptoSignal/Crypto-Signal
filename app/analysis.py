"""
Executes the trading strategies and analyzes the results.
"""



import structlog

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


    def analyze_macd(self, market_pair, exchange, time_unit='1d',
                     period_count=26, hot_thresh=0, cold_thresh=0):

        macd_analyzer = MovingAvgConvDiv()
        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )

        macd_value = macd_analyzer.calculate_MACD_delta(historical_data)

        macd_data = {
            'values': (macd_value,),
            'is_hot': False,
            'is_cold': False
        }

        return macd_data


    def analyze_breakout(self, market_pair, exchange, time_unit='5m',
                         period_count=5, hot_thresh=0, cold_thresh=0):

        breakout_analyzer = Breakout()
        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit)

        breakout_value = breakout_analyzer.get_breakout_value(historical_data)
        is_breaking_out = breakout_value >= hot_thresh

        breakout_data = {
            'values': (breakout_value,),
            'is_hot': is_breaking_out,
            'is_cold': False
        }

        return breakout_data


    def analyze_rsi(self, market_pair, exchange, time_unit='1h',
                    period_count=1000, hot_thresh=0, cold_thresh=0):

        rsi_analyzer = RelativeStrengthIndex()
        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )

        rsi_value = rsi_analyzer.get_rsi_value(historical_data, period_count)

        is_overbought = rsi_value >= cold_thresh
        is_oversold = rsi_value <= hot_thresh

        rsi_data = {
            'values': (rsi_value,),
            'is_cold': is_overbought,
            'is_hot': is_oversold
        }

        return rsi_data


    def analyze_sma(self, market_pair, exchange, time_unit='5m',
                    period_count=20, hot_thresh=0, cold_thresh=0):

        ma_analyzer = MovingAverages()

        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )

        sma_value = ma_analyzer.get_sma_value(period_count, historical_data)

        is_sma_trending = ma_analyzer.is_sma_trending(sma_value, hot_thresh)

        sma_data = {
            'values': (sma_value,),
            'is_hot': is_sma_trending,
            'is_cold': False
        }

        return sma_data


    def analyze_ema(self, market_pair, exchange, time_unit='5m',
                    period_count=20, hot_thresh=0, cold_thresh=0):

        ma_analyzer = MovingAverages()

        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )

        ema_value = ma_analyzer.get_ema_value(period_count, historical_data)

        is_ema_trending = ma_analyzer.is_ema_trending(ema_value, hot_thresh)

        ema_data = {
            'values': (ema_value,),
            'is_hot': is_ema_trending,
            'is_cold': False
        }

        return ema_data


    def analyze_ichimoku_cloud(self, market_pair, exchange, time_unit='1d',
                               period_count=(26, 9, 52), hot_thresh=0, cold_thresh=0):

        ic_analyzer = IchimokuCloud()

        span_b_periods = period_count[2]
        base_line_periods = period_count[0]
        conversion_line_periods = period_count[1]

        max_period_count = max(
            span_b_periods,
            base_line_periods,
            conversion_line_periods
        )

        history = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=max_period_count,
            time_unit=time_unit
        )

        base_line_data = history[0:base_line_periods]
        conversion_line_data = history[0:conversion_line_periods]
        span_b_data = history[0:span_b_periods]

        leading_span_a = ic_analyzer.get_leading_span_a(base_line_data, conversion_line_data)
        leading_span_b = ic_analyzer.get_leading_span_b(span_b_data)
        is_ichimoku_trending = ic_analyzer.is_ichimoku_trending(hot_thresh)

        ichimoku_data = {
            'values': (leading_span_a, leading_span_b),
            'is_hot': is_ichimoku_trending,
            'is_cold': False
        }

        return ichimoku_data


    def analyze_bollinger_bands(self, market_pair, exchange, time_unit='1d',
                                period_count=20, std_dev=2.):

        bollingers = BollingerBands()

        historical_data = self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )

        upper_band, lower_band = bollingers.get_bollinger_bands(
            historical_data, period=period_count, k=std_dev
        )

        bb_data = {
            'values': (upper_band, lower_band),
            'is_hot': False,
            'is_cold': False
        }

        return bb_data
