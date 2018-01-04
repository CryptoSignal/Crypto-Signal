"""
Collect required information from exchanges
"""

import time

import structlog
import ccxt

class ExchangeInterface():
    """
    Collect required information from exchanges
    """
    def __init__(self, exchange_config):
        self.logger = structlog.get_logger()
        self.exchanges = {}
        for exchange in exchange_config:
            if exchange_config[exchange]['required']['enabled']:
                new_exchange = getattr(ccxt, exchange)()
                if new_exchange:
                    if 'key' in exchange_config[exchange]['optional']:
                        new_exchange.apiKey = exchange_config[exchange]['optional']['key']
                    if 'secret' in exchange_config[exchange]['optional']:
                        new_exchange.secret = exchange_config[exchange]['optional']['secret']
                    if 'username' in exchange_config[exchange]['optional']:
                        new_exchange.username = exchange_config[exchange]['optional']['username']
                    if 'password' in exchange_config[exchange]['optional']:
                        new_exchange.password = exchange_config[exchange]['optional']['password']
                    self.exchanges[new_exchange.id] = new_exchange
                else:
                    print("Unable to load exchange %s", new_exchange)

    def get_historical_data(self, market_pair, exchange, period_count, time_unit):
        """
        Get history data
        """
        historical_data = []
        historical_data.append(self.exchanges[exchange].fetch_ohlcv(
            market_pair,
            timeframe=time_unit,
            limit=period_count))
        return historical_data[0]

    def get_account_markets(self):
        """
        Get user market balances
        """
        account_markets = {}
        for exchange in self.exchanges:
            account_markets.update(self.exchanges[exchange].fetch_balance())
        return account_markets

    def get_exchange_markets(self):
        """
        Get exchange markets
        """
        exchange_markets = {}
        for exchange in self.exchanges:
            exchange_markets[exchange] = self.exchanges[exchange].load_markets()
        return exchange_markets

    def get_symbol_markets(self, market_pairs):
        """
        Get symbols market in each exchange
        """
        symbol_markets = {}
        for exchange in self.exchanges:
            self.exchanges[exchange].load_markets()
            symbol_markets[exchange] = {}
            for market_pair in market_pairs:
                symbol_markets[exchange][market_pair] = self.exchanges[exchange].markets[market_pair]
        return symbol_markets
