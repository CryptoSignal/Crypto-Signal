"""Interface for performing queries against exchange API's
"""

import time
from datetime import datetime, timedelta, timezone

import ccxt
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt

class ExchangeInterface():
    """Interface for performing queries against exchange API's
    """

    def __init__(self, exchange_config):
        """Initializes ExchangeInterface class

        Args:
            exchange_config (dict): A dictionary containing configuration for the exchanges.
        """

        self.logger = structlog.get_logger()
        self.exchanges = {}

        # Loads the exchanges using ccxt.
        for exchange in exchange_config:
            if exchange_config[exchange]['required']['enabled']:
                new_exchange = getattr(ccxt, exchange)({
                    "enableRateLimit": True
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
                    self.logger.warn("Unable to load exchange %s", new_exchange)


    def override_exchange_config(self):
        """Enables all exchanges regardless of user configuration. Useful for the UI layer.
        """

        for exchange in ccxt.exchanges:
            self.exchanges[exchange] = getattr(ccxt, exchange)({
                "enableRateLimit": True
            })


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_historical_data(self, market_pair, exchange, time_unit, start_date=None, max_days=100):
        """Get historical OHLCV for a symbol pair

        Decorators:
            retry

        Args:
            market_pair (str): Contains the symbol pair to operate on i.e. BURST/BTC
            exchange (str): Contains the exchange to fetch the historical data from.
            time_unit (str): A string specifying the ccxt time unit i.e. 5m or 1d.
            start_date (int, optional): Timestamp in milliseconds.
            max_days (int, optional): Defaults to 100. Maximum number of days to fetch data for
                if start date is not specified.

        Returns:
            list: Contains a list of lists which contain timestamp, open, high, low, close, volume.
        """

        if not start_date:
            max_days_date = datetime.now() - timedelta(days=max_days)
            start_date = int(max_days_date.replace(tzinfo=timezone.utc).timestamp() * 1000)

        historical_data = self.exchanges[exchange].fetch_ohlcv(
            market_pair,
            timeframe=time_unit,
            since=start_date
        )

        time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return historical_data


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_account_markets(self, exchange):
        """Get the symbol pairs listed within a users account.

        Decorators:
            retry

        Args:
            exchange (str): Contains the exchange to fetch the data from.

        Returns:
            dict: A dictionary containing market data for the symbol pairs.
        """

        account_markets = {}
        account_markets.update(self.exchanges[exchange].fetch_balance())
        time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return account_markets


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_markets_for_exchange(self, exchange):
        """Get market data for all symbol pairs listed on the given exchange.

        Decorators:
            retry

        Args:
            exchange (str): Contains the exchange to fetch the data from

        Returns:
            dict: A dictionary containing market data for all symbol pairs.
        """

        exchange_markets = self.exchanges[exchange].load_markets()

        return exchange_markets


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_exchange_markets(self):
        """Get market data for all symbol pairs listed on all configured exchanges.

        Decorators:
            retry

        Returns:
            dict: A dictionary containing market data for all symbol pairs.
        """

        exchange_markets = {}
        for exchange in self.exchanges:
            exchange_markets[exchange] = self.exchanges[exchange].load_markets()
            time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return exchange_markets


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_symbol_markets(self, market_pairs):
        """Get market data for specific symbols on all configured exchanges.

        Decorators:
            retry

        Args:
            market_pairs (list): The symbol pairs you want to retrieve market data for.

        Returns:
            dict: A dictionary containing market data for requested symbol pairs.
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


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_order_book(self, market_pair, exchange):
        """Retrieve the order information for a particular symbol pair.

        Decorators:
            retry

        Args:
            market_pair (str): Contains the symbol pair to operate on i.e. BURST/BTC
            exchange (str): Contains the exchange to fetch the data from.

        Returns:
            dict: A dictionary containing bid, ask and other order information on a pair.
        """

        return self.exchanges[exchange].fetch_order_book(market_pair)


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_open_orders(self):
        """Get the users currently open orders on all configured exchanges.

        Decorators:
            retry

        Returns:
            dict: A dictionary containing open order information.
        """

        open_orders = {}
        for exchange in self.exchanges:
            open_orders[exchange] = self.exchanges[exchange].fetch_open_orders()
            time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return open_orders


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def cancel_order(self, exchange, order_id):
        """Cancels an open order on a particular exchange.

        Decorators:
            retry

        Args:
            exchange (str): Contains the exchange to cancel the order on.
            order_id (str): The order id you want to cancel.
        """

        self.exchanges[exchange].cancel_order(order_id)
        time.sleep(self.exchanges[exchange].rateLimit / 1000)


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_quote_symbols(self, exchange):
        """Get a list of quote symbols on an exchange.

        Decorators:
            retry

        Args:
            exchange (str): Contains the exchange to fetch the data from.

        Returns:
            list: List of quote symbols on an exchange.
        """

        quote_symbols = []
        for market_pair in self.exchanges[exchange].markets:
            _, quote_symbol = market_pair.split('/')
            if not quote_symbol in quote_symbols:
                quote_symbols.append(quote_symbol)

        return quote_symbols


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_btc_value(self, exchange, base_symbol, volume):
        """Returns the BTC value of a symbol

        Decorators:
            retry

        Args:
            exchange (str): The name / exchange id of the exchange to query.
            base_symbol (str): The symbol you want the BTC value of.
            volume (float): A number indicating how much of a symbol you have.

        Returns:
            float: The BTC value of the symbol given volume.
        """

        btc_value = 0
        try:
            market_pair = base_symbol + "/BTC"

            order_book = self.get_order_book(market_pair, exchange)
            bid = order_book['bids'][0][0] if order_book['bids'] else None
            if bid:
                btc_value = bid * volume
        except ccxt.ExchangeError:
            market_pair = "BTC/" + base_symbol

            order_book = self.get_order_book(market_pair, exchange)
            ask = order_book['asks'][0][0] if order_book['asks'] else None
            if ask:
                btc_value = volume / ask

        return btc_value


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_btc_volume(self, exchange, base_symbol):
        """Get the volume of BTC exchange for a given symbol in a given period.

        Decorators:
            retry

        Args:
            exchange (str): The name / exchange id of the exchange to query.
            base_symbol (str): The symbol you want the BTC volume of.

        Returns:
            float: The total volume for queried period.
        """

        market_pair = base_symbol + "/BTC"
        ticker = self.exchanges[exchange].fetch_ticker(market_pair)
        btc_volume = ticker['quoteVolume']

        return btc_volume
