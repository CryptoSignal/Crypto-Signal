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
                        "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
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
                        "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
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
                        "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
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
                        "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
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
                        "{{exchange}}-{{market}}-{{indicator}}-{{indicator_number}} is {{status}}!{{ '\n' -}}"
                    )
                }
            }
        }

        self.indicators = {
            'momentum': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_MOMENTUM_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_MOMENTUM_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('INDICATOR_MOMENTUM_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'signal': self._string_splitter(os.environ.get('INDICATOR_MOMENTUM_{}_SIGNAL'.format(i), ['momentum'])),
                'hot': self._hot_cold_typer(os.environ.get('INDICATOR_MOMENTUM_{}_HOT'.format(i), 0)),
                'cold': self._hot_cold_typer(os.environ.get('INDICATOR_MOMENTUM_{}_COLD'.format(i), 0)),
                'candle_period': os.environ.get('INDICATOR_MOMENTUM_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INDICATOR_MOMENTUM_{}_PERIOD_COUNT'.format(i), 10))
            } for i in range(int(os.environ.get('INDICATOR_MOMENTUM_NUM_INDICATORS', 1)))],

            'mfi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_MFI_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_MFI_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('INDICATOR_MFI_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'signal': self._string_splitter(os.environ.get('INDICATOR_MOMENTUM_{}_SIGNAL'.format(i), ['mfi'])),
                'hot': self._hot_cold_typer(os.environ.get('INDICATOR_MFI_{}_HOT'.format(i), 0)),
                'cold': self._hot_cold_typer(os.environ.get('INDICATOR_MFI_{}_COLD'.format(i), 0)),
                'candle_period': os.environ.get('INDICATOR_MFI_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INDICATOR_MFI_{}_PERIOD_COUNT'.format(i), 10))
            } for i in range(int(os.environ.get('INDICATOR_MFI_NUM_INDICATORS', 1)))],

            'rsi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_RSI_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_RSI_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('INDICATOR_RSI_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'signal': self._string_splitter(os.environ.get('INDICATOR_MOMENTUM_{}_SIGNAL'.format(i), ['rsi'])),
                'hot': self._hot_cold_typer(os.environ.get('INDICATOR_RSI_{}_HOT'.format(i), 30)),
                'cold': self._hot_cold_typer(os.environ.get('INDICATOR_RSI_{}_COLD'.format(i), 70)),
                'candle_period': os.environ.get('INDICATOR_RSI_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INDICATOR_RSI_{}_PERIOD_COUNT'.format(i), 14))
            } for i in range(int(os.environ.get('INDICATOR_RSI_NUM_INDICATORS', 1)))],

            'stoch_rsi': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'signal': self._string_splitter(os.environ.get('INDICATOR_MOMENTUM_{}_SIGNAL'.format(i), ['stoch_rsi'])),
                'hot': self._hot_cold_typer(os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_HOT'.format(i), 20)),
                'cold': self._hot_cold_typer(os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_COLD'.format(i), 80)),
                'candle_period': os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INDICATOR_STOCHASTIC_RSI_{}_PERIOD_COUNT'.format(i), 14))
            } for i in range(int(os.environ.get('INDICATOR_STOCHASTIC_RSI_NUM_INDICATORS', 1)))],

            'macd': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_MACD_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('INDICATOR_MACD_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('INDICATOR_MACD_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'signal': self._string_splitter(os.environ.get('INDICATOR_MOMENTUM_{}_SIGNAL'.format(i), ['macd'])),
                'hot': self._hot_cold_typer(os.environ.get('INDICATOR_MACD_{}_HOT'.format(i), 0)),
                'cold': self._hot_cold_typer(os.environ.get('INDICATOR_MACD_{}_COLD'.format(i), 0)),
                'candle_period': os.environ.get('INDICATOR_MACD_{}_CANDLE_PERIOD'.format(i), '1d')
            } for i in range(int(os.environ.get('INDICATOR_MACD_NUM_INDICATORS', 1)))],

            'ichimoku': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_ICHIMOKU_{}_ENABLED'.format(i), 'True')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('BEHAVIOUR_ICHIMOKU_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'signal': self._string_splitter(os.environ.get('INFORMANT_ICHIMOKU_{}_SIGNAL'.format(i), ['leading_span_a', 'leading_span_b'])),
                'alert_frequency': os.environ.get('BEHAVIOUR_ICHIMOKU_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'hot': self._hot_cold_typer(os.environ.get('BEHAVIOUR_ICHIMOKU_{}_HOT'.format(i), 'True')),
                'cold': self._hot_cold_typer(os.environ.get('BEHAVIOUR_ICHIMOKU_{}_COLD'.format(i), 'True')),
                'candle_period': os.environ.get('BEHAVIOUR_ICHIMOKU_{}_CANDLE_PERIOD'.format(i), '1d')
            } for i in range(int(os.environ.get('BEHAVIOUR_ICHIMOKU_NUM_INDICATORS', 1)))]
        }

        self.informants = {
            'vwap': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INFORMANT_VWAP_{}_ENABLED'.format(i), 'True')
                )),
                'signal': self._string_splitter(os.environ.get('INFORMANT_VWAP_{}_SIGNAL'.format(i), ['vwap'])),
                'candle_period': os.environ.get('INFORMANT_VWAP_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INFORMANT_VWAP_{}_PERIOD_COUNT'.format(i), 15))
            } for i in range(int(os.environ.get('INFORMANT_VWAP_NUM_INDICATORS', 1)))],

            'sma': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INFORMANT_SMA_{}_ENABLED'.format(i), 'True')
                )),
                'signal': self._string_splitter(os.environ.get('INFORMANT_SMA_{}_SIGNAL'.format(i), ['sma'])),
                'candle_period': os.environ.get('INFORMANT_SMA_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INFORMANT_SMA_{}_PERIOD_COUNT'.format(i), 15))
            } for i in range(int(os.environ.get('INFORMANT_SMA_NUM_INDICATORS', 1)))],

            'ema': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INFORMANT_EMA_{}_ENABLED'.format(i), 'True')
                )),
                'signal': self._string_splitter(os.environ.get('INFORMANT_EMA_{}_SIGNAL'.format(i), ['ema'])),
                'candle_period': os.environ.get('INFORMANT_EMA_{}_CANDLE_PERIOD'.format(i), '1d'),
                'period_count': int(os.environ.get('INFORMANT_EMA_{}_PERIOD_COUNT'.format(i), 15))
            } for i in range(int(os.environ.get('INFORMANT_EMA_NUM_INDICATORS', 1)))],

            'bollinger_bands': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('INFORMANT_BOL_BAND_{}_ENABLED'.format(i), 'True')
                )),
                'signal': self._string_splitter(os.environ.get('INFORMANT_BOL_BAND_{}_SIGNAL'.format(i), ['upperband', 'middleband', 'lowerband'])),
                'candle_period': os.environ.get('INFORMANT_BOL_BAND_{}_CANDLE_PERIOD'.format(i), '1d')
            } for i in range(int(os.environ.get('INFORMANT_BOL_BAND_NUM_INDICATORS', 1)))]
        }

        self.crossovers = {
            'std_crossover': [{
                'enabled': bool(distutils.util.strtobool(
                    os.environ.get('CROSSOVER_STD_CROSSOVER_{}_ENABLED'.format(i), 'False')
                )),
                'alert_enabled': bool(distutils.util.strtobool(
                    os.environ.get('CROSSOVER_STD_CROSSOVER_{}_ALERT_ENABLED'.format(i), 'True')
                )),
                'alert_frequency': os.environ.get('CROSSOVER_STD_CROSSOVER_{}_ALERT_FREQUENCY'.format(i), 'once'),
                'key_indicator': os.environ.get('CROSSOVER_STD_CROSSOVER_{}_KEY_INDICATOR'.format(i), 'ema'),
                'key_indicator_index': int(os.environ.get('CROSSOVER_STD_CROSSOVER_{}_KEY_INDICATOR_INDEX'.format(i), 0)),
                'key_indicator_type': os.environ.get('CROSSOVER_STD_CROSSOVER_{}_KEY_INDICATOR_TYPE'.format(i), 'informants'),
                'key_signal': os.environ.get('CROSSOVER_STD_CROSSOVER_{}_KEY_SIGNAL'.format(i), 'ema'),
                'crossed_indicator': os.environ.get('CROSSOVER_STD_CROSSOVER_{}_CROSSED_INDICATOR'.format(i), 'sma'),
                'crossed_indicator_index': int(os.environ.get('CROSSOVER_STD_CROSSOVER_{}_CROSSED_INDICATOR_INDEX'.format(i), 0)),
                'crossed_indicator_type': os.environ.get('CROSSOVER_STD_CROSSOVER_{}_CROSSED_INDICATOR_TYPE'.format(i), 'informants'),
                'crossed_signal': os.environ.get('INDICATOR_EMA_CROSSOVER_{}_CROSSED_SIGNAL'.format(i), 'sma')
            } for i in range(int(os.environ.get('CROSSOVER_STD_CROSSOVER_NUM_INDICATORS', 1)))]
        }

        self.exchanges = dict()
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
