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
                running analysis on exchange information.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
        """

        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier

    def run(self, market_pairs):
        """The behaviour entrypoint

        Args:
            market_pairs (list): List of symbol pairs to operate on, if empty get all pairs.
        """

        if market_pairs:
            market_data = self.exchange_interface.get_symbol_markets(market_pairs)
        else:
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

                    rsi_data = self.strategy_analyzer.analyze_rsi(
                        one_day_historical_data,
                        hot_thresh=self.behaviour_config['rsi']['hot'],
                        cold_thresh=self.behaviour_config['rsi']['cold']
                    )

                    sma_data = self.strategy_analyzer.analyze_sma(
                        one_day_historical_data,
                        hot_thresh=self.behaviour_config['sma']['hot'],
                        cold_thresh=self.behaviour_config['sma']['cold']
                    )

                    ema_data = self.strategy_analyzer.analyze_ema(
                        one_day_historical_data,
                        hot_thresh=self.behaviour_config['ema']['hot'],
                        cold_thresh=self.behaviour_config['ema']['cold']
                    )

                    breakout_data = self.strategy_analyzer.analyze_breakout(
                        five_minute_historical_data,
                        hot_thresh=self.behaviour_config['breakout']['hot'],
                        cold_thresh=self.behaviour_config['breakout']['cold']
                    )

                    ichimoku_data = self.strategy_analyzer.analyze_ichimoku_cloud(
                        one_day_historical_data,
                        hot_thresh=self.behaviour_config['ichimoku']['hot'],
                        cold_thresh=self.behaviour_config['ichimoku']['cold']
                    )

                    macd_data = self.strategy_analyzer.analyze_macd(
                        one_day_historical_data,
                        hot_thresh=self.behaviour_config['macd']['hot'],
                        cold_thresh=self.behaviour_config['macd']['cold']
                    )

                except ccxt.errors.RequestTimeout:
                    continue

                message = ""
                if breakout_data['is_hot']:
                    message += "Breakout: {} is breaking out!\n".format(market_pair)

                if rsi_data['is_cold']:
                    message += "RSI: {} is over bought!\n".format(market_pair)
                elif rsi_data['is_hot']:
                    message += "RSI: {} is over sold!\n".format(market_pair)

                if macd_data['is_hot']:
                    message += "MACD: {} trend is good according to MACD!\n".format(market_pair)
                if macd_data['is_cold']:
                    message += "MACD: {} trend is poor according to MACD!\n".format(market_pair)

                if sma_data['is_hot']:
                    message += "SMA: {} is trending well according to SMA!\n".format(market_pair)

                if ema_data['is_hot']:
                    message += "EMA: {} is trending well according to EMA!\n".format(market_pair)

                if ichimoku_data['is_hot']:
                    message += "IMC: {} is trending well according to Ichimoku!\n".format(market_pair)

                if message:
                    self.notifier.notify_all(message)

                print("{}: \tBreakout: {} \tRSI: {} \tSMA: {} \tEMA: {} \tIMC: {} \tMACD: {}".format(
                    market_pair,
                    breakout_data['values'][0],
                    format(rsi_data['values'][0], '.2f'),
                    format(sma_data['values'][0], '.7f'),
                    format(ema_data['values'][0], '.7f'),
                    format(ichimoku_data['values'][0], '.7f') + "/" + format(ichimoku_data['values'][1], '.7f'),
                    format(macd_data['values'][0], '.7f')))
