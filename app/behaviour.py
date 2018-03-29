""" Runs the default analyzer, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import json
import traceback

import structlog
from ccxt import ExchangeError
from tenacity import RetryError


class Behaviour():
    """Default analyzer which gives users basic trading information.
    """

    def __init__(self, behaviour_config, exchange_interface, strategy_analyzer, notifier):
        """Initializes DefaultBehaviour class.

        Args:
            behaviour_config (dict): A dictionary of configuration for this analyzer.
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
        self.last_result = {}


    def run(self, market_pairs, output_mode):
        """The analyzer entrypoint

        Args:
            market_pairs (list): List of symbol pairs to operate on, if empty get all pairs.
        """

        self.logger.info("Starting default analyzer...")

        if market_pairs:
            self.logger.info("Found configured markets: %s", market_pairs)
        else:
            self.logger.info("No configured markets, using all available on exchange.")

        market_data = self.exchange_interface.get_exchange_markets(markets=market_pairs)

        self.logger.info("Using the following exchange(s): %s", list(market_data.keys()))

        new_result = self._test_strategies(market_data, output_mode)

        self.notifier.notify_all(new_result)


    def _test_strategies(self, market_data, output_mode):
        """Test the strategies and perform notifications as required

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to analyze.
        """

        analysis_dispatcher = self.strategy_analyzer.dispatcher()
        new_result = {}
        for exchange in market_data:
            if exchange not in new_result:
                new_result[exchange] = {}
            self.logger.info("Beginning analysis of %s", exchange)

            for market_pair in market_data[exchange]:
                if market_pair not in new_result[exchange]:
                    new_result[exchange][market_pair] = {}
                historical_data = {}

                for analyzer in self.behaviour_config:
                    if analyzer not in new_result[exchange][market_pair]:
                        new_result[exchange][market_pair][analyzer] = []

                    if analyzer in analysis_dispatcher:
                        behaviour_conf = self.behaviour_config[analyzer]

                        for indicator_conf in behaviour_conf:
                            if indicator_conf['enabled']:
                                candle_period = indicator_conf['candle_period']

                                try:
                                    if candle_period not in historical_data:
                                        historical_data[candle_period] = self.exchange_interface.get_historical_data(
                                            market_data[exchange][market_pair]['symbol'],
                                            exchange,
                                            candle_period
                                        )

                                    # If the period is customizable for the current indicator, fetch it
                                    # from the configuration
                                    if 'period_count' in indicator_conf:
                                        period_count = indicator_conf['period_count']

                                        new_result[exchange][market_pair][analyzer].append(
                                            analysis_dispatcher[analyzer](
                                                historical_data[candle_period],
                                                hot_thresh=indicator_conf['hot'],
                                                cold_thresh=indicator_conf['cold'],
                                                period_count=period_count
                                            )
                                        )
                                    else:
                                        new_result[exchange][market_pair][analyzer].append(
                                            analysis_dispatcher[analyzer](
                                                historical_data[candle_period],
                                                hot_thresh=indicator_conf['hot'],
                                                cold_thresh=indicator_conf['cold']
                                            )
                                        )
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
                                        'Something went wrong fetching data for %s, skipping',
                                        market_pair
                                    )
                                    self.logger.debug(traceback.format_exc())
                                except RetryError:
                                    self.logger.info(
                                        'Too many retries fetching information for pair %s, skipping',
                                        market_pair
                                    )
                                except ExchangeError:
                                    self.logger.info(
                                        'Exchange supplied bad data for pair %s, skipping',
                                        market_pair
                                    )
                                    self.logger.debug(traceback.format_exc())
                    else:
                        self.logger.warn("No such analyzer %s, skipping.", analyzer)

                #message += '{}\n'.format(self._get_notifier_message(analyzed_data, market_pair))

                if output_mode == 'cli':
                    output = self._get_cli_output(new_result[exchange])
                elif output_mode == 'csv':
                    output = self._get_csv_output(new_result[exchange])
                elif output_mode == 'json':
                    output = self._get_json_output(new_result[exchange])
                else:
                    output = 'Unknown output mode!'

                print(output)

            #if message.strip():
            #    self.notifier.notify_all(message)

        return new_result


    def _get_notifier_message(self, analyzed_data, market_pair):
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
                for i, _ in enumerate(analyzed_data[analysis]):
                    name = split_name(analysis.lower())
                    alert_freq = self.behaviour_config[name][i]['alert_frequency']
                    candle_period = self.behaviour_config[name][i]['candle_period']

                    if self.behaviour_config[name][i]['alert_enabled'] and alert_freq:
                        if analyzed_data[analysis][i]['is_hot']:
                            message += "{} {} ({}): {} is hot!\n".format(
                                analysis,
                                candle_period,
                                analyzed_data[analysis][i]['values'][0],
                                market_pair
                            )

                        if analyzed_data[analysis][i]['is_cold']:
                            message += "{} {} ({}): {} is cold!\n".format(
                                analysis,
                                candle_period,
                                analyzed_data[analysis][i]['values'][0],
                                market_pair
                            )

                        # Don't send any more alerts if our alert frequency is set to "one"
                        if alert_freq.lower() == 'once':
                            self.behaviour_config[name][i]['alert_frequency'] = None

        return message


    def _get_cli_output(self, analyzed_data):
        """Creates the message to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis

        Returns:
            str: Completed cli message
        """

        normal_colour = '\u001b[0m'
        hot_colour = '\u001b[31m'
        cold_colour = '\u001b[36m'

        for market_pair in analyzed_data:
            output = "{}:\t".format(market_pair)
            for analysis in analyzed_data[market_pair]:
                for i, indicator in enumerate(analyzed_data[market_pair][analysis]):
                    colour_code = normal_colour
                    if indicator['is_hot']:
                        colour_code = hot_colour

                    if indicator['is_cold']:
                        colour_code = cold_colour

                    formatted_values = []
                    for value in indicator['values']:
                        if isinstance(value, float):
                            formatted_values.append(format(value, '.8f'))
                        else:
                            formatted_values.append(value)
                    formatted_string = '/'.join(formatted_values)

                    output += "{}{}: {}{}     ".format(
                        colour_code,
                        '{} #{}'.format(analysis, i),
                        formatted_string,
                        normal_colour
                    )
        return output


    def _get_csv_output(self, analyzed_data):
        """Creates the csv to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis

        Returns:
            str: Completed cli csv
        """
        for market_pair in analyzed_data:
            output = market_pair
            for analysis in analyzed_data[market_pair]:
                for i, indicator in enumerate(analyzed_data[market_pair][analysis]):
                    output += ',{} #{}'.format(analysis, i)
                    if indicator['is_hot']:
                        output += ',hot'

                    if indicator['is_cold']:
                        output += ',cold'

                    formatted_values = []
                    for value in indicator['values']:
                        if isinstance(value, float):
                            formatted_values.append(format(value, '.8f'))
                        else:
                            formatted_values.append(value)
                    formatted_string = '/'.join(formatted_values)

                    output += ',' + formatted_string
        return output



    def _get_json_output(self, analyzed_data):
        """Creates the JSON to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis

        Returns:
            str: Completed JSON message
        """

        stringified_analysis = analyzed_data
        for market_pair in analyzed_data:
            for analysis in analyzed_data[market_pair]:
                for i, indicator in enumerate(analyzed_data[market_pair][analysis]):
                    stringified_analysis[analysis][i]['is_hot'] = str(indicator['is_hot'])
                    stringified_analysis[analysis][i]['is_cold'] = str(indicator['is_cold'])
            output = {'pair': market_pair, 'analysis': analyzed_data}
            output = json.dumps(output)
        return output
