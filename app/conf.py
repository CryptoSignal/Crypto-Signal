"""
Load configuration
"""

import os
import json
import distutils.util
from string import whitespace

import ccxt # Only uses ccxt to get exchanges, never queries them.

class Configuration():
    def __init__(self):
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
        for setting_key, setting_val in settings.items():
            env_var_name = setting_key.upper()
            new_val = os.environ.get(env_var_name, setting_val)
            if isinstance(setting_val, list) and not isinstance(new_val, list):
                settings[setting_key] = self.__csv_to_list(new_val)
            else:
                settings[setting_key] = new_val

        return settings


    def __merge_exchange_opts(self, exchange_settings):
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
        return comma_separated_string.translate(str.maketrans('', '', whitespace)).split(",")


    def fetch_settings(self):
        return self.settings


    def fetch_exchange_config(self):
        return self.exchange_config


    def fetch_notifier_config(self):
        return self.notifier_config


    def fetch_database_config(self):
        return self.database_config


    def fetch_behaviour_config(self, selected_behaviour):
        return self.behaviour_config[selected_behaviour]
