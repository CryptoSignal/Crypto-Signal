"""
Collect required information from exchanges
"""

import time

import ccxt
import structlog

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


    def get_historical_data(self, market_pair, exchange, time_unit, start_date):
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
        historical_data.append(
            self.exchanges[exchange].fetch_ohlcv(
                market_pair,
                timeframe=time_unit,
                since=start_date
            )
        )
        time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return historical_data[0]


    def get_account_markets(self, exchange):
        """
        Get user market balances
        """
        account_markets = {}
        account_markets.update(self.exchanges[exchange].fetch_balance())
        time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return account_markets


    def get_exchange_markets(self):
        """
        Get exchange markets
        """
        exchange_markets = {}
        for exchange in self.exchanges:
            exchange_markets[exchange] = self.exchanges[exchange].load_markets()
            time.sleep(self.exchanges[exchange].rateLimit / 1000)
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
                symbol_markets[exchange][market_pair] = self.exchanges[exchange].markets[
                    market_pair]
            time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return symbol_markets

    def get_order_book(self, market_pair, exchange):
        return self.exchanges[exchange].fetch_order_book(market_pair)

    def get_open_orders(self):
        open_orders = {}
        for exchange in self.exchanges:
            open_orders[exchange] = self.exchanges[exchange].fetch_open_orders()
            time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return open_orders

    def cancel_order(self, exchange, order_id):
        self.exchanges[exchange].cancel_order(order_id)
        time.sleep(self.exchanges[exchange].rateLimit / 1000)

    def get_quote_symbols(self, exchange):
        quote_symbols = []
        for market_pair in self.exchanges[exchange].markets:
            base_symbol, quote_symbol = market_pair.split('/')
            if not quote_symbol in quote_symbols:
                quote_symbols.append(quote_symbol)

        return quote_symbols
