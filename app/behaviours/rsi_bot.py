
import ccxt
import structlog


class RSIBot():
    def __init__(self, behaviour_config, exchange_interface, strategy_analyzer, notifier,
        db_handler):

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
                    rsi_data[exchange][market_pair] = self.strategy_analyzer.analyze_rsi(
                        market_data[exchange][market_pair]['symbol'],
                        exchange)

                except ccxt.NetworkError:
                    self.logger.warn("Read timeout getting data for %s on %s skipping",
                        market_pair,
                        exchange)
                    continue

        current_holdings = self.get_holdings()

        for exchange, markets in rsi_data.items():
            for market_pair in markets:
                self.buy(market_pair, exchange)
                self.sell(market_pair, exchange)
                if markets[market_pair]['is_hot']:
                    if not market_pair in current_holdings[exchange]:
                        self.buy(market_pair, exchange)

                elif markets[market_pair]['is_cold']:
                    if market_pair in current_holdings[exchange]:
                        self.sell(market_pair, exchange)


    def buy(self, market_pair, exchange):
        (base_symbol, quote_symbol) = market_pair.split('/')
        order_book = self.exchange_interface.get_order_book(market_pair, exchange)
        ask = order_book['asks'][0][0] if order_book['asks'] else None
        if not ask:
            return

        funds = self.behaviour_config['trade_parameters']['buy']['btc_amount']
        purchase_limit = self.behaviour_config['trade_parameters']['buy']['btc_trade_limit']
        purchase_quote_amount = purchase_limit
        if purchase_limit > funds:
            purchase_quote_amount = funds
        purchase_total_price = purchase_quote_amount / ask

        if self.behaviour_config['trade_parameters']['mode'] == 'live':
            # Do live trading stuff here
            print('Nothing to do yet')

        purchase_payload = {
            'exchange': exchange,
            'base_symbol': base_symbol,
            'quote_symbol': quote_symbol,
            'purchase_base_value': ask,
            'purchase_quote_value': purchase_quote_amount,
            'purchase_total': purchase_total_price
        }
        self.db_handler.create_transaction(purchase_payload)


    def sell(self, market_pair, exchange):
        (base_symbol, quote_symbol) = market_pair.split('/')
        query_payload = {
            'base_symbol': base_symbol,
            'quote_symbol': quote_symbol,
            'exchange': exchange,
            'is_open': True
        }

        transaction = self.db_handler.read_transactions(query_payload)[0]

        order_book = self.exchange_interface.get_order_book(market_pair, exchange)
        bid = order_book['bids'][0][0] if order_book['bids'] else None
        if not bid:
            return

        sale_value = bid * transaction.purchase_total

        if self.behaviour_config['trade_parameters']['mode'] == 'live':
            # Do live trading stuff here
            print('Nothing to do yet')

        sale_payload = {
            'sale_base_value': bid,
            'sale_quote_value': transaction.purchase_total,
            'sale_total': sale_value,
            'is_open': False
        }

        self.db_handler.update_transaction(transaction, sale_payload)


    def get_holdings(self):
        transactions = self.db_handler.read_transactions({'is_open': True})
        holdings = {}

        for row in transactions:
            if not row.exchange in holdings:
                holdings[row.exchange] = []

            market_pair = row.base_symbol + '/' + row.quote_symbol
            holdings[row.exchange].append(market_pair)

        return holdings
