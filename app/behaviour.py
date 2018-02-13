""" Runs the default behaviour, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import structlog

class Behaviour():
    """Default behaviour which gives users basic trading information.
    """

    def __init__(self, behaviour_config, exchange_interface, strategy_analyzer, notifier):
        """Initializes DefaultBehaviour class.

        Args:
            behaviour_config (dict): A dictionary of configuration for this behaviour.
            exchange_interface (ExchangeInterface): Instance of the ExchangeInterface class for
                making exchange queries.
            strategy_analyzer (StrategyAnalyzer): Instance of the StrategyAnalyzer class for
                running analyzed_data on exchange information.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
        """

        self.logger = structlog.get_logger()
        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier


    def run(self, market_pairs):
        """The behaviour entrypoint

        Args:
            market_pairs (list): List of symbol pairs to operate on, if empty get all pairs.
        """

        self.logger.info("Starting default behaviour...")

        if market_pairs:
            self.logger.debug("Found configured symbol pairs.")
            market_data = self.exchange_interface.get_symbol_markets(market_pairs)
        else:
            self.logger.debug("No configured symbol pairs, using all available on exchange.")
            market_data = self.exchange_interface.get_exchange_markets()

        self.__test_strategies(market_data)


    def __test_strategies(self, market_data):
        """Test the strategies and perform notifications as required

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to analyze.
        """

        analysis_dispatcher = self.strategy_analyzer.dispatcher()
        for exchange in market_data:
            for market_pair in market_data[exchange]:
                analyzed_data = {}
                historical_data = {}

                for behaviour in self.behaviour_config:
                    if behaviour in analysis_dispatcher:
                        behaviour_conf = self.behaviour_config[behaviour]

                        if behaviour_conf['enabled']:
                            candle_period = behaviour_conf['candle_period']

                            if not candle_period in historical_data:
                                historical_data[candle_period] = self.exchange_interface.get_historical_data(
                                    market_data[exchange][market_pair]['symbol'],
                                    exchange,
                                    candle_period
                                )

                            analyzed_data[behaviour] = analysis_dispatcher[behaviour](
                                historical_data[candle_period],
                                hot_thresh=behaviour_conf['hot'],
                                cold_thresh=behaviour_conf['cold']
                            )
                    else:
                        self.logger.warn("No such behaviour: %s, skipping.", behaviour)

                message = ""
                output = "{}:\t".format(market_pair)
                for analysis in analyzed_data:
                    if analyzed_data[analysis]:
                        if self.behaviour_config[analysis.lower()]['alert_enabled']:
                            color_code = '\u001b[0m'
                            color_reset = '\u001b[0m'
                            if analyzed_data[analysis]['is_hot']:
                                color_code = '\u001b[31m'
                                message += "{}: {} is hot!\n".format(analysis, market_pair)

                            if analyzed_data[analysis]['is_cold']:
                                color_code = '\u001b[36m'
                                message += "{}: {} is cold!\n".format(analysis, market_pair)

                        formatted_values = []
                        for value in analyzed_data[analysis]['values']:
                            if isinstance(value, float):
                                formatted_values.append(format(value, '.8f'))
                            else:
                                formatted_values.append(value)

                        formatted_string = '/'.join(formatted_values)
                        output += "{}{}: {}{}     ".format(
                            color_code,
                            analysis,
                            formatted_string,
                            color_reset
                        )

                if message:
                    self.notifier.notify_all(message)

                print(output)
