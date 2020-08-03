"""Interface for performing queries against exchange API's
"""

import re
import sys
import time
from datetime import datetime, timedelta, timezone

import ccxt
import numpy as np
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
        self.exchanges = dict()
        self.base_markets = dict()
        self.top_pairs = None
        self.exclude = []

        # Loads the exchanges using ccxt.
        for exchange in exchange_config:
            if exchange_config[exchange]['required']['enabled']:
                new_exchange = getattr(ccxt, exchange)({
                    "enableRateLimit": True
                })

                # sets up api permissions for user if given
                if new_exchange:
                    self.exchanges[new_exchange.id] = new_exchange
                    if 'all_pairs' in exchange_config[exchange]:
                        if len(exchange_config[exchange]['all_pairs']) > 0:
                            self.base_markets[new_exchange.id] = exchange_config[exchange]['all_pairs']
                        else:
                            self.base_markets[new_exchange.id] = list()

                    if 'top_pairs' in exchange_config[exchange]:
                        self.top_pairs = exchange_config[exchange]['top_pairs']

                    if 'exclude' in exchange_config[exchange]:
                        self.exclude = exchange_config[exchange]['exclude']
                else:
                    self.logger.error(
                        "Unable to load exchange %s", new_exchange)

    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_historical_data(self, market_pair, exchange, time_unit, start_date=None, max_periods=240):
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

        try:
            if time_unit not in self.exchanges[exchange].timeframes:
                raise ValueError(
                    "{} does not support {} timeframe for OHLCV data. Possible values are: {}".format(
                        exchange,
                        time_unit,
                        list(self.exchanges[exchange].timeframes)
                    )
                )
        except AttributeError:
            self.logger.error(
                '%s interface does not support timeframe queries! We are unable to fetch data!',
                exchange
            )
            raise AttributeError(sys.exc_info())

        if not start_date:
            timeframe_regex = re.compile('([0-9]+)([a-zA-Z])')
            timeframe_matches = timeframe_regex.match(time_unit)
            time_quantity = timeframe_matches.group(1)
            time_period = timeframe_matches.group(2)

            timedelta_values = {
                'm': 'minutes',
                'h': 'hours',
                'd': 'days',
                'w': 'weeks',
                'M': 'months',
                'y': 'years'
            }

            timedelta_args = {
                timedelta_values[time_period]: int(time_quantity)}

            start_date_delta = timedelta(**timedelta_args)

            max_days_date = datetime.now() - (max_periods * start_date_delta)
            start_date = int(max_days_date.replace(
                tzinfo=timezone.utc).timestamp() * 1000)

        historical_data = self.exchanges[exchange].fetch_ohlcv(
            market_pair,
            timeframe=time_unit,
            since=start_date
        )

        if not historical_data:
            raise ValueError(
                'No historical data provided returned by exchange.')

        # Sort by timestamp in ascending order
        historical_data.sort(key=lambda d: d[0])

        time.sleep(self.exchanges[exchange].rateLimit / 1000)

        return historical_data

    @retry(retry=retry_if_exception_type(ccxt.NetworkError), stop=stop_after_attempt(3))
    def get_top_markets(self, exchange, base_markets):
        top_markets = []

        if self.exchanges[exchange].has['fetchTickers']:
            tickers = self.exchanges[exchange].fetch_tickers()

            for base_market in base_markets:
                if len(self.exclude) > 0:
                    for pair_to_exclude in self.exclude:
                        tickers.pop(pair_to_exclude + '/' + base_market, None)

                values = [(k, int(v['quoteVolume']))
                          for k, v in tickers.items() if k.endswith(base_market)]

                values = np.array(
                    values, dtype=[('market', 'U10'), ('volume', int)])
                values = np.sort(values, order='volume')

                if self.top_pairs and (len(values) > self.top_pairs):
                    limit = -self.top_pairs
                    values = values[limit:]['market'].tolist()
                else:
                    values = values[:]['market'].tolist()

                top_markets = top_markets + values

        return top_markets

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

        exchange_markets = dict()
        for exchange in exchanges:
            exchange_markets[exchange] = self.exchanges[exchange].load_markets()
            curr_markets = {
                k: v for k, v in exchange_markets[exchange].items() if v['active'] == True}

            if markets:
                # Only retrieve markets the users specified
                exchange_markets[exchange] = {
                    key: curr_markets[key] for key in curr_markets if key in markets}

                for market in markets:
                    if market not in exchange_markets[exchange]:
                        self.logger.info(
                            '%s has no market %s, ignoring.', exchange, market)
            else:
                if self.base_markets[exchange]:
                    if self.top_pairs and self.top_pairs > 0:
                        self.logger.info('Getting top %d pairs from %s in %s', self.top_pairs, str(
                            self.base_markets[exchange]), exchange)
                        all_markets = {key: curr_markets[key] for key in curr_markets
                                       if curr_markets[key]['quote'] in self.base_markets[exchange]}

                        top_markets = self.get_top_markets(
                            exchange, self.base_markets[exchange])

                        exchange_markets[exchange] = {
                            k: v for k, v in all_markets.items() if k in top_markets}
                    else:
                        self.logger.info('Getting all %s market pairs for %s ' % (
                            self.base_markets[exchange], exchange))
                        exchange_markets[exchange] = {key: curr_markets[key] for key in curr_markets
                                                      if curr_markets[key]['quote'] in self.base_markets[exchange]}

                        if isinstance(self.exclude, list) and len(self.exclude) > 0:
                            for base_market in self.base_markets[exchange]:
                                for pair_to_exclude in self.exclude:
                                    exchange_markets[exchange].pop(
                                        pair_to_exclude, None)
                                    exchange_markets[exchange].pop(
                                        pair_to_exclude + '/' + base_market, None)

            time.sleep(self.exchanges[exchange].rateLimit / 1000)

        return exchange_markets
