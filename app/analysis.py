"""Executes the trading strategies and analyzes the results.
"""

import math
from datetime import datetime

import structlog
import pandas
from talib import abstract

from analyzers.indicators import *
from analyzers.informants import *
from analyzers import *

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
            'stoch_rsi': stoch_rsi.StochasticRSI().analyze,
            'obv': obv.OBV().analyze
        }

        return dispatcher


    def informant_dispatcher(self):
        """Returns a dictionary for dynamic informant selector

        Returns:
            dictionary: A dictionary of functions to serve as a dynamic informant selector.
        """

        dispatcher = {
            'sma': sma.SMA().analyze,
            'ema': ema.EMA().analyze,
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
