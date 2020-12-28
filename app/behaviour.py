""" Runs the default analyzer, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import json
import os
import traceback
from copy import deepcopy

import numpy as np
import pandas as pd
import structlog
from ccxt import ExchangeError
from tenacity import RetryError

from analysis import StrategyAnalyzer
from outputs import Output


class Behaviour():
    """Default analyzer which gives users basic trading information.
    """

    def __init__(self, config, exchange_interface, notifier):
        """Initializes DefaultBehaviour class.

        Args:
            indicator_conf (dict): A dictionary of configuration for this analyzer.
            exchange_interface (ExchangeInterface): Instance of the ExchangeInterface class for
                making exchange queries.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
        """

        self.logger = structlog.get_logger()
        self.indicator_conf = config.indicators
        self.informant_conf = config.informants
        self.crossover_conf = config.crossovers
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = StrategyAnalyzer()
        self.notifier = notifier
        self.all_historical_data = dict()

        output_interface = Output()
        self.output = output_interface.dispatcher

        self.enable_charts = config.settings['enable_charts']
        self.timezone = config.settings['timezone']

    def run(self, market_data, output_mode):
        """The analyzer entrypoint

        Args:
            market_data (dict): Dict of exchanges and symbol pairs to operate on.
            output_mode (str): Which console output mode to use.
        """

        self.logger.info("Starting default analyzer...")

        self.logger.info("Using the following exchange(s): %s",
                         list(market_data.keys()))

        self.all_historical_data = self.get_all_historical_data(market_data)

        new_result = self._test_strategies(market_data, output_mode)

        self.notifier.set_timezone(self.timezone)

        if self.enable_charts:
            self.notifier.set_enable_charts(True)
            self.notifier.set_all_historical_data(self.all_historical_data)

        self.notifier.notify_all(new_result)

    def get_all_historical_data(self, market_data):
        """Get historical data for each exchange/market pair/candle period

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to get data.
        """

        indicator_dispatcher = self.strategy_analyzer.indicator_dispatcher()
        informant_dispatcher = self.strategy_analyzer.informant_dispatcher()

        data = dict()

        for exchange in market_data:
            self.logger.info("Getting data for %s", list(
                market_data[exchange].keys()))
            if exchange not in data:
                data[exchange] = dict()

            for market_pair in market_data[exchange]:
                if market_pair not in data[exchange]:
                    data[exchange][market_pair] = dict()

                for indicator in self.indicator_conf:
                    if indicator not in indicator_dispatcher:
                        self.logger.warn(
                            "No such indicator %s, skipping.", indicator)
                        continue

                    for indicator_conf in self.indicator_conf[indicator]:
                        if indicator_conf['enabled']:
                            candle_period = indicator_conf['candle_period']

                            if candle_period not in data[exchange][market_pair]:
                                data[exchange][market_pair][candle_period] = self._get_historical_data(
                                    market_pair,
                                    exchange,
                                    candle_period
                                )

                for informant in self.informant_conf:
                    if informant not in informant_dispatcher:
                        self.logger.warn(
                            "No such informant %s, skipping.", informant)
                        continue

                    for informant_conf in self.informant_conf[informant]:
                        if informant_conf['enabled']:
                            candle_period = informant_conf['candle_period']

                            if candle_period not in data[exchange][market_pair]:
                                data[exchange][market_pair][candle_period] = self._get_historical_data(
                                    market_pair,
                                    exchange,
                                    candle_period
                                )

        return data

    def _test_strategies(self, market_data, output_mode):
        """Test the strategies and perform notifications as required

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to analyze.
            output_mode (str): Which console output mode to use.
        """

        new_result = dict()
        for exchange in market_data:
            self.logger.info("Beginning analysis of %s", exchange)
            if exchange not in new_result:
                new_result[exchange] = dict()

            for market_pair in market_data[exchange]:
                self.logger.info("Beginning analysis of %s", market_pair)
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

                new_result[exchange][market_pair]['crossovers'] = self._get_crossover_results(
                    new_result[exchange][market_pair]
                )

                if output_mode in self.output:
                    output_data = deepcopy(new_result[exchange][market_pair])
                    print(
                        self.output[output_mode](output_data, market_pair),
                        end=''
                    )
                else:
                    self.logger.warn()

        # Print an empty line when complete
        print()
        return new_result

    def _get_indicator_results(self, exchange, market_pair):
        """Execute the indicator analysis on a particular exchange and pair.

        Args:
            exchange (str): The exchange to get the indicator results for.
            market_pair (str): The pair to get the market pair results for.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        indicator_dispatcher = self.strategy_analyzer.indicator_dispatcher()
        results = {indicator: list()
                   for indicator in self.indicator_conf.keys()}
        historical_data_cache = self.all_historical_data[exchange][market_pair]

        for indicator in self.indicator_conf:
            if indicator not in indicator_dispatcher:
                self.logger.warn("No such indicator %s, skipping.", indicator)
                continue

            for indicator_conf in self.indicator_conf[indicator]:
                if not indicator_conf['enabled']:
                    continue

                candle_period = indicator_conf['candle_period']

                # Exchange doesnt support such candle period
                if candle_period not in historical_data_cache:
                    continue

                if historical_data_cache[candle_period]:
                    analysis_args = {
                        'historical_data': historical_data_cache[candle_period],
                        'signal': indicator_conf['signal'],
                        'hot_thresh': indicator_conf['hot'] if 'hot' in indicator_conf else 0,
                        'cold_thresh': indicator_conf['cold'] if 'cold' in indicator_conf else 0
                    }

                    if 'period_count' in indicator_conf:
                        analysis_args['period_count'] = indicator_conf['period_count']

                    if indicator == 'rsi' and 'lrsi_filter' in indicator_conf:
                        analysis_args['lrsi_filter'] = indicator_conf['lrsi_filter']

                    if indicator == 'ma_ribbon':
                        analysis_args['pval_th'] = indicator_conf['pval_th'] if 'pval_th' in indicator_conf else 20
                        if 'ma_series' in indicator_conf:
                            series = indicator_conf['ma_series']
                            analysis_args['ma_series'] = [
                                int(i) for i in series.replace(' ', '').split(',')]
                        else:
                            analysis_args['ma_series'] = [5, 15, 25, 35, 45]

                    if indicator == 'ma_crossover':
                        analysis_args['exponential'] = indicator_conf['exponential'] if 'exponential' in indicator_conf else False
                        analysis_args['ma_fast'] = indicator_conf['ma_fast'] if 'ma_fast' in indicator_conf else 13
                        analysis_args['ma_slow'] = indicator_conf['ma_slow'] if 'ma_slow' in indicator_conf else 30

                    if indicator == 'stochrsi_cross':
                        analysis_args['smooth_k'] = indicator_conf['smooth_k'] if 'smooth_k' in indicator_conf else 10
                        analysis_args['smooth_d'] = indicator_conf['smooth_d'] if 'smooth_d' in indicator_conf else 3

                    if indicator == 'bollinger' or indicator == 'bbp':
                        analysis_args['std_dev'] = indicator_conf['std_dev'] if 'std_dev' in indicator_conf else 2

                    if indicator == 'klinger_oscillator':
                        analysis_args['ema_short_period'] = indicator_conf['vf_ema_short'] if 'vf_ema_short' in indicator_conf else 32
                        analysis_args['ema_long_period'] = indicator_conf['vf_ema_long'] if 'vf_ema_long' in indicator_conf else 55
                        analysis_args['signal_period'] = indicator_conf['kvo_signal'] if 'kvo_signal' in indicator_conf else 13

                    if indicator == 'ichimoku':
                        analysis_args['tenkansen_period'] = indicator_conf['tenkansen_period'] if 'tenkansen_period' in indicator_conf else 20
                        analysis_args['kijunsen_period'] = indicator_conf['kijunsen_period'] if 'kijunsen_period' in indicator_conf else 60
                        analysis_args['senkou_span_b_period'] = indicator_conf[
                            'senkou_span_b_period'] if 'senkou_span_b_period' in indicator_conf else 120

                    if indicator == 'candle_recognition':
                        analysis_args['candle_check'] = indicator_conf['candle_check'] if 'candle_check' in indicator_conf else 1
                        analysis_args['notification'] = indicator_conf['notification'] if 'notification' in indicator_conf else 'hot'
                    if indicator == 'aroon_oscillator':
                        analysis_args['sma_vol_period'] = indicator_conf['sma_vol_period'] if 'sma_vol_period' in indicator_conf else 50

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
        """Execute the informant analysis on a particular exchange and pair.

        Args:
            exchange (str): The exchange to get the indicator results for.
            market_pair (str): The pair to get the market pair results for.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        informant_dispatcher = self.strategy_analyzer.informant_dispatcher()
        results = {informant: list()
                   for informant in self.informant_conf.keys()}
        historical_data_cache = self.all_historical_data[exchange][market_pair]

        for informant in self.informant_conf:

            if informant not in informant_dispatcher:
                self.logger.warn("No such informant %s, skipping.", informant)
                continue

            for informant_conf in self.informant_conf[informant]:
                if not informant_conf['enabled']:
                    continue

                candle_period = informant_conf['candle_period']

                # Exchange doesnt support such candle period
                if candle_period not in historical_data_cache:
                    continue

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

    def _get_crossover_results(self, new_result):
        """Execute crossover analysis on the results so far.

        Args:
            new_result (dict): A dictionary containing the results of the informant and indicator
                analysis.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        crossover_dispatcher = self.strategy_analyzer.crossover_dispatcher()
        results = {crossover: list()
                   for crossover in self.crossover_conf.keys()}

        for crossover in self.crossover_conf:
            if crossover not in crossover_dispatcher:
                self.logger.warn("No such crossover %s, skipping.", crossover)
                continue

            for crossover_conf in self.crossover_conf[crossover]:
                if not crossover_conf['enabled']:
                    self.logger.debug("%s is disabled, skipping.", crossover)
                    continue

                key_indicator = new_result[crossover_conf['key_indicator_type']
                                           ][crossover_conf['key_indicator']][crossover_conf['key_indicator_index']]
                crossed_indicator = new_result[crossover_conf['crossed_indicator_type']
                                               ][crossover_conf['crossed_indicator']][crossover_conf['crossed_indicator_index']]

                crossover_conf['candle_period'] = crossover_conf['key_indicator'] + \
                    str(crossover_conf['key_indicator_index'])

                dispatcher_args = {
                    'key_indicator': key_indicator['result'],
                    'key_signal': crossover_conf['key_signal'],
                    'key_indicator_index': crossover_conf['key_indicator_index'],
                    'crossed_indicator': crossed_indicator['result'],
                    'crossed_signal': crossover_conf['crossed_signal'],
                    'crossed_indicator_index': crossover_conf['crossed_indicator_index']
                }

                results[crossover].append({
                    'result': crossover_dispatcher[crossover](**dispatcher_args),
                    'config': crossover_conf
                })
        return results

    def _get_historical_data(self, market_pair, exchange, candle_period):
        """Gets a list of OHLCV data for the given pair and exchange.

        Args:
            market_pair (str): The market pair to get the OHLCV data for.
            exchange (str): The exchange to get the OHLCV data for.
            candle_period (str): The timeperiod to collect for the given pair and exchange.

        Returns:
            list: A list of OHLCV data.
        """

        historical_data = list()
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
        """Get the results of performing technical analysis

        Args:
            dispatcher (dict): A dictionary of functions for performing TA.
            indicator (str): The name of the desired indicator.
            dispatcher_args (dict): A dictionary of arguments to provide the analyser
            market_pair (str): The market pair to analyse

        Returns:
            pandas.DataFrame: Returns a pandas.DataFrame of results or an empty string.
        """

        try:
            results = dispatcher[indicator](**dispatcher_args)
        except TypeError:
            self.logger.info(
                'Invalid type encountered while processing pair %s for indicator %s, skipping',
                market_pair,
                indicator
            )
            self.logger.info(traceback.format_exc())
            results = str()
        return results
