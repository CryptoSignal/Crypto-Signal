"""Simple trading bot.
"""

from datetime import datetime, timedelta

import structlog

class SimpleBotBehaviour():
    """Simple trading bot.
    """

    def __init__(self, behaviour_config, exchange_interface,
                 strategy_analyzer, notifier, db_handler):
        """Initialize SimpleBotBehaviour class.

        Args:
            behaviour_config (dict): A dictionary of configuration for this behaviour.
            exchange_interface (ExchangeInterface): Instance of the ExchangeInterface class for
                making exchange queries.
            strategy_analyzer (StrategyAnalyzer): Instance of the StrategyAnalyzer class for
                running analysis on exchange information.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
            db_handler (DatbaseHandler): Instance of the DatabaseHandler class for reading and
                storing transaction data.
        """

        self.logger = structlog.get_logger()
        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier
        self.db_handler = db_handler


    def run(self, market_pairs):
        """The behaviour entrypoint

        Args:
            market_pairs (str): List of symbol pairs to operate on, if empty get all pairs.
        """

        self.logger.info("Starting bot behaviour...")

        if market_pairs:
            self.logger.debug("Found configured symbol pairs.")
            market_data = self.exchange_interface.get_symbol_markets(market_pairs)
        else:
            self.logger.debug("No configured symbol pairs, using all available on exchange.")
            market_data = self.exchange_interface.get_exchange_markets()

        analyzed_data = {}
        for exchange, markets in market_data.items():
            analyzed_data[exchange] = {}

            for market_pair in markets:
                historical_data = self.exchange_interface.get_historical_data(
                    market_data[exchange][market_pair]['symbol'],
                    exchange,
                    self.behaviour_config['analysis_timeframe']
                )

                strategy_result = self.__run_strategy(historical_data)
                if strategy_result:
                    analyzed_data[exchange][market_pair] = strategy_result

        self.logger.info("Reconciling open orders...")
        self.__reconcile_open_orders()

        self.logger.info("Updating current holdings...")
        current_holdings = self.__get_holdings()

        if not current_holdings:
            self.__create_holdings()
            current_holdings = self.__get_holdings()
        else:
            if self.behaviour_config['mode'] == 'live':
                self.__update_holdings()
                current_holdings = self.__get_holdings()

        self.logger.info("Looking for trading opportunities...")
        for exchange, markets in analyzed_data.items():
            for market_pair in analyzed_data[exchange]:
                base_symbol, quote_symbol = market_pair.split('/')

                if markets[market_pair]['is_hot']:
                    self.logger.debug(
                        "%s is hot at %s!",
                        market_pair,
                        markets[market_pair]['values'][0]
                    )
                    if not current_holdings[exchange][quote_symbol]['volume_total'] == 0:
                        if not base_symbol in current_holdings[exchange]\
                        or current_holdings[exchange][base_symbol]['volume_total'] == 0:
                            self.logger.debug("%s is not in holdings, buying!", base_symbol)
                            self.buy(
                                base_symbol,
                                quote_symbol,
                                market_pair,
                                exchange,
                                current_holdings)
                            current_holdings = self.__get_holdings()

                elif markets[market_pair]['is_cold']:
                    self.logger.debug(
                        "%s is cold at %s!",
                        market_pair,
                        markets[market_pair]['values'][0]
                    )
                    if base_symbol in current_holdings[exchange]\
                    and not current_holdings[exchange][base_symbol]['volume_free'] == 0:
                        self.logger.debug("%s is in holdings, selling!", base_symbol)
                        self.sell(
                            base_symbol,
                            quote_symbol,
                            market_pair,
                            exchange,
                            current_holdings)
                        current_holdings = self.__get_holdings()

        self.logger.debug(current_holdings)


    def __run_strategy(self, historical_data):
        """Run the selected analyzer over the historical data

        Args:
            historical_data (list): A matrix of historical OHLCV data.

        Returns:
            dict: The analyzed results for the historical data.
        """

        if self.behaviour_config['strategy'] == 'rsi':
            result = self.strategy_analyzer.analyze_rsi(
                historical_data,
                period_count=self.behaviour_config['strategy_period'],
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        elif self.behaviour_config['strategy'] == 'sma':
            result = self.strategy_analyzer.analyze_sma(
                historical_data,
                period_count=self.behaviour_config['strategy_period'],
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        elif self.behaviour_config['strategy'] == 'ema':
            result = self.strategy_analyzer.analyze_ema(
                historical_data,
                period_count=self.behaviour_config['strategy_period'],
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        elif self.behaviour_config['strategy'] == 'breakout':
            result = self.strategy_analyzer.analyze_breakout(
                historical_data,
                period_count=self.behaviour_config['strategy_period'],
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        elif self.behaviour_config['strategy'] == 'ichimoku':
            result = self.strategy_analyzer.analyze_ichimoku_cloud(
                historical_data,
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        elif self.behaviour_config['strategy'] == 'macd':
            result = self.strategy_analyzer.analyze_macd(
                historical_data,
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        elif self.behaviour_config['strategy'] == 'macd_sl':
            result = self.strategy_analyzer.analyze_macd_sl(
                historical_data,
                hot_thresh=self.behaviour_config['buy']['strategy_threshold'],
                cold_thresh=self.behaviour_config['sell']['strategy_threshold']
            )
        else:
            self.logger.error("No strategy selected, bailing out.")
            exit(1)

        return result


    def __reconcile_open_orders(self):
        """Cancels any orders that have been open for too long.
        """
        open_orders = self.exchange_interface.get_open_orders()

        for exchange in open_orders:
            for order in open_orders[exchange]:
                order_time = datetime.fromtimestamp(
                    order['timestamp']
                ).strftime('%c')

                time_to_hold = datetime.now() - timedelta(
                    hours=self.behaviour_config['open_order_max_hours']
                )

                if self.behaviour_config['mode'] == 'live':
                    if time_to_hold > order_time:
                        self.exchange_interface.cancel_order(
                            exchange,
                            order['id']
                        )


    def buy(self, base_symbol, quote_symbol, market_pair, exchange, current_holdings):
        """Buy a base currency with a quote currency.

        Args:
            base_symbol (str): The symbol for the base currency (currency being bought).
            quote_symbol (str): The symbol for the quote currency (currency being sold).
            market_pair (str): Contains the symbol pair to operate on in the form of Base/Quote.
            exchange (str): Contains the exchange the user wants to perform the trade on.
            current_holdings (dict): A dictionary containing the users currently available funds.
        """

        order_book = self.exchange_interface.get_order_book(market_pair, exchange)
        base_ask = order_book['asks'][0][0] if order_book['asks'] else None
        if not base_ask:
            return

        base_ask_volume = order_book['asks'][0][1]

        current_symbol_holdings = current_holdings[exchange][quote_symbol]
        quote_volume = current_symbol_holdings['volume_free']

        if quote_symbol in self.behaviour_config['buy']['trade_limits']:
            trade_limit = self.behaviour_config['buy']['trade_limits'][quote_symbol]
            if quote_volume > trade_limit:
                quote_volume = trade_limit

        base_volume = quote_volume / base_ask
        rank = 1

        # Go down the asks until we find an offer that will fill our order completely
        while rank < len(order_book['asks']) and base_volume > base_ask_volume:
            base_ask, base_ask_volume = order_book['asks'][rank]
            base_volume = quote_volume / base_ask

            rank += 1

        if self.behaviour_config['mode'] == 'live':
            # Do live trading stuff here
            print('Nothing to do yet')
        else:
            potential_holdings = self.db_handler.read_rows(
                'holdings',
                {
                    'exchange': exchange,
                    'symbol': base_symbol
                }
            )

            if potential_holdings.count():
                base_holding = potential_holdings.one()
                base_holding.volume_free = base_holding.volume_free + base_volume
                base_holding.volume_used = base_holding.volume_used
                base_holding.volume_total = base_holding.volume_free + base_holding.volume_used
                self.db_handler.update_row('holdings', base_holding)
            else:
                base_holding = {
                    'exchange': exchange,
                    'symbol': base_symbol,
                    'volume_free': base_volume,
                    'volume_used': 0,
                    'volume_total': base_volume
                }
                self.db_handler.create_row('holdings', base_holding)

            quote_holding = self.db_handler.read_rows(
                'holdings',
                {
                    'exchange': exchange,
                    'symbol': quote_symbol
                }
            ).one()

            quote_holding.volume_free = quote_holding.volume_free - quote_volume
            quote_holding.volume_used = quote_holding.volume_used
            quote_holding.volume_total = quote_holding.volume_free + quote_holding.volume_used

            self.db_handler.update_row('holdings', quote_holding)

        purchase_payload = {
            'exchange': exchange,
            'base_symbol': base_symbol,
            'quote_symbol': quote_symbol,
            'action': 'buy_base',
            'base_value': base_ask,
            'quote_value': quote_bid,
            'fee_rate': 0,
            'base_volume': base_volume,
            'quote_volume': quote_bid
        }

        print(purchase_payload)

        self.db_handler.create_row('transactions', purchase_payload)


    def sell(self, base_symbol, quote_symbol, market_pair, exchange, current_holdings):
        """Sell a base currency for a quote currency.

        Args:
            base_symbol (str): The symbol for the base currency (currency being sold).
            quote_symbol (str): The symbol for the quote currency (currency being bought).
            market_pair (str): Contains the symbol pair to operate on in the form of Base/Quote.
            exchange (str): Contains the exchange the user wants to perform the trade on.
            current_holdings (dict): A dictionary containing the users currently available funds.
        """

        order_book = self.exchange_interface.get_order_book(market_pair, exchange)
        base_bid = order_book['bids'][0][0] if order_book['bids'] else None
        if not base_bid:
            return

        base_bid_volume = order_book['bids'][0][1]

        current_symbol_holdings = current_holdings[exchange][base_symbol]
        base_volume = current_symbol_holdings['volume_free']

        if base_symbol in self.behaviour_config['sell']['trade_limits']:
            trade_limit = self.behaviour_config['sell']['trade_limits'][base_symbol]

            if base_volume > trade_limit:
                base_volume = trade_limit

        quote_volume = base_bid * base_volume
        rank = 1

        # Go down the bids until we find an offer that will fill our order completely
        while rank < len(order_book['bids']) and base_volume > base_bid_volume:
            base_bid, base_bid_volume = order_book['bids'][rank]
            quote_volume = base_bid * base_bid_volume

            rank += 1

        if self.behaviour_config['mode'] == 'live':
            # Do live trading stuff here
            print('Nothing to do yet')
        else:
            base_holding = self.db_handler.read_rows(
                'holdings',
                {
                    'exchange': exchange,
                    'symbol': base_symbol
                }
            ).one()

            base_holding.volume_free = base_holding.volume_free - base_bid
            base_holding.volume_used = base_holding.volume_used
            base_holding.volume_total = base_holding.volume_free + base_holding.volume_used
            self.db_handler.update_row('holdings', base_holding)

            quote_holding = self.db_handler.read_rows(
                'holdings',
                {
                    'exchange': exchange,
                    'symbol': quote_symbol
                }
            ).one()

            quote_holding.volume_free = quote_holding.volume_free + quote_volume
            quote_holding.volume_used = quote_holding.volume_used
            quote_holding.volume_total = quote_holding.volume_free + quote_holding.volume_used
            self.db_handler.update_row('holdings', quote_holding)

        sale_payload = {
            'exchange': exchange,
            'base_symbol': base_symbol,
            'quote_symbol': quote_symbol,
            'action': 'sell_base',
            'base_value': bid,
            'quote_value': quote_volume,
            'fee_rate': 0,
            'base_volume': base_bid,
            'quote_volume': quote_volume
        }

        print(sale_payload)

        self.db_handler.create_row('transactions', sale_payload)


    def __get_holdings(self):
        """Fetch the users crypto holdings from the database cache.

        Returns:
            dict: A dictionary of the users available funds.
        """

        holdings_table = self.db_handler.read_rows('holdings')

        holdings = {}
        for row in holdings_table:
            if not row.exchange in holdings:
                holdings[row.exchange] = {}

            holdings[row.exchange][row.symbol] = {
                'volume_free': row.volume_free,
                'volume_used': row.volume_used,
                'volume_total': row.volume_total
            }

        return holdings


    def __create_holdings(self):
        """Query the users account details to populate the crypto holdings database cache.
        """

        for exchange in self.exchange_interface.exchanges:
            user_account_markets = self.exchange_interface.get_account_markets(exchange)
            for symbol in user_account_markets['free']:
                holding_payload = {
                    'exchange': exchange,
                    'symbol': symbol,
                    'volume_free': user_account_markets['free'][symbol],
                    'volume_used': user_account_markets['used'][symbol],
                    'volume_total': user_account_markets['total'][symbol]
                }

                self.db_handler.create_row('holdings', holding_payload)

            quote_symbols = self.exchange_interface.get_quote_symbols(exchange)

            for symbol in quote_symbols:
                if symbol not in user_account_markets['free']:
                    holding_payload = {
                        'exchange': exchange,
                        'symbol': symbol,
                        'volume_free': 0,
                        'volume_used': 0,
                        'volume_total': 0
                    }

                self.db_handler.create_row('holdings', holding_payload)


    def __update_holdings(self):
        """Synchronize the database cache with the crypto holdings from the users account.
        """

        holdings_table = self.db_handler.read_rows('holdings')
        user_account_markets = {}
        for row in holdings_table:
            if not row.exchange in user_account_markets:
                user_account_markets[row.exchange] = self.exchange_interface.get_account_markets(
                    row.exchange
                )

            row.volume_free = user_account_markets[row.exchange]['free'][row.symbol]
            row.volume_used = user_account_markets[row.exchange]['used'][row.symbol]
            row.volume_total = user_account_markets[row.exchange]['total'][row.symbol]

            self.db_handler.update_row('holdings', row)
