"""
Collect required information from exchanges
"""

import distutils.util

import structlog
import ccxt

class ExchangeInterface():
    """
    Collect required information from exchanges
    """
    def __init__(self, exchange_config):
        self.logger = structlog.get_logger()
        self.exchanges = []
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
                    self.exchanges.append(new_exchange)
                else:
                    print("Unable to load exchange %s", new_exchange)

    def get_historical_data(self, coin_pair, period_count, time_unit):
        """
        Get history data
        """
        historical_data = []
        for exchange in self.exchanges:
            historical_data.append(exchange.fetch_ohlcv(
                coin_pair,
                timeframe=time_unit,
                limit=period_count))
        return historical_data[0]

    def get_user_markets(self):
        """
        Get user market balances
        """
        user_markets = {}
        for exchange in self.exchanges:
            user_markets.update(exchange.fetch_balance())
        return user_markets
