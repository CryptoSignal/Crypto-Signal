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

    def __init__(self, config, exchange_interface, strategy_analyzer, notifier):
        """Initializes DefaultBehaviour class.

        Args:
            indicator_conf (dict): A dictionary of configuration for this analyzer.
            exchange_interface (ExchangeInterface): Instance of the ExchangeInterface class for
                making exchange queries.
            strategy_analyzer (StrategyAnalyzer): Instance of the StrategyAnalyzer class for
                running analyzed_data on exchange information.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
        """

        self.logger = structlog.get_logger()
        self.indicator_conf = config.indicators
        self.informant_conf = config.informants
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier
        self.last_result = dict()


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

        analysis_dispatcher = self.strategy_analyzer.analysis_dispatcher()
        informant_dispatcher = self.strategy_analyzer.informant_dispatcher()

        new_result = dict()
        for exchange in market_data:
            if exchange not in new_result:
                new_result[exchange] = dict()
            self.logger.info("Beginning analysis of %s", exchange)

            for market_pair in market_data[exchange]:
                if market_pair not in new_result[exchange]:
                    new_result[exchange][market_pair] = dict()
                historical_data = dict()

                #for indicator in self.informant_conf:
                for indicator in self.indicator_conf:
                    if indicator not in new_result[exchange][market_pair]:
                        new_result[exchange][market_pair][indicator] = list()

                    #if indicator in informant_dispatcher:
                    if indicator in analysis_dispatcher:
                        behaviour_conf = self.indicator_conf[indicator]
                        #behaviour_conf = self.informant_conf[indicator]

                        for indicator_conf in behaviour_conf:
                            if indicator_conf['enabled']:
                                candle_period = indicator_conf['candle_period']


                                if candle_period not in historical_data:
                                    historical_data[candle_period] = self.exchange_interface.get_historical_data(
                                        market_data[exchange][market_pair]['symbol'],
                                        exchange,
                                        candle_period
                                    )

                                analysis_args = {
                                    'historical_data': historical_data[candle_period],
                                    'hot_thresh': indicator_conf['hot'],
                                    'cold_thresh': indicator_conf['cold']
                                }

                                #analysis_args = {
                                #    'historical_data': historical_data[candle_period]
                                #}

                                # If the period is customizable for the current indicator,
                                # fetch it from the configuration
                                if 'period_count' in indicator_conf:
                                    analysis_args['period_count'] = indicator_conf['period_count']

                                new_result[exchange][market_pair][indicator].append({
                                    'result': analysis_dispatcher[indicator](**analysis_args),
                                    #'result': informant_dispatcher[indicator](**analysis_args),
                                    'config': indicator_conf
                                })
                                try:
                                    pass
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
                        self.logger.warn("No such indicator %s, skipping.", indicator)

                if output_mode == 'cli':
                    output = self._get_cli_output(new_result[exchange][market_pair], market_pair)
                elif output_mode == 'csv':
                    output = self._get_csv_output(new_result[exchange][market_pair], market_pair)
                elif output_mode == 'json':
                    output = self._get_json_output(new_result[exchange][market_pair], market_pair)
                else:
                    output = 'Unknown output mode!'

                print(output)

        return new_result


    def _get_cli_output(self, analyzed_data, market_pair):
        """Creates the message to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis

        Returns:
            str: Completed cli message
        """

        normal_colour = '\u001b[0m'
        hot_colour = '\u001b[31m'
        cold_colour = '\u001b[36m'

        output = "{}:\t".format(market_pair)
        for analysis in analyzed_data:
            for i, indicator in enumerate(analyzed_data[analysis]):
                colour_code = normal_colour
                if indicator['result']['is_hot']:
                    colour_code = hot_colour

                if indicator['result']['is_cold']:
                    colour_code = cold_colour

                formatted_values = list()
                for value in indicator['result']['values']:
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


    def _get_csv_output(self, analyzed_data, market_pair):
        """Creates the csv to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis

        Returns:
            str: Completed cli csv
        """

        output = market_pair
        for analysis in analyzed_data:
            for i, indicator in enumerate(analyzed_data[analysis]):
                output += ',{} #{}'.format(analysis, i)
                if indicator['result']['is_hot']:
                    output += ',hot'

                if indicator['result']['is_cold']:
                    output += ',cold'

                formatted_values = list()
                for value in indicator['result']['values']:
                    if isinstance(value, float):
                        formatted_values.append(format(value, '.8f'))
                    else:
                        formatted_values.append(value)
                formatted_string = '/'.join(formatted_values)

                output += ',' + formatted_string
        return output


    def _get_json_output(self, analyzed_data, market_pair):
        """Creates the JSON to output to the CLI

        Args:
            analyzed_data (dict): The result of the completed analysis

        Returns:
            str: Completed JSON message
        """

        output = {'pair': market_pair, 'analysis': analyzed_data}
        output = json.dumps(output)
        return output
