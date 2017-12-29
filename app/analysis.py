"""
Executes the trading strategies and analyzes the results.
"""

from exchange import ExchangeAggregator
from strategies.breakout import Breakout
#from strategies.ichimoku_cloud import IchimokuCloud
from strategies.relative_strength_index import RelativeStrengthIndex
from strategies.moving_averages import MovingAverages


class StrategyAnalyzer():
    """
    Executes the trading strategies and analyzes the results.
    """
    def __init__(self, config):
        self.exchange_aggregator = ExchangeAggregator(config)

    def analyze_breakout(self, coin_pair, period_count=5, time_unit='fiveMin'):
        breakout_analyzer = Breakout()
        historical_data = self.exchange_aggregator.get_historical_data(
            coin_pair=coin_pair,
            period_count=period_count,
            time_unit=time_unit)
        breakout_value, is_breaking_out = breakout_analyzer.find_breakout(historical_data)
        return breakout_value, is_breaking_out

    def analyze_rsi(self, coin_pair, period_count=36, time_unit='thirtyMin'):
        rsi_analyzer = RelativeStrengthIndex()
        historical_data = self.exchange_aggregator.get_historical_data(
            coin_pair=coin_pair,
            period_count=period_count,
            time_unit=time_unit
        )
        rsi_value = rsi_analyzer.find_rsi(historical_data)
        return rsi_value

    def analyze_moving_averages(self, coin_pair, period_count=20, time_unit='fiveMin'):
        ma_analyzer = MovingAverages()
        historical_data = self.exchange_aggregator.get_historical_data(
            coin_pair=coin_pair,
            period_count=period_count,
            time_unit=time_unit
        )
        sma_value = ma_analyzer.calculate_sma(period_count, historical_data)
        ema_value = ma_analyzer.calculate_ema(period_count, historical_data)
        return sma_value, ema_value


