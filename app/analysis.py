"""
Executes the trading strategies and analyzes the results.
"""

import asyncio

import structlog

from strategies.breakout import Breakout
from strategies.ichimoku_cloud import IchimokuCloud
from strategies.moving_averages import MovingAverages
from strategies.relative_strength_index import RelativeStrengthIndex


class StrategyAnalyzer():
    """
    Handles trading strategies for breakouts, rsi, moving averages, 
    and ichimoku clouds. All methods are asynchronous.

    Attributes:
       _exchange_interface: asynchronous interface used to communicate with exchanges. 
    """
    def __init__(self, exchange_interface, config):
        self.__exchange_interface = exchange_interface
        self.logger = structlog.get_logger()
        self.config = config

        self.ma_config = self.config["moving_averages"]
        self.break_config = self.config["breakout"]
        self.rsi_config = self.config["rsi"]
        self.ichimoku_config = self.config["ichimoku_cloud"]


    async def analyze_breakout(self, market_pair, exchange):

        breakout_analyzer = Breakout()

        historical_data = await self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=self.break_config['period_count'],
            time_unit=self.break_config['time_unit'])

        breakout_value = breakout_analyzer.get_breakout_value(historical_data)
        is_breaking_out = breakout_value >= self.break_config["breakout_threshold"]

        breakout_data = {
            'value': breakout_value, 
            'is_breaking_out': is_breaking_out
            }

        return breakout_data


    async def analyze_rsi(self, market_pair, exchange):

        rsi_analyzer = RelativeStrengthIndex()

        historical_data = await self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=self.rsi_config['period_count'],
            time_unit=self.rsi_config['time_unit']
        )

        rsi_value = rsi_analyzer.get_rsi_value(historical_data, self.rsi_config['period_count'])

        is_overbought = rsi_value >= self.rsi_config['overbought']
        is_oversold = rsi_value <= self.rsi_config['oversold']

        rsi_data = {
            'value': rsi_value, 
            'is_overbought': is_overbought, 
            'is_oversold': is_oversold
            }

        return rsi_data


    async def analyze_moving_averages(self, market_pair, exchange):

        ma_analyzer = MovingAverages()


        period_count = self.ma_config["period_count"]
        historical_data = await self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=period_count,
            time_unit=self.ma_config["time_unit"]
        )

        sma_value = ma_analyzer.get_sma_value(period_count, historical_data)
        ema_value = ma_analyzer.get_ema_value(period_count, historical_data)

        is_sma_trending = ma_analyzer.is_sma_trending(sma_value, self.ma_config["sma_threshold"])
        is_ema_trending = ma_analyzer.is_ema_trending(ema_value, self.ma_config["ema_threshold"])

        ma_data = {
            'sma_value': sma_value, 
            'ema_value': ema_value, 
            'is_sma_trending': is_sma_trending, 
            'is_ema_trending': is_ema_trending
            }

        return ma_data


    async def analyze_ichimoku_cloud(self, market_pair, exchange, ichimoku_threshold=0):
        ic_analyzer = IchimokuCloud()

        span_b_periods = self.ichimoku_config['span_b']['period_count']
        base_line_periods = self.ichimoku_config['base_line']['period_count']
        conversion_line_periods = self.ichimoku_config['conversion_line']['period_count']

        max_period_count = max(
            span_b_periods,
            base_line_periods,
            conversion_line_periods
        )

        history = await self.__exchange_interface.get_historical_data(
            market_pair=market_pair,
            exchange=exchange,
            period_count=max_period_count,
            time_unit=self.ichimoku_config['time_unit']
        )

        base_line_data = history[0:base_line_periods]
        conversion_line_data = history[0:conversion_line_periods]
        span_b_data = history[0:span_b_periods]

        leading_span_a = ic_analyzer.get_leading_span_a(base_line_data, conversion_line_data)
        leading_span_b = ic_analyzer.get_leading_span_b(span_b_data)
        is_ichimoku_trending = ic_analyzer.is_ichimoku_trending(self.ichimoku_config["ichimoku_threshold"])

        ichimoku_data = {
            'span_a_value': leading_span_a, 
            'span_b_value': leading_span_b, 
            'is_ichimoku_trending': is_ichimoku_trending
            }
        
        return ichimoku_data


    async def analyze_all(self, market_pair, exchange):
        ichimoku_data = self.analyze_ichimoku_cloud(self, market_pair, exchange)

        # Moving averages and breakout both use 5 mins.
        history = await self.__exchange_interface.get_historical_data() 
