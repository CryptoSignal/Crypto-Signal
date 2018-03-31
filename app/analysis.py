"""Executes the trading strategies and analyzes the results.
"""

import math
from datetime import datetime

import structlog
import pandas
from talib import abstract

from indicators import *

class StrategyAnalyzer():
    """Contains all the methods required for analyzing strategies.
    """

    def __init__(self):
        """Initializes StrategyAnalyzer class """
        self.logger = structlog.get_logger()


    def dispatcher(self):
        """Returns a dictionary for dynamic anaylsis selector

        Returns:
            dict: A dictionary of functions to serve as a dynamic analysis selector.
        """

        dispatcher = {
            'macd': macd.MACD().analyze,
            'macd_sl': macd.MACD().analyze_sl,
            'rsi': rsi.RSI().analyze,
            'sma': sma.SMA().analyze,
            'sma_crossover': sma.SMA().analyze_crossover,
            'ema': ema.EMA().analyze,
            'ema_crossover': ema.EMA().analyze_crossover,
            'ichimoku': ichimoku.Ichimoku().analyze,
            'momentum': momentum.Momentum().analyze,
            'mfi': mfi.MFI().analyze,
            'stoch_rsi': stoch_rsi.StochasticRSI().analyze
        }

        return dispatcher
