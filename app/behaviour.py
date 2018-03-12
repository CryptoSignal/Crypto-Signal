""" Runs the default behaviour, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import json
import traceback

import structlog
from ccxt import ExchangeError
from tenacity import RetryError


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


    def run(self, market_pairs, output_mode):
        """The behaviour entrypoint

        Args:
            market_pairs (list): List of symbol pairs to operate on, if empty get all pairs.
        """

        self.logger.info("Starting default behaviour...")

        if market_pairs:
            self.logger.info("Found configured markets: %s", market_pairs)
        else:
            self.logger.info("No configured markets, using all available on exchange.")

        market_data = self.exchange_interface.get_exchange_markets(markets=market_pairs)

        self.logger.info("Using the following exchange(s): %s", list(market_data.keys()))

        self.__test_strategies(market_data, output_mode)


    def __test_strategies(self, market_data, output_mode):
        """Test the strategies and perform notifications as required

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to analyze.
        """

        analysis_dispatcher = self.strategy_analyzer.dispatcher()
        for exchange in market_data:
            self.logger.info("Beginning analysis of %s", exchange)
            message = ''
            for market_pair in market_data[exchange]:
                analyzed_data = {}
                historical_data = {}

                try:
                    for behaviour in self.behaviour_config:
                        if behaviour in analysis_dispatcher:
                            behaviour_conf = self.behaviour_config[behaviour]

                            if behaviour_conf['enabled']:
                                candle_period = behaviour_conf['candle_period']

                                if candle_period not in historical_data:
                                    historical_data[candle_period] = self.exchange_interface.get_historical_data(
                                        market_data[exchange][market_pair]['symbol'],
                                        exchange,
                                        candle_period
                                    )

                                # If the period is customizable for the current indicator, fetch it
                                # from the configuration
                                if 'period_count' in behaviour_conf:
                                    period_count = behaviour_conf['period_count']

                                    # If our period_count is a list, run a separate analysis over the
                                    # same indicator for each period provided
                                    if isinstance(period_count, list):
                                        for period in period_count:
                                            analyzed_data[behaviour + str(period)] = analysis_dispatcher[behaviour](
                                                historical_data[candle_period],
                                                hot_thresh=behaviour_conf['hot'],
                                                cold_thresh=behaviour_conf['cold'],
                                                period_count=period
                                            )
                                    else:
                                        # Else period_count is either an int (for a standalone indicator)
                                        # or tuple (in the case of SMA/EMA crossovers), which means we should
                                        # just pass the entire value into the analyzer
                                        analyzed_data[behaviour] = analysis_dispatcher[behaviour](
                                            historical_data[candle_period],
                                            hot_thresh=behaviour_conf['hot'],
                                            cold_thresh=behaviour_conf['cold'],
                                            period_count=period_count
                                        )
                                else:
                                    analyzed_data[behaviour] = analysis_dispatcher[behaviour](
                                        historical_data[candle_period],
                                        hot_thresh=behaviour_conf['hot'],
                                        cold_thresh=behaviour_conf['cold']
                                    )

                        else:
                            self.logger.warn("No such behaviour %s, skipping.", behaviour)
                except ValueError as e:
                    self.logger.info(e)
                    self.logger.info(
                        'Invalid data encountered while processing pair %s, skipping',
                        market_pair
                    )
                    self.logger.debug(traceback.format_exc())
                except TypeError:
                    self.logger.info(
                        'Invalid data encountered while processing pair %s, skipping',
                        market_pair
                    )
                    self.logger.debug(traceback.format_exc())
                except AttributeError:
                    self.logger.info(
                        'Something went wrong fetching data for %s, skippping',
                        market_pair
                    )
                    self.logger.debug(traceback.format_exc())
                except RetryError:
                    self.logger.info(
                        'Too many retries fetching informationg for pair %s, skipping',
                        market_pair
                    )
                except ExchangeError:
                    self.logger.info(
                        'Exchange supplied bad data for pair %s, skipping',
                        market_pair
                    )
                    self.logger.debug(traceback.format_exc())

                message += '{}\n'.format(self.__get_notifier_message(analyzed_data, market_pair))

                if output_mode == 'cli':
                    output = self.__get_cli_output(analyzed_data, market_pair)
                elif output_mode == 'csv':
                    output = self.__get_csv_output(analyzed_data, market_pair)
                elif output_mode == 'json':
                    output = self.__get_json_output(analyzed_data, market_pair)
                else:
                    output = 'Unknown output mode!'

                print(output)

            if message:
                self.notifier.notify_all(message)


    def __get_notifier_message(self, analyzed_data, market_pair):
        """Creates the message to send via the configured notifier(s)

        Args:
            analyzed_data (dict): The result of the completed analysis
            market_pair (str): The market related to the message

        Returns:
            str: Completed notifier message
        """

        import re

        def split_name(name):
            return re.split(r'[0-9]+', name)[0]

        message = ""
        for analysis in analyzed_data:
            if analyzed_data[analysis]:
                if self.behaviour_config[split_name(analysis.lower())]['alert_enabled']:
                    if analyzed_data[analysis]['is_hot']:
                        message += "{}: {} is hot!\n".format(analysis, market_pair)

                    if analyzed_data[analysis]['is_cold']:
                        message += "{}: {} is cold!\n".format(analysis, market_pair)

        return message


    def __get_cli_output(self, analyzed_data, market_pair):
        """Creates the message to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis
            market_pair (str): The market related to the message

        Returns:
            str: Completed cli message
        """

        normal_colour = '\u001b[0m'
        hot_colour = '\u001b[31m'
        cold_colour = '\u001b[36m'

        output = "{}:\t".format(market_pair)
        for analysis in analyzed_data:
            if analyzed_data[analysis]:
                colour_code = normal_colour
                if analyzed_data[analysis]['is_hot']:
                    colour_code = hot_colour

                if analyzed_data[analysis]['is_cold']:
                    colour_code = cold_colour

                formatted_values = []
                for value in analyzed_data[analysis]['values']:
                    if isinstance(value, float):
                        formatted_values.append(format(value, '.8f'))
                    else:
                        formatted_values.append(value)
                formatted_string = '/'.join(formatted_values)

                output += "{}{}: {}{}     ".format(
                    colour_code,
                    analysis,
                    formatted_string,
                    normal_colour
                )
        return output


    def __get_csv_output(self, analyzed_data, market_pair):
        """Creates the csv to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis
            market_pair (str): The market related to the message

        Returns:
            str: Completed cli csv
        """

        output = market_pair
        for analysis in analyzed_data:
            if analyzed_data[analysis]:
                output += ',' + analysis
                if analyzed_data[analysis]['is_hot']:
                    output += ',hot'

                if analyzed_data[analysis]['is_cold']:
                    output += ',cold'

                formatted_values = []
                for value in analyzed_data[analysis]['values']:
                    if isinstance(value, float):
                        formatted_values.append(format(value, '.8f'))
                    else:
                        formatted_values.append(value)
                formatted_string = '/'.join(formatted_values)

                output += ',' + formatted_string
        return output



    def __get_json_output(self, analyzed_data, market_pair):
        """Creates the JSON to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis
            market_pair (str): The market related to the message

        Returns:
            str: Completed JSON message
        """

        stringified_analysis = analyzed_data
        for analysis in analyzed_data:
            if analyzed_data[analysis]:
                stringified_analysis[analysis]['is_hot'] = str(analyzed_data[analysis]['is_hot'])
                stringified_analysis[analysis]['is_cold'] = str(analyzed_data[analysis]['is_cold'])
        output = {'pair': market_pair, 'analysis': analyzed_data}
        output = json.dumps(output)
        return output
