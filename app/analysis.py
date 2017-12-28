"""
Executes the trading strategies and analyzes the results.
"""

from strategies.breakout import Breakout
#from strategies.ichimoku_cloud import IchimokuCloud
#from strategies.relative_string_index import RelativeStrengthIndex
#from strategies.moving_averages import MovingAverages


class StrategyAnalyzer():
    """
    Executes the trading strategies and analyzes the results.
    """
    def analyze_breakout(self, historical_data):
        breakout_analyzer = Breakout()
        breakout_value, is_breaking_out = breakout_analyzer.find_breakout(historical_data)
        return breakout_value, is_breaking_out
