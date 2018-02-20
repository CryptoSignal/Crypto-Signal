"""Interface for performing queries against exchange API's
"""

import re
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
    def get_historical_data(self, market_pair, exchange, time_unit, start_date=None, max_periods=100):
        """Get historical OHLCV for a symbol pair

        Decorators:
            retry

        Args:
            market_pair (str): Contains the symbol pair to operate on i.e. BURST/BTC
            exchange (str): Contains the exchange to fetch the historical data from.
            time_unit (str): A string specifying the ccxt time unit i.e. 5m or 1d.
            start_date (int, optional): Timestamp in milliseconds.
            max_periods (int, optional): Defaults to 100. Maximum number of time periods
              back to fetch data for.

        Returns:
            list: Contains a list of lists which contain timestamp, open, high, low, close, volume.
        """

        if time_unit not in self.exchanges[exchange].timeframes:
            raise ValueError(
                exchange + " does not support " + time_unit + " timeframe for OHLCV data. \n" +
                "Possible values are: {}".format(list(self.exchanges[exchange].timeframes))
            )

        if not start_date:
            timeframe_regex = re.compile('([0-9]+)([a-zA-Z])')
            timeframe_matches = timeframe_regex.match(time_unit)
            time_quantity = timeframe_matches.group(1)
            time_period = timeframe_matches.group(2)

            if time_period == 'm':
                timedelta_args = { 'minutes': int(time_quantity) }
            elif time_period == 'h':
                timedelta_args = { 'hours': int(time_quantity) }
            elif time_period == 'd':
                timedelta_args = { 'days': int(time_quantity) }
            elif time_period == 'M':
                timedelta_args = { 'months': int(time_quantity) }
            elif time_period == 'y':
                timedelta_args = { 'years': int(time_quantity) }
            else:
                raise ValueError('unknown time unit: {}'.format(time_period))

            start_date_delta = timedelta(**timedelta_args)

            max_days_date = datetime.now() - (max_periods * start_date_delta)
            start_date = int(max_days_date.replace(tzinfo=timezone.utc).timestamp() * 1000)

        historical_data = self.exchanges[exchange].fetch_ohlcv(
            market_pair,
            timeframe=time_unit,
            since=start_date
        )

        time.sleep(self.exchanges[exchange].rateLimit / 1000)

        # Sort by timestamp in ascending order
        historical_data.sort(key=lambda d: d[0])
        return historical_data


    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_exchange_markets(self, exchanges=[], markets=[]):
        """Get market data for all symbol pairs listed on all configured exchanges.

        Args:
            markets (list, optional): A list of markets to get from the exchanges. Default is all
                markets.
            exchanges (list, optional): A list of exchanges to collect market data from. Default is
                all enabled exchanges.

        Decorators:
            retry

        Returns:
            dict: A dictionary containing market data for all symbol pairs.
        """

        if not exchanges:
            exchanges = self.exchanges

        exchange_markets = {}
        for exchange in exchanges:
            exchange_markets[exchange] = self.exchanges[exchange].load_markets()

            if markets:
                markets_to_remove = []
                for market in markets:
                    if not market in exchange_markets[exchange]:
                        self.logger.info('%s has no market %s, ignoring.', exchange, market)

                for market in exchange_markets[exchange]:
                    if not market in markets:
                        markets_to_remove.append(market)

                for market in markets_to_remove:
                    exchange_markets[exchange].pop(market, None)

            time.sleep(self.exchanges[exchange].rateLimit / 1000)
        return exchange_markets
