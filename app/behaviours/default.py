""" Runs the default behaviour, which performs two functions...
1. Output the signal information to the prompt.
2. Notify users when a threshold is crossed.
"""

import ccxt
import structlog

class DefaultBehaviour():
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

        for exchange in market_data:
            for market_pair in market_data[exchange]:

                try:
                    one_day_historical_data = self.strategy_analyzer.get_historical_data(
                        market_data[exchange][market_pair]['symbol'],
                        exchange,
                        '1d'
                    )

                    five_minute_historical_data = self.strategy_analyzer.get_historical_data(
                        market_data[exchange][market_pair]['symbol'],
                        exchange,
                        '5m'
                    )

                    analyzed_data = {}

                    if self.behaviour_config['rsi']['enabled']:
                        analyzed_data['RSI'] = self.strategy_analyzer.analyze_rsi(
                            one_day_historical_data,
                            hot_thresh=self.behaviour_config['rsi']['hot'],
                            cold_thresh=self.behaviour_config['rsi']['cold']
                        )

                    if self.behaviour_config['sma']['enabled']:
                        analyzed_data['SMA'] = self.strategy_analyzer.analyze_sma(
                            one_day_historical_data,
                            hot_thresh=self.behaviour_config['sma']['hot'],
                            cold_thresh=self.behaviour_config['sma']['cold']
                        )

                    if self.behaviour_config['ema']['enabled']:
                        analyzed_data['EMA'] = self.strategy_analyzer.analyze_ema(
                            one_day_historical_data,
                            hot_thresh=self.behaviour_config['ema']['hot'],
                            cold_thresh=self.behaviour_config['ema']['cold']
                        )

                    if self.behaviour_config['breakout']['enabled']:
                        analyzed_data['Breakout'] = self.strategy_analyzer.analyze_breakout(
                            five_minute_historical_data,
                            hot_thresh=self.behaviour_config['breakout']['hot'],
                            cold_thresh=self.behaviour_config['breakout']['cold']
                        )

                    if self.behaviour_config['ichimoku']['enabled']:
                        analyzed_data['Ichimoku'] = self.strategy_analyzer.analyze_ichimoku_cloud(
                            one_day_historical_data,
                            hot_thresh=self.behaviour_config['ichimoku']['hot'],
                            cold_thresh=self.behaviour_config['ichimoku']['cold']
                        )

                    if self.behaviour_config['macd']['enabled']:
                        analyzed_data['MACD'] = self.strategy_analyzer.analyze_macd(
                            one_day_historical_data,
                            hot_thresh=self.behaviour_config['macd']['hot'],
                            cold_thresh=self.behaviour_config['macd']['cold']
                        )

                except ccxt.errors.RequestTimeout:
                    continue

                message = ""
                output = "{}: ".format(market_pair)
                for analysis in analyzed_data:
                    if self.behaviour_config[analysis.lower()]['alert_enabled']:
                        if analyzed_data[analysis]['is_hot']:
                            message += "{}: {} is hot!\n".format(analysis, market_pair)

                        if analyzed_data[analysis]['is_cold']:
                            message += "{}: {} is cold!\n".format(analysis, market_pair)

                    formatted_values = []
                    for value in analyzed_data[analysis]['values']:
                        if isinstance(value, float):
                            formatted_values.append(format(value, '.8f'))
                        else:
                            formatted_values.append(value)

                    formatted_string = '/'.join(formatted_values)
                    output += "{}: {}\t".format(analysis, formatted_string)

                if message:
                    self.notifier.notify_all(message)

                print(output)
