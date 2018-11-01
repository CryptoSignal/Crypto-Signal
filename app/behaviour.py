""" Runs the default analyzer, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import json
import traceback
import structlog
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

from matplotlib.dates import DateFormatter, DayLocator,HourLocator,  WeekdayLocator, MONDAY
from mpl_finance.mpl_finance import candlestick_ohlc

from copy import deepcopy
from ccxt import ExchangeError
from tenacity import RetryError

from analysis import StrategyAnalyzer
from outputs import Output
from analyzers.utils import IndicatorUtils

class Behaviour(IndicatorUtils):
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


    def run(self, market_data, output_mode):
        """The analyzer entrypoint

        Args:
            market_data (dict): Dict of exchanges and symbol pairs to operate on.
            output_mode (str): Which console output mode to use.
        """

        self.logger.info("Starting default analyzer...")

        self.logger.info("Using the following exchange(s): %s", list(market_data.keys()))

        self.all_historical_data = self.get_all_historical_data(market_data)

        self._create_charts(market_data)

        new_result = self._test_strategies(market_data, output_mode)

        self.notifier.notify_all(new_result)

    def get_all_historical_data(self, market_data):
        """Get historical data for each exchange/market pair/candle period

        Args:
            market_data (dict): A dictionary containing the market data of the symbols to get data.
        """

        indicator_dispatcher = self.strategy_analyzer.indicator_dispatcher()
        data = dict()

        for exchange in market_data:
            self.logger.info("Getting data of %s", exchange)
            if exchange not in data:
                data[exchange] = dict()

            for market_pair in market_data[exchange]:
                if market_pair not in data[exchange]:
                    data[exchange][market_pair] = dict()

                for indicator in self.indicator_conf:
                    if indicator not in indicator_dispatcher:
                        self.logger.warn("No such indicator %s, skipping.", indicator)
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
        results = { indicator: list() for indicator in self.indicator_conf.keys() }
        historical_data_cache = self.all_historical_data[exchange][market_pair]

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

                if candle_period in historical_data_cache:
                    self.logger.info('Reading candle data from cache for %s %s',indicator, indicator_conf['candle_period'])
                else:
                    self.logger.info('Re-Reading candle data from exchange for %s %s',indicator, indicator_conf['candle_period'])
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
        """Execute the informant analysis on a particular exchange and pair.

        Args:
            exchange (str): The exchange to get the indicator results for.
            market_pair (str): The pair to get the market pair results for.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

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


    def _get_crossover_results(self, new_result):
        """Execute crossover analysis on the results so far.

        Args:
            new_result (dict): A dictionary containing the results of the informant and indicator
                analysis.

        Returns:
            list: A list of dictinaries containing the results of the analysis.
        """

        crossover_dispatcher = self.strategy_analyzer.crossover_dispatcher()
        results = { crossover: list() for crossover in self.crossover_conf.keys() }

        for crossover in self.crossover_conf:
            if crossover not in crossover_dispatcher:
                self.logger.warn("No such crossover %s, skipping.", crossover)
                continue

            for crossover_conf in self.crossover_conf[crossover]:
                if not crossover_conf['enabled']:
                    self.logger.debug("%s is disabled, skipping.", crossover)
                    continue

                key_indicator = new_result[crossover_conf['key_indicator_type']][crossover_conf['key_indicator']][crossover_conf['key_indicator_index']]
                crossed_indicator = new_result[crossover_conf['crossed_indicator_type']][crossover_conf['crossed_indicator']][crossover_conf['crossed_indicator_index']]

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

    def _create_charts(self, market_data):
        """Create charts for each market_pair/candle_period

        Args:
            market_data (dict): A dictionary containing the market data of the symbols
        """

        for exchange in market_data:
            self.logger.info("Beginning chart creation for %s", exchange)

            for market_pair in market_data[exchange]:
                historical_data = self.all_historical_data[exchange][market_pair]

                for candle_period in historical_data:
                    self.logger.info('Creating chart for %s %s', market_pair, candle_period)


    def _create_chart(self, exchange, market_pair, candle_period):
        data = self.all_historical_data[exchange][market_pair][candle_period]

        df = self.convert_to_dataframe(data)

        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)

        textsize = 11
        left, width = 0.1, 0.8
        rect1 = [left, 0.6, width, 0.3]
        rect2 = [left, 0.3, width, 0.3]
        rect3 = [left, 0.1, width, 0.2]

        fig = plt.figure(facecolor='white')
        fig.set_size_inches(8, 12, forward=True)
        axescolor = '#f6f6f6'  # the axes background color

        ax1 = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
        ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax1)
        ax2t = ax2.twinx()
        ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax1)

        #'1h' 0.02 , max_locator -> 1
        # 4h -> 0.08, max_locator -> 8

        min_locator = 4
        max_locator = 1
        stick_width = 0.02

        ax1.set_ymargin(0.2)
        candlestick_ohlc(ax1, zip(mdates.date2num(df.index.to_pydatetime()),
                            df['open'], df['high'],
                            df['low'], df['close']),
                    width=stick_width, colorup='olivedrab', colordown='crimson')
                    

        # plot the relative strength indicator
        prices = df["close"]

        # plot the price and volume data
        #dx = r["Adj Close"] - r.Close
        #low = r.Low + dx
        #high = r.High + dx

        deltas = np.zeros_like(prices)
        deltas[1:] = np.diff(prices)
        up = deltas > 0
        #ax2.vlines(r.index[up], low[up], high[up], color='black', label='_nolegend_')
        #ax2.vlines(r.index[~up], low[~up], high[~up],color='black', label='_nolegend_')
        ma25 = self.moving_average(prices, 25, type='simple')
        ma7 = self.moving_average(prices, 7, type='simple')

        linema20, = ax1.plot(df.index, ma25, color='indigo', lw=0.5, label='MA (25)')
        linema200, = ax1.plot(df.index, ma7, color='orange', lw=0.5, label='MA (7)')
    
        ax1.text(0.04, 0.94, 'MA (7, close, 0)', color='orange', transform=ax1.transAxes, fontsize=textsize, va='top')
        ax1.text(0.24, 0.94, 'MA (25, close, 0)', color='indigo', transform=ax1.transAxes,  fontsize=textsize, va='top')

        rsi = self.relative_strength(prices)
        fillcolor = 'darkmagenta'

        ax2.plot(df.index, rsi, color=fillcolor, linewidth=0.5)
        ax2.axhline(70, color='darkmagenta', linestyle='dashed', alpha=0.6)
        ax2.axhline(30, color='darkmagenta', linestyle='dashed', alpha=0.6)
        ax2.fill_between(df.index, rsi, 70, where=(rsi >= 70),
                        facecolor=fillcolor, edgecolor=fillcolor)
        ax2.fill_between(df.index, rsi, 30, where=(rsi <= 30),
                        facecolor=fillcolor, edgecolor=fillcolor)
        ax2.set_ylim(0, 100)
        ax2.set_yticks([30, 70])
        ax2.text(0.024, 0.94, 'RSI (14)', va='top',
                transform=ax2.transAxes, fontsize=textsize)
        #ax1.set_title('%s daily' % ticker)    


        # compute the MACD indicator
        fillcolor = 'darkslategrey'
        nslow = 26
        nfast = 12
        nema = 9
        emaslow, emafast, macd = self.moving_average_convergence(
            prices, nslow=nslow, nfast=nfast)
        ema9 = self.moving_average(macd, nema, type='exponential')
        ax3.plot(df.index, macd, color='blue', lw=0.5)
        ax3.plot(df.index, ema9, color='red', lw=0.5)
        ax3.fill_between(df.index, macd - ema9, 0, alpha=0.4,
                        facecolor=fillcolor, edgecolor=fillcolor)

        ax3.text(0.024, 0.94, 'MACD (%d, %d, close, %d)' % (nfast, nslow, nema), va='top',
                transform=ax3.transAxes, fontsize=textsize)    


        for ax in ax1, ax2, ax2t, ax3:
            if ax != ax3:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                for label in ax.get_xticklabels():
                    label.set_rotation(30)
                    label.set_horizontalalignment('right')

            #ax.fmt_xdata = mdates.DateFormatter('%d/%b') #%d/%b  %Y-%m-%d
            #ax.xaxis.set_major_locator(DayLocator(interval=2))
            ax.xaxis.set_major_formatter(DateFormatter('%d/%b'))
            #for 4h is not useful
            #ax.xaxis.set_minor_locator(HourLocator(interval=min_locator))  #6 for 1h
            #ax.xaxis.set_minor_formatter(DateFormatter('%H:%M'))
            #ax.xaxis.set_tick_params(which='major', pad=15) 

        fig.autofmt_xdate()

        market_pair = market_pair.replace('/', '_').lower()
        chart_name = '{}_{}_{}.png'.format(exchange, market_pair, candle_period)

        plt.savefig(chart_name)        

    def relative_strength(self, prices, n=14):
        """
        compute the n period relative strength indicator
        http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
        http://www.investopedia.com/terms/r/rsi.asp
        """

        deltas = np.diff(prices)
        seed = deltas[:n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100. / (1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return rsi


    def moving_average(self, x, n, type='simple'):
        """
        compute an n period moving average.

        type is 'simple' | 'exponential'

        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a


    def moving_average_convergence(self, x, nslow=26, nfast=12):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and
        slow exponential moving avg

        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = self.moving_average(x, nslow, type='exponential')
        emafast = self.moving_average(x, nfast, type='exponential')
        return emaslow, emafast, emafast - emaslow
