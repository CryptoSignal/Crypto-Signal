"""Load configuration from default-config.json or env
"""

import os
import json
import distutils.util
from string import whitespace

import ccxt # Only uses ccxt to get exchanges, never queries them.

class Configuration():
    """Parses the various forms of configuration to create the config objects.
    """
    def __init__(self):
        """Initializes the Configuration class
        """

        config = json.load(open('default-config.json'))

        for exchange in ccxt.exchanges:
            if not exchange in config['exchanges']:
                config['exchanges'][exchange] = {
                    'required': {'enabled': False},
                    'optional': {}
                }

        secrets_file = 'secrets.json'
        secrets = json.load(open(secrets_file)) if os.path.isfile(secrets_file) else {}
        config.update(secrets)

        self.settings = self.__merge_setting_opts(config['settings'])
        self.exchange_config = self.__merge_exchange_opts(config['exchanges'])
        self.notifier_config = self.__merge_notifier_opts(config['notifiers'])
        self.behaviour_config = config['behaviours']
        self.database_config = config['database']


    def __merge_setting_opts(self, settings):
        """Merges the config file settings config with environment variables.

        Args:
            settings (dict): A dictionary of settings from default-config.json

        Returns:
            dict: The updated settings config including the environment variables.
        """

        for setting_key, setting_val in settings.items():
            env_var_name = setting_key.upper()
            new_val = os.environ.get(env_var_name, setting_val)
            if isinstance(setting_val, list) and not isinstance(new_val, list):
                settings[setting_key] = self.__csv_to_list(new_val)
            if isinstance(setting_val, int) and not isinstance(new_val, int):
                settings[setting_key] = int(new_val)
            else:
                settings[setting_key] = new_val

        return settings


    def __merge_exchange_opts(self, exchange_settings):
        """Merges the config file exchange config with environment variables.

        Args:
            exchange_settings (dict): A dictionary of exchange config from default-config.json

        Returns:
            dict: The updated exchange config including the environment variables.
        """

        for exchange_key, exchange_val in exchange_settings.items():
            for option_key, option_val in exchange_settings[exchange_key].items():
                for setting_key, setting_val in exchange_settings[exchange_key][option_key].items():

                    env_var_name = '_'.join([
                        exchange_key.upper(),
                        option_key.upper(), setting_key.upper()
                        ])

                    new_val = os.environ.get(env_var_name, setting_val)

                    if setting_key == "enabled" and isinstance(new_val, str):
                        new_val = bool(distutils.util.strtobool(new_val))
                    if isinstance(setting_val, list) and not isinstance(new_val, list):
                        exchange_settings[exchange_key][option_key][setting_key] = self.__csv_to_list(new_val)
                    else:
                        exchange_settings[exchange_key][option_key][setting_key] = new_val

        return exchange_settings


    def __merge_notifier_opts(self, notifier_settings):
        """Merges the config file notifier config with environment variables.

        Args:
            notifier_settings (dict): A dictionary of notifier config from default-config.json

        Returns:
            dict: The updated notifier config including the environment variables.
        """

        for notifier_key, notifier_val in notifier_settings.items():
            for option_key, option_val in notifier_settings[notifier_key].items():
                for setting_key, setting_val in notifier_settings[notifier_key][option_key].items():
                    env_var_name = '_'.join([
                        notifier_key.upper(),
                        option_key.upper(),
                        setting_key.upper()])
                    new_val = os.environ.get(env_var_name, setting_val)
                    if isinstance(setting_val, list) and not isinstance(new_val, list):
                        notifier_settings[notifier_key][option_key][setting_key] = self.__csv_to_list(new_val)

                    else:
                        notifier_settings[notifier_key][option_key][setting_key] = new_val

        return notifier_settings


    def __csv_to_list(self, comma_separated_string):
        """Convert comma separated string into a list

        Args:
            comma_separated_string (str): Comma separated string to convert to list.

        Returns:
            list: List of values after being split.
        """

        return comma_separated_string.translate(str.maketrans('', '', whitespace)).split(",")


    def get_settings(self):
        """Get the general app settings

        Returns:
            dict: Dictionary containing general app config
        """

        return self.settings


    def get_exchange_config(self):
        """Get the exchange config

        Returns:
            dict: Dictionary containing exchange config
        """

        return self.exchange_config


    def get_notifier_config(self):
        """Get the notifier config

        Returns:
            dict: Dictionary containing notifier config
        """

        return self.notifier_config


    def get_database_config(self):
        """Get the database config

        Returns:
            dict: Dictionary containing database config
        """

        return self.database_config


    def get_behaviour_config(self, selected_behaviour):
        """Get the behaviour config

        Returns:
            dict: Dictionary containing behaviour config
        """

        return self.behaviour_config[selected_behaviour]
