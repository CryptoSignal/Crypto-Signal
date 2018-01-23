from flask import Flask, request, jsonify, render_template

import ccxt
import structlog
from behaviours.ui.backtesting.backtest import Backtester


"""
A server object wrapping our flask instance
"""
class ServerBehaviour(object):
    def __init__(self, behaviour_config, exchange_interface,
                 strategy_analyzer, notifier, db_handler):
        """Initialize RSIBot class.

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

        self.app = Flask(__name__, static_folder='www/static', template_folder='www/static/templates')
        self.__add_backtesting_endpoints()
        self.exchange_interface.override_exchange_config()


    def __add_backtesting_endpoints(self):

        def index_action():
            return render_template("index.html")

        def markets_action():
            exchange = request.args.get('exchange')

            markets = list(self.exchange_interface.get_markets_for_exchange(exchange))

            return jsonify(response=200, result=markets)

        def exchanges_action():
            exchanges = ccxt.exchanges

            return jsonify(response=200, result=exchanges)


        def backtesting_action():
            exchange_name = request.args.get('exchangeName')
            coin_pair = request.args.get('pair')
            period_length = request.args.get('period')
            capital = float(request.args.get('capital'))
            stop_loss = float(request.args.get('stopLoss'))
            start_time = int(request.args.get('startTime'))

            post_data = request.get_json()
            indicators = post_data['indicators']
            buy_strategy = post_data['buyStrategy']
            sell_strategy = post_data['sellStrategy']

            try:
                backtester = Backtester(coin_pair, period_length, exchange_name, self.exchange_interface, capital, stop_loss,
                                    start_time, buy_strategy, sell_strategy, indicators)
                backtester.run()
                result = backtester.get_results()

                return jsonify(response=200, result=result)

            except Exception as e:
                # Return the exception message if the selected exchange encounters an error while fetching historical data
                return jsonify(response=500, result={'message': str(e)})

        self.add_endpoint(endpoint='/', endpoint_name='index', handler=index_action)
        self.add_endpoint(endpoint='/backtest', endpoint_name='backtest', methods=['POST'], handler=backtesting_action)
        self.add_endpoint(endpoint='/markets', endpoint_name='markets', handler=markets_action)
        self.add_endpoint(endpoint='/exchanges', endpoint_name='exchanges', handler=exchanges_action)

    def run(self, debug=True):
        self.app.run(debug=debug, host='0.0.0.0', port=5000)

    def add_endpoint(self, endpoint=None, endpoint_name=None, methods=['GET'], handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=methods)


class EndpointAction(object):

    def __init__(self, action):
        self.action = action

    def __call__(self, *args):
        return self.action()
