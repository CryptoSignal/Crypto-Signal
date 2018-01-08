"""
Collect required information from exchanges
"""

import time


import ccxt.async as ccxt
import structlog
import asyncio


class ExchangeInterface():
    """
    Collects required information from exchanges
    """
    def __init__(self, exchange_config):
        self.logger = structlog.get_logger()
        self.exchanges = {}

        # Loads the exchanges using ccxt.
        for exchange in exchange_config:
            if exchange_config[exchange]['required']['enabled']:
                new_exchange = getattr(ccxt, exchange)({
                    "enableRateLimit": True # Enables built-in rate limiter
                    })

                # sets up api permissions for user if given
                if new_exchange:
                    if 'key' in exchange_config[exchange]['optional']:
                        new_exchange.apiKey = exchange_config[exchange]['optional']['key']

                    if 'secret' in exchange_config[exchange]['optional']:
                        new_exchange.secret = exchange_config[exchange]['optional'][
                            'secret']

                    if 'username' in exchange_config[exchange]['optional']:
                        new_exchange.username = exchange_config[exchange]['optional'][
                            'username']

                    if 'password' in exchange_config[exchange]['optional']:
                        new_exchange.password = exchange_config[exchange]['optional'][
                            'password']

                    self.exchanges[new_exchange.id] = new_exchange

                else:
                    print("Unable to load exchange %s", new_exchange)


    async def get_historical_data(self, market_pair, exchange, period_count, time_unit):
        """
        Gets historical data for market_pair from exchange for period_count periods of
        interval time_unit.

        Args:
            market_pair: the market who's historical data is to be queried.
            exchange: the exchange that holds the historical data
            time_unit: interval between periods.

        Returns:
            Historical data from market in JSON.
        """

        historical_data = []
        historical_data.append(await self.exchanges[exchange].fetch_ohlcv(
            market_pair,
            timeframe=time_unit,
            limit=period_count))
        return historical_data[0]


    async def get_account_markets(self):
        """
        Get user market balances
        """
        account_markets = {}
        for exchange in self.exchanges:
            account_markets.update(await self.exchanges[exchange].fetch_balance())
            
        return account_markets


    async def get_exchange_markets(self):
        """
        Get exchange markets
        """
        exchange_markets = {}
        for exchange in self.exchanges:
            exchange_markets[exchange] = await self.exchanges[exchange].load_markets()

        return exchange_markets


    async def get_symbol_markets(self, market_pairs):
        """
        Get symbols market in each exchange
        """
        symbol_markets = {}
        for exchange in self.exchanges:
            await self.exchanges[exchange].load_markets()
            symbol_markets[exchange] = {}

            for market_pair in market_pairs:
                symbol_markets[exchange][market_pair] = self.exchanges[exchange].markets[
                    market_pair]

        return symbol_markets

    async def get_order_book(self, market_pair, exchange):
        return await self.exchanges[exchange].fetch_order_book(market_pair)
