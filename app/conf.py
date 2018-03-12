"""Load configuration from environment
"""

import os
import distutils.util
from string import whitespace

import ccxt

class Configuration():
    """Parses the environment configuration to create the config objects.
    """

    def __init__(self):
        """Initializes the Configuration class
        """

        self.settings = {
            'log_mode': os.environ.get('SETTINGS_LOG_MODE', 'text'),
            'log_level': os.environ.get('SETTINGS_LOG_LEVEL', 'INFO'),
            'output_mode': os.environ.get('SETTINGS_OUTPUT_MODE', 'cli'),
            'update_interval': int(os.environ.get('SETTINGS_UPDATE_INTERVAL', 300)),
            'market_pairs': self._string_splitter(os.environ.get('SETTINGS_MARKET_PAIRS', None))
        }

        self.notifiers = {
            'twilio': {
                'required': {
                    'key': os.environ.get('NOTIFIERS_TWILIO_REQUIRED_KEY', None),
                    'secret': os.environ.get('NOTIFIERS_TWILIO_REQUIRED_SECRET', None),
                    'sender_number': os.environ.get('NOTIFIERS_TWILIO_REQUIRED_SENDER_NUMBER', None),
                    'receiver_number': os.environ.get('NOTIFIERS_TWILIO_REQUIRED_RECEIVER_NUMBER', None)
                }
            },

            'discord': {
                'required': {
                    'webhook': os.environ.get('NOTIFIERS_DISCORD_REQUIRED_WEBHOOK', None),
                    'username': os.environ.get('NOTIFIERS_DISCORD_REQUIRED_USERNAME', None)
                },
                'optional':{
                    'avatar': os.environ.get('NOTIFIERS_DISCORD_OPTIONAL_AVATAR', None)
                }
            },

            'slack': {
                'required': {
                    'webhook': os.environ.get('NOTIFIERS_SLACK_REQUIRED_WEBHOOK', None)
                }
            },

            'gmail': {
                'required': {
                    'username': os.environ.get('NOTIFIERS_GMAIL_REQUIRED_USERNAME', None),
                    'password': os.environ.get('NOTIFIERS_GMAIL_REQUIRED_PASSWORD', None),
                    'destination_emails': self._string_splitter(
                        os.environ.get('NOTIFIERS_GMAIL_REQUIRED_DESTINATION_EMAILS', None)
                    )
                }
            },

            'telegram': {
                'required': {
                    'token': os.environ.get('NOTIFIERS_TELEGRAM_REQUIRED_TOKEN', None),
                    'chat_id': os.environ.get('NOTIFIERS_TELEGRAM_REQUIRED_CHAT_ID', None)
                }
            }
        }

        self.behaviour = {
            'momentum': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MOMENTUM_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MOMENTUM_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_MOMENTUM_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MOMENTUM_HOT', 0)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MOMENTUM_COLD', 0)),
                'candle_period': os.environ.get('BEHAVIOUR_MOMENTUM_CANDLE_PERIOD', '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_MOMENTUM_PERIOD_COUNT', 10))
            }],

            'rsi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_RSI_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_RSI_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_RSI_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_RSI_HOT', 30)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_RSI_COLD', 70)),
                'candle_period': os.environ.get('BEHAVIOUR_RSI_CANDLE_PERIOD', '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_RSI_PERIOD_COUNT', 14))
            }],

            'stoch_rsi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_HOT', 20)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_COLD', 80)),
                'candle_period': os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_CANDLE_PERIOD', '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_PERIOD_COUNT', 14))
            }],

            'macd': {
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MACD_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MACD_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_MACD_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MACD_HOT', 0)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MACD_COLD', 0)),
                'candle_period': os.environ.get('BEHAVIOUR_MACD_CANDLE_PERIOD', '1d')
            },

            'sma': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_SMA_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_HOT', 1)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_COLD', 1)),
                'candle_period': os.environ.get('BEHAVIOUR_SMA_CANDLE_PERIOD', '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_SMA_PERIOD_COUNT', 15))
            }],

            'sma_crossover': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_CROSSOVER_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_CROSSOVER_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_SMA_CROSSOVER_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_CROSSOVER_HOT', 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_CROSSOVER_COLD', 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_SMA_CROSSOVER_CANDLE_PERIOD', '1d'),
                'period_count': self._tuple_maker(os.environ.get('BEHAVIOUR_SMA_CROSSOVER_PERIOD_COUNT', '15/21'))
            }],

            'ema': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_EMA_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_HOT', 1)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_COLD', 1)),
                'candle_period': os.environ.get('BEHAVIOUR_EMA_CANDLE_PERIOD', '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_EMA_PERIOD_COUNT', 15))
            }],

            'ema_crossover': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_CROSSOVER_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_CROSSOVER_ALERT_ENABLED', 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_EMA_CROSSOVER_ALERT_FREQUENCY', 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_CROSSOVER_HOT', 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_CROSSOVER_COLD', 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_EMA_CROSSOVER_CANDLE_PERIOD', '1d'),
                'period_count': self._tuple_maker(os.environ.get('BEHAVIOUR_EMA_CROSSOVER_PERIOD_COUNT', '15/21'))
            }],

            'ichimoku': {
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_ICHIMOKU_ENABLED', 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_ICHIMOKU_ALERT_ENABLED', 'True')
                )),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_ICHIMOKU_HOT', 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_ICHIMOKU_COLD', 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_ICHIMOKU_CANDLE_PERIOD', '1d')
            },
        }

        self.exchanges = {}
        for exchange in ccxt.exchanges:
            exchange_var_name = 'EXCHANGES_' + exchange.upper() + '_REQUIRED_ENABLED'
            self.exchanges[exchange] = {
                'required': {
                    'enabled': bool(distutils.util.strtobool(
                        os.environ.get(exchange_var_name, 'False')
                    )),
                }
            }

    def _tuple_maker(self, string):
        """Splits a string into an n-tuple.

        Args:
            string (str): A string that can potentially be split into a tuple.

        Returns:
            list: An n-tuple of ints if each string in the tuple is castable to int
                  An n-tuple of strings if the each string in the tuple is uncastable to int
        """

        if isinstance(string, str):
            strlist = string.split("/")
            try:
                return tuple(int(s) for s in strlist)
            except ValueError:
                return tuple(strlist)

        return string,

    def _string_splitter(self, string):
        """Splits a string into a list.

        Args:
            string (str): A string that can potentially be split into a list.

        Returns:
            list: A list of strings if the values in the list are not castable to int,
                  A list of ints if the values in the list are castable to int
        """

        if isinstance(string, str):
            strlist = string.translate(str.maketrans('', '', whitespace)).split(",")

            # Try to cast each string to an integer, or return the list if it is uncastable
            try:
                return [int(elem) for elem in strlist]
            except ValueError:
                return strlist

        return string


    def _hot_cold_typer(self, hot_cold):
        """Attempt to infer the type of the hot or cold option.

        Args:
            hot_cold (float|string): A float, stringified float or stringified bool

        Returns:
            float|bool: Float or bool after type conversion.
        """

        if hot_cold == '':
            hot_cold = None
        else:
            try:
                hot_cold = float(hot_cold)
            except ValueError:
                hot_cold = bool(distutils.util.strtobool(hot_cold))
        return hot_cold
