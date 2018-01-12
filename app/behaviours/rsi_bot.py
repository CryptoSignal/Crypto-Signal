
import ccxt
import structlog
from datetime import datetime, timedelta

class RSIBot():
    def __init__(self, behaviour_config, exchange_interface,
                 strategy_analyzer, notifier, db_handler):

        self.logger = structlog.get_logger()
        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier
        self.db_handler = db_handler


    def run(self, market_pairs):
        if market_pairs:
            market_data = self.exchange_interface.get_symbol_markets(market_pairs)
        else:
            market_data = self.exchange_interface.get_exchange_markets()

        rsi_data = {}
        for exchange, markets in market_data.items():
            rsi_data[exchange] = {}
            for market_pair in markets:
                try:
                    self.strategy_analyzer.prepare_historical_data(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                    )

                    rsi_data[exchange][market_pair] = self.strategy_analyzer.analyze_rsi(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                    )

                except ccxt.NetworkError:
                    self.logger.warn(
                        "Read timeout getting data for %s on %s skipping",
                        market_pair,
                        exchange
                    )
                    continue

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

        current_holdings = self.__get_holdings()

        if not current_holdings:
            self.__create_holdings()
            current_holdings = self.__get_holdings()
        else:
            if self.behaviour_config['mode'] == 'live':
                self.__update_holdings()
                current_holdings = self.__get_holdings()

        for exchange, markets in rsi_data.items():
            for market_pair in markets:
                base_symbol, quote_symbol = market_pair.split('/')
                self.buy(base_symbol, quote_symbol, market_pair, exchange, current_holdings)
                current_holdings = self.__get_holdings()
                self.sell(base_symbol, quote_symbol, market_pair, exchange, current_holdings)
                exit()



                if markets[market_pair]['is_hot']:
                    if not base_symbol in current_holdings[exchange]\
                    or current_holdings[exchange][base_symbol]['volume_total'] == 0:
                        self.buy(base_symbol, quote_symbol, market_pair, exchange, current_holdings)

                elif markets[market_pair]['is_cold']:
                    if base_symbol in current_holdings[exchange]\
                    and not current_holdings[exchange][base_symbol]['volume_free'] == 0:
                        self.sell(base_symbol, quote_symbol, market_pair, exchange, current_holdings)


    def buy(self, base_symbol, quote_symbol, market_pair, exchange, current_holdings):
        order_book = self.exchange_interface.get_order_book(market_pair, exchange)
        base_ask = order_book['asks'][0][0] if order_book['asks'] else None
        if not base_ask:
            return

        current_symbol_holdings = current_holdings[exchange][quote_symbol]
        quote_bid = current_symbol_holdings['volume_free']

        if quote_symbol in self.behaviour_config['buy']['trade_limits']:
            trade_limit = self.behaviour_config['buy']['trade_limits'][quote_symbol]
            if quote_bid > trade_limit:
                quote_bid = trade_limit

        base_volume = quote_bid / base_ask

        if self.behaviour_config['mode'] == 'live':
            # Do live trading stuff here
            print('Nothing to do yet')
        else:
            potential_holdings = self.db_handler.read_holdings(
                {
                    'exchange': exchange,
                    'symbol': base_symbol
                }
            )

            if potential_holdings:
                base_holding = potential_holdings[0]
                base_holding.volume_free = base_holding.volume_free + base_volume
                base_holding.volume_used = base_holding.volume_used
                base_holding.volume_total = base_holding.volume_free + base_holding.volume_used
                self.db_handler.update_holding(base_holding)
            else:
                base_holding = {
                    'exchange': exchange,
                    'symbol': base_symbol,
                    'volume_free': base_volume,
                    'volume_used': 0,
                    'volume_total': base_volume
                }
                self.db_handler.create_holding(base_holding)

            quote_holding = self.db_handler.read_holdings(
                {
                    'exchange': exchange,
                    'symbol': base_symbol
                }
            )[0]

            quote_holding.volume_free = quote_holding.volume_free - quote_bid
            quote_holding.volume_used = quote_holding.volume_used
            quote_holding.volume_total = quote_holding.volume_free + quote_holding.volume_used
            self.db_handler.update_holding(quote_holding)

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

        self.db_handler.create_transaction(purchase_payload)


    def sell(self, base_symbol, quote_symbol, market_pair, exchange, current_holdings):
        order_book = self.exchange_interface.get_order_book(market_pair, exchange)
        bid = order_book['bids'][0][0] if order_book['bids'] else None
        if not bid:
            return

        current_symbol_holdings = current_holdings[exchange][base_symbol]
        base_bid = current_symbol_holdings['volume_free']

        if base_symbol in self.behaviour_config['buy']['trade_limits']:
            trade_limit = self.behaviour_config['buy']['trade_limits'][base_symbol]
            if base_bid > trade_limit:
                base_bid = trade_limit

        quote_volume = base_bid * bid

        if self.behaviour_config['mode'] == 'live':
            # Do live trading stuff here
            print('Nothing to do yet')
        else:
            base_holding = self.db_handler.read_holdings(
                {
                    'exchange': exchange,
                    'symbol': base_symbol
                }
            )[0]

            base_holding.volume_free = base_holding.volume_free - base_bid
            base_holding.volume_used = base_holding.volume_used
            base_holding.volume_total = base_holding.volume_free + base_holding.volume_used
            self.db_handler.update_holding(base_holding)

            quote_holding = self.db_handler.read_holdings(
                {
                    'exchange': exchange,
                    'symbol': base_symbol
                }
            )[0]

            quote_holding.volume_free = quote_holding.volume_free + quote_volume
            quote_holding.volume_used = quote_holding.volume_used
            quote_holding.volume_total = quote_holding.volume_free + quote_holding.volume_used
            self.db_handler.update_holding(quote_holding)

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

        self.db_handler.create_transaction(sale_payload)


    def __get_holdings(self):
        holdings_table = self.db_handler.read_holdings()
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

                self.db_handler.create_holding(holding_payload)


    def __update_holdings(self):
        holdings_table = self.db_handler.read_holdings()
        user_account_markets = {}
        for row in holdings_table:
            if not row.exchange in user_account_markets:
                user_account_markets[row.exchange] = self.exchange_interface.get_account_markets(row.exchange)

            row.volume_free = user_account_markets[row.exchange]['free'][row.symbol]
            row.volume_used = user_account_markets[row.exchange]['used'][row.symbol]
            row.volume_total = user_account_markets[row.exchange]['total'][row.symbol]

            self.db_handler.update_holding(row)
