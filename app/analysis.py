"""
Executes the trading strategies and analyzes the results.
"""

import structlog
from strategies.breakout import Breakout
from strategies.ichimoku_cloud import IchimokuCloud
from strategies.relative_strength_index import RelativeStrengthIndex
from strategies.moving_averages import MovingAverages

class StrategyAnalyzer():
    """
    Executes the trading strategies and analyzes the results.
    """
    def __init__(self, exchange_interface):
        self.exchange_interface = exchange_interface
        self.logger = structlog.get_logger()

    def analyze_breakout(self, market_pair, exchange, breakout_threshold=0.75, period_count=5, time_unit='5m'):
        breakout_analyzer = Breakout()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit)
        breakout_value = breakout_analyzer.get_breakout_value(historical_data)
        is_breaking_out = breakout_analyzer.is_breaking_out(breakout_value, breakout_threshold)
        breakout_data = {'value': breakout_value, 'is_breaking_out': is_breaking_out}
        return breakout_data

    def analyze_rsi(self, market_pair, exchange, overbought_threshold=0, oversold_threshold=0, period_count=1000, time_unit='1h'):
        rsi_analyzer = RelativeStrengthIndex()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )
        rsi_value = rsi_analyzer.get_rsi_value(historical_data, period_count)
        is_overbought = rsi_analyzer.is_overbought(rsi_value, overbought_threshold)
        is_oversold = rsi_analyzer.is_oversold(rsi_value, oversold_threshold)
        rsi_data = {'value': rsi_value, 'is_overbought': is_overbought, 'is_oversold': is_oversold}
        return rsi_data

    def analyze_moving_averages(self, market_pair, exchange, sma_threshold=0, ema_threshold=0, period_count=20, time_unit='5m'):
        ma_analyzer = MovingAverages()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=time_unit
        )
        sma_value = ma_analyzer.get_sma_value(period_count, historical_data)
        ema_value = ma_analyzer.get_ema_value(period_count, historical_data)
        is_sma_trending = ma_analyzer.is_sma_trending(sma_value, sma_threshold)
        is_ema_trending = ma_analyzer.is_ema_trending(ema_value, ema_threshold)
        ma_data = {'sma_value': sma_value, 'ema_value': ema_value, 'is_sma_trending': is_sma_trending, 'is_ema_trending': is_ema_trending}
        return ma_data

    def analyze_ichimoku_cloud(self, market_pair, exchange, ichimoku_threshold=0):
        ic_analyzer = IchimokuCloud()
        base_line_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=26,
            time_unit='1d'
        )
        conversion_line_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=9,
            time_unit='1d'
        )
        span_b_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=52,
            time_unit='1d'
        )

        leading_span_a = ic_analyzer.get_leading_span_a(base_line_data, conversion_line_data)
        leading_span_b = ic_analyzer.get_leading_span_b(span_b_data)
        is_ichimoku_trending = ic_analyzer.is_ichimoku_trending(ichimoku_threshold)

        ichimoku_data = {'span_a_value': leading_span_a, 'span_b_value': leading_span_b, 'is_ichimoku_trending': is_ichimoku_trending}
        return ichimoku_data
