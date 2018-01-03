"""
Collect required information from exchanges
"""

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

    def get_historical_data(self, market_pair, period_count, time_unit):
        """
        Get history data
        """
        historical_data = []
        for exchange in self.exchanges:
            historical_data.append(exchange.fetch_ohlcv(
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
            account_markets.update(exchange.fetch_balance())
        return account_markets

    def get_exchange_markets(self):
        """
        Get exchange markets
        """
        exchange_markets = {}
        for exchange in self.exchanges:
            exchange_markets[exchange.id] = exchange.load_markets()
        return exchange_markets

    def get_symbol_markets(self, symbol_pairs):
        """
        Get symbols market in each exchange
        """
        symbol_markets = {}
        for exchange in self.exchanges:
            exchange.load_markets()
            symbol_markets[exchange.id] = {}
            for symbol_pair in symbol_pairs:
                symbol_markets[exchange.id][symbol_pair] = exchange.markets[symbol_pair]
        return symbol_markets
