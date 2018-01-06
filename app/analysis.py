"""
Executes the trading strategies and analyzes the results.
"""

import structlog
from strategies.breakout import Breakout
from strategies.ichimoku_cloud import IchimokuCloud
from strategies.relative_strength_index import RelativeStrengthIndex
from strategies.moving_averages import MovingAverages
from strategies.moving_avg_convergence_divergence import MovingAvgConvDiv
from strategies.bollinger_bands import BollingerBands

class StrategyAnalyzer():
    """
    Executes the trading strategies and analyzes the results.
    """
    def __init__(self, exchange_interface):
        self.exchange_interface = exchange_interface
        self.logger = structlog.get_logger()

    def analyze_macd(self, market_pair, time_unit='1d'):
        macd_analyzer = MovingAvgConvDiv()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=26,
            time_unit=time_unit
        )
        macd_value = macd_analyzer.calculate_MACD_delta(historical_data)
        return macd_value

    def analyze_breakout(self, market_pair, period_count=5, time_unit='5m'):
        breakout_analyzer = Breakout()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=period_count,
            time_unit=time_unit)
        breakout_value, is_breaking_out = breakout_analyzer.find_breakout(historical_data)
        return breakout_value, is_breaking_out

    def analyze_rsi(self, market_pair, period_count=1000, time_unit='1h'):
        rsi_analyzer = RelativeStrengthIndex()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=period_count,
            time_unit=time_unit
        )
        rsi_value = rsi_analyzer.find_rsi(historical_data, period_count)
        return rsi_value

    def analyze_moving_averages(self, market_pair, period_count=20, time_unit='5m'):
        ma_analyzer = MovingAverages()
        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=period_count,
            time_unit=time_unit
        )
        sma_value = ma_analyzer.calculate_sma(period_count, historical_data)
        ema_value = ma_analyzer.calculate_ema(period_count, historical_data)
        return sma_value, ema_value

    def analyze_ichimoku_cloud(self, market_pair):
        ic_analyzer = IchimokuCloud()
        base_line_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=26,
            time_unit='1d'
        )
        conversion_line_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=9,
            time_unit='1d'
        )
        span_b_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=52,
            time_unit='1d'
        )

        leading_span_a = ic_analyzer.calculate_leading_span_a(base_line_data, conversion_line_data)
        leading_span_b = ic_analyzer.calculate_leading_span_b(span_b_data)
        return leading_span_a, leading_span_b

    def analyze_bollinger_bands(self, market_pair, period_count=21, std_dev=2., time_unit='5m'):
        bollingers = BollingerBands()

        historical_data = self.exchange_interface.get_historical_data(
            market_pair=market_pair,
            period_count=period_count,
            time_unit=time_unit
        )

        upper_band, lower_band = bollingers.get_bollinger_bands(historical_data, period=period_count, k=std_dev)
        return upper_band, lower_band

