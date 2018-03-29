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
                },
                'optional': {
                    'template': os.environ.get(
                        'NOTIFIERS_TWILIO_OPTIONAL_TEMPLATE',
                        "{{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}"
                    )
                }
            },

            'discord': {
                'required': {
                    'webhook': os.environ.get('NOTIFIERS_DISCORD_REQUIRED_WEBHOOK', None),
                    'username': os.environ.get('NOTIFIERS_DISCORD_REQUIRED_USERNAME', None)
                },
                'optional':{
                    'avatar': os.environ.get('NOTIFIERS_DISCORD_OPTIONAL_AVATAR', None),
                    'template': os.environ.get(
                        'NOTIFIERS_DISCORD_OPTIONAL_TEMPLATE',
                        "{{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}"
                    )
                }
            },

            'slack': {
                'required': {
                    'webhook': os.environ.get('NOTIFIERS_SLACK_REQUIRED_WEBHOOK', None)
                },
                'optional': {
                    'template': os.environ.get(
                        'NOTIFIERS_SLACK_OPTIONAL_TEMPLATE',
                        "{{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}"
                    )
                }
            },

            'gmail': {
                'required': {
                    'username': os.environ.get('NOTIFIERS_GMAIL_REQUIRED_USERNAME', None),
                    'password': os.environ.get('NOTIFIERS_GMAIL_REQUIRED_PASSWORD', None),
                    'destination_emails': self._string_splitter(
                        os.environ.get('NOTIFIERS_GMAIL_REQUIRED_DESTINATION_EMAILS', None)
                    )
                },
                'optional': {
                    'template': os.environ.get(
                        'NOTIFIERS_GMAIL_OPTIONAL_TEMPLATE',
                        "{{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}"
                    )
                }
            },

            'telegram': {
                'required': {
                    'token': os.environ.get('NOTIFIERS_TELEGRAM_REQUIRED_TOKEN', None),
                    'chat_id': os.environ.get('NOTIFIERS_TELEGRAM_REQUIRED_CHAT_ID', None)
                },
                'optional': {
                    'template': os.environ.get(
                        'NOTIFIERS_TELEGRAM_OPTIONAL_TEMPLATE',
                        "{{exchange}}-{{market}}-{{analyzer}}-{{analyzer_number}} is {{status}}!{{ '\n' -}}"
                    )
                }
            }
        }

        self.behaviour = {
            'momentum': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MOMENTUM_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MOMENTUM_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_MOMENTUM_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MOMENTUM_{}_HOT'.format(i), 0)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MOMENTUM_{}_COLD'.format(i), 0)),
                'candle_period': os.environ.get('BEHAVIOUR_MOMENTUM_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_MOMENTUM_{}_PERIOD_COUNT'.format(i), 10))
            } for i in range(int(os.environ.get('BEHAVIOUR_MOMENTUM_NUM_INDICATORS', 1)))],

            'rsi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_RSI_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_RSI_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_RSI_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_RSI_{}_HOT'.format(i), 30)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_RSI_{}_COLD'.format(i), 70)),
                'candle_period': os.environ.get('BEHAVIOUR_RSI_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_RSI_{}_PERIOD_COUNT'.format(i), 14))
            } for i in range(int(os.environ.get('BEHAVIOUR_RSI_NUM_INDICATORS', 1)))],

            'stoch_rsi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_HOT'.format(i), 20)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_COLD'.format(i), 80)),
                'candle_period': os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_{}_PERIOD_COUNT'.format(i), 14))
            } for i in range(int(os.environ.get('BEHAVIOUR_STOCHASTIC_RSI_NUM_INDICATORS', 1)))],

            'macd': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MACD_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MACD_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_MACD_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MACD_{}_HOT'.format(i), 0)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MACD_{}_COLD'.format(i), 0)),
                'candle_period': os.environ.get('BEHAVIOUR_MACD_{}_CANDLE_PERIOD'.format(i), '1d')
            } for i in range(int(os.environ.get('BEHAVIOUR_MACD_NUM_INDICATORS', 1)))],

            'macd_sl': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MACD_SL_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_MACD_SL_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_MACD_SL_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MACD_SL_{}_HOT'.format(i), 0)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_MACD_SL_{}_COLD'.format(i), 0)),
                'candle_period': os.environ.get('BEHAVIOUR_MACD_SL_{}_CANDLE_PERIOD'.format(i), '1d')
            } for i in range(int(os.environ.get('BEHAVIOUR_MACD_SL_NUM_INDICATORS', 1)))],

            'sma': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_SMA_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_{}_HOT'.format(i), 1)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_{}_COLD'.format(i), 1)),
                'candle_period': os.environ.get('BEHAVIOUR_SMA_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_SMA_{}_PERIOD_COUNT'.format(i), 15))
            } for i in range(int(os.environ.get('BEHAVIOUR_SMA_NUM_INDICATORS', 1)))],

            'sma_crossover': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_HOT'.format(i), 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_COLD'.format(i), 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': self._tuple_maker(
                    os.environ.get('BEHAVIOUR_SMA_CROSSOVER_{}_PERIOD_COUNT'.format(i), '15/21')
                )
            } for i in range(int(os.environ.get('BEHAVIOUR_SMA_CROSSOVER_NUM_INDICATORS', 1)))],

            'ema': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_EMA_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_{}_HOT'.format(i), 1)),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_{}_COLD'.format(i), 1)),
                'candle_period': os.environ.get('BEHAVIOUR_EMA_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('BEHAVIOUR_EMA_{}_PERIOD_COUNT'.format(i), 15))
            } for i in range(int(os.environ.get('BEHAVIOUR_EMA_NUM_INDICATORS', 1)))],

            'ema_crossover': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_HOT'.format(i), 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_COLD'.format(i), 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': self._tuple_maker(
                    os.environ.get('BEHAVIOUR_EMA_CROSSOVER_{}_PERIOD_COUNT'.format(i), '15/21')
                )
            } for i in range(int(os.environ.get('BEHAVIOUR_EMA_CROSSOVER_NUM_INDICATORS', 1)))],

            'ichimoku': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_ICHIMOKU_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_ICHIMOKU_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('BEHAVIOUR_ICHIMOKU_{}_ALERT_FREQUENCY'.format(i), 'always'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_ICHIMOKU_{}_HOT'.format(i), 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_ICHIMOKU_{}_COLD'.format(i), 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_ICHIMOKU_{}_CANDLE_PERIOD'.format(i), '1d')
            } for i in range(int(os.environ.get('BEHAVIOUR_ICHIMOKU_NUM_INDICATORS', 1)))],
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
