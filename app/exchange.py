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
                    self.exchanges[new_exchange.id] = new_exchange
                else:
                    self.logger.error("Unable to load exchange %s", new_exchange)


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
