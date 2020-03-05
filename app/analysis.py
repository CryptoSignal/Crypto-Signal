"""Executes the trading strategies and analyzes the results.
"""

import structlog

from analyzers.informants import *
from analyzers import *

from analyzers.indicators import ichimoku, macd, rsi, momentum, mfi, adx, plus_di, minus_di, stoch_rsi, obv, kdj, td, valley_loc


class StrategyAnalyzer():
    """Contains all the methods required for analyzing strategies.
    """

    def __init__(self):
        """Initializes StrategyAnalyzer class """
        self.logger = structlog.get_logger()


    def indicator_dispatcher(self):
        """Returns a dictionary for dynamic anaylsis selector

        Returns:
            dictionary: A dictionary of functions to serve as a dynamic analysis selector.
        """

        dispatcher = {
            'ichimoku': ichimoku.Ichimoku().analyze,
            'macd': macd.MACD().analyze,
            'rsi': rsi.RSI().analyze,
            'momentum': momentum.Momentum().analyze,
            'mfi': mfi.MFI().analyze,
            'adx': adx.ADX().analyze,
            'plus_di': plus_di.PLUS_DI().analyze,
            'minus_di': minus_di.MINUS_DI().analyze,
            'stoch_rsi': stoch_rsi.StochasticRSI().analyze,
            'obv': obv.OBV().analyze,
            'kdj': kdj.KDJ().analyze,
            'td': td.TD().analyze
            # 'peak_loc': peak_loc.Peak_Loc().analyze,
            # 'valley_loc': valley_loc.Valley_Loc().analyze
        }

        return dispatcher


    def informant_dispatcher(self):
        """Returns a dictionary for dynamic informant selector

        Returns:
            dictionary: A dictionary of functions to serve as a dynamic informant selector.
        """

        dispatcher = {
            'sma': sma.SMA().analyze,
            'ema7': ema.EMA().analyze,
            'ema22': ema.EMA().analyze,
            'ema33': ema.EMA().analyze,
            'ema65': ema.EMA().analyze,
            'ema120': ema.EMA().analyze,
            'ema365': ema.EMA().analyze,
            'vwap': vwap.VWAP().analyze,
            'bollinger_bands': bollinger_bands.Bollinger().analyze,
            'ohlcv': ohlcv.OHLCV().analyze
        }

        return dispatcher


    def crossover_dispatcher(self):
        """Returns a pandas.DataFrame for dynamic crossover selector

        Returns:
            dictionary: A dictionary of functions to serve as a dynamic crossover selector.
        """

        dispatcher = {
            'std_crossover': crossover.CrossOver().analyze
        }

        return dispatcher
