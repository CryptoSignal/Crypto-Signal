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

        self.output = {
            'cli': self._get_cli_output,
            'csv': self._get_csv_output,
            'json': self._get_json_output
        }


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

        new_result = dict()
        for exchange in market_data:
            self.logger.info("Beginning analysis of %s", exchange)
            if exchange not in new_result:
                new_result[exchange] = dict()

            for market_pair in market_data[exchange]:
                if market_pair not in new_result[exchange]:
                    new_result[exchange][market_pair] = dict()

                new_result[exchange][market_pair]['indicators'] = self._get_indicator_results(
                    exchange,
                    market_pair
                )

                new_result[exchange][market_pair]['informants'] = self._get_informant_results(
                    exchange,
                    market_pair
                )

                if output_mode in self.output:
                    print(
                        self.output[output_mode](new_result[exchange][market_pair], market_pair),
                        end=''
                    )
                else:
                    self.logger.warn()

        # Print an empty line when complete
        print()
        return new_result


    def _get_indicator_results(self, exchange, market_pair):
        indicator_dispatcher = self.strategy_analyzer.indicator_dispatcher()
        results = { indicator: list() for indicator in self.indicator_conf.keys() }
        historical_data_cache = dict()

        for indicator in self.indicator_conf:
            if indicator not in indicator_dispatcher:
                self.logger.warn("No such indicator %s, skipping.", indicator)
                continue

            for indicator_conf in self.indicator_conf[indicator]:
                if indicator_conf['enabled']:
                    candle_period = indicator_conf['candle_period']
                else:
                    self.logger.debug("%s is disabled, skipping.", indicator)
                    continue

                if candle_period not in historical_data_cache:
                    historical_data_cache[candle_period] = self._get_historical_data(
                        market_pair,
                        exchange,
                        candle_period
                    )

                if historical_data_cache[candle_period]:
                    analysis_args = {
                        'historical_data': historical_data_cache[candle_period],
                        'signal': indicator_conf['signal'],
                        'hot_thresh': indicator_conf['hot'],
                        'cold_thresh': indicator_conf['cold']
                    }

                    if 'period_count' in indicator_conf:
                        analysis_args['period_count'] = indicator_conf['period_count']

                    results[indicator].append({
                        'result': self._get_analysis_result(
                            indicator_dispatcher,
                            indicator,
                            analysis_args,
                            market_pair
                        ),
                        'config': indicator_conf
                    })
        return results


    def _get_informant_results(self, exchange, market_pair):
        informant_dispatcher = self.strategy_analyzer.informant_dispatcher()
        results = { informant: list() for informant in self.informant_conf.keys() }
        historical_data_cache = dict()

        for informant in self.informant_conf:
            if informant not in informant_dispatcher:
                self.logger.warn("No such informant %s, skipping.", informant)
                continue

            for informant_conf in self.informant_conf[informant]:
                if informant_conf['enabled']:
                    candle_period = informant_conf['candle_period']
                else:
                    self.logger.debug("%s is disabled, skipping.", informant)
                    continue

                if candle_period not in historical_data_cache:
                    historical_data_cache[candle_period] = self._get_historical_data(
                        market_pair,
                        exchange,
                        candle_period
                    )

                if historical_data_cache[candle_period]:
                    analysis_args = {
                        'historical_data': historical_data_cache[candle_period]
                    }

                    if 'period_count' in informant_conf:
                        analysis_args['period_count'] = informant_conf['period_count']

                    results[informant].append({
                        'result': self._get_analysis_result(
                            informant_dispatcher,
                            informant,
                            analysis_args,
                            market_pair
                        ),
                        'config': informant_conf
                    })
        return results


    def _get_historical_data(self, market_pair, exchange, candle_period):
        try:
            historical_data = self.exchange_interface.get_historical_data(
                market_pair,
                exchange,
                candle_period
            )
        except RetryError:
            self.logger.error(
                'Too many retries fetching information for pair %s, skipping',
                market_pair
            )
        except ExchangeError:
            self.logger.error(
                'Exchange supplied bad data for pair %s, skipping',
                market_pair
            )
        except ValueError as e:
            self.logger.error(e)
            self.logger.error(
                'Invalid data encountered while processing pair %s, skipping',
                market_pair
            )
            self.logger.debug(traceback.format_exc())
        except AttributeError:
            self.logger.error(
                'Something went wrong fetching data for %s, skipping',
                market_pair
            )
            self.logger.debug(traceback.format_exc())
        return historical_data


    def _get_analysis_result(self, dispatcher, indicator, dispatcher_args, market_pair):
        try:
            results = dispatcher[indicator](**dispatcher_args)
        except TypeError:
            self.logger.info(
                'Invalid type encountered while processing pair %s for indicator %s, skipping',
                market_pair,
                indicator
            )
            self.logger.debug(traceback.format_exc())
        return results


    def _get_cli_output(self, results, market_pair):
        """Creates the message to output to the CLI

        Args:
            results (dict): The result of the completed analysis

        Returns:
            str: Completed cli message
        """

        normal_colour = '\u001b[0m'
        hot_colour = '\u001b[31m'
        cold_colour = '\u001b[36m'

        output = "{}:\t\n".format(market_pair)
        output += 'indicators:\t'
        for indicator in results['indicators']:
            for i, analysis in enumerate(results['indicators'][indicator]):
                colour_code = normal_colour

                if analysis['result'].iloc[-1]['is_hot']:
                    colour_code = hot_colour

                if analysis['result'].iloc[-1]['is_cold']:
                    colour_code = cold_colour

                formatted_values = list()
                for signal in analysis['config']['signal']:
                    value = analysis['result'].iloc[-1][signal]
                    if isinstance(value, float):
                        formatted_values.append(format(value, '.8f'))
                    else:
                        formatted_values.append(value)
                    formatted_string = '/'.join(formatted_values)

                output += "{}{}: {}{} \t".format(
                    colour_code,
                    '{} #{}'.format(indicator, i),
                    formatted_string,
                    normal_colour
                )

        output += '\ninformants:\t'
        for informant in results['informants']:
            for i, analysis in enumerate(results['informants'][informant]):
                formatted_values = list()
                for signal in analysis['config']['signal']:
                    value = analysis['result'].iloc[-1][signal]
                    if isinstance(value, float):
                        formatted_values.append(format(value, '.8f'))
                    else:
                        formatted_values.append(value)
                    formatted_string = '/'.join(formatted_values)

                output += "{}: {} \t".format(
                    '{} #{}'.format(informant, i),
                    formatted_string
                )
        output += '\n\n'
        return output


    def _get_csv_output(self, results, market_pair):
        """Creates the csv to output to the CLI

        Args:
            results (dict): The result of the completed analysis

        Returns:
            str: Completed cli csv
        """

        output = str()
        for indicator_type in results:
            for indicator in results[indicator_type]:
                for i, analysis in enumerate(results[indicator_type][indicator]):
                    for signal in analysis['config']['signal']:
                        value = analysis['result'].iloc[-1][signal]
                        if isinstance(value, float):
                            value = format(value, '.8f')

                        is_hot = str()
                        if 'is_hot' in analysis['result'].iloc[-1]:
                            is_hot = str(analysis['result'].iloc[-1]['is_hot'])

                        is_cold = str()
                        if 'is_cold' in analysis['result'].iloc[-1]:
                            is_cold = str(analysis['result'].iloc[-1]['is_cold'])

                        new_output = ','.join([
                            market_pair,
                            indicator,
                            str(i),
                            value,
                            is_hot,
                            is_cold
                        ])

                        output += '\n{}'.format(new_output)

        return output


    def _get_json_output(self, results, market_pair):
        """Creates the JSON to output to the CLI

        Args:
            results (dict): The result of the completed analysis

        Returns:
            str: Completed JSON message
        """

        result_list = list()
        for indicator_type in results:
            for indicator in results[indicator_type]:
                for analysis in results[indicator_type][indicator]:
                    result_list.append(analysis['result'].to_dict(orient='records')[-1])

        output = {'pair': market_pair, indicator_type: result_list}
        output = json.dumps(output)
        output += '\n'
        return output
