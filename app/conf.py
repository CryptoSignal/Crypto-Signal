"""
Load configuration
"""

import os
import json
import distutils.util
from string import whitespace

import ccxt

class Configuration():
    def __init__(self):
        self.config = json.load(open('default-config.json'))

        for exchange in ccxt.exchanges:
            if not exchange in self.config['exchanges']:
                self.config['exchanges'][exchange] = {'required': {'enabled': False}, 'optional': {}}

        secrets_file = 'secrets.json'
        secrets = json.load(open(secrets_file)) if os.path.isfile(secrets_file) else {}
        self.config.update(secrets)

        for setting_key, setting_val in self.config['settings'].items():
            env_var_name = setting_key.upper()
            new_val = os.environ.get(env_var_name, setting_val)
            if isinstance(setting_val, list) and not isinstance(new_val, list):
                self.config['settings'][setting_key] = self._csv_to_list(new_val)
            else:
                self.config['settings'][setting_key] = new_val

        for exchange_key, exchange_val in self.config['exchanges'].items():
            for option_key, option_val in self.config['exchanges'][exchange_key].items():
                for setting_key, setting_val in self.config['exchanges'][exchange_key][option_key].items():
                    env_var_name = '_'.join([exchange_key.upper(), option_key.upper(), setting_key.upper()])
                    new_val = os.environ.get(env_var_name, setting_val)
                    if setting_key == "enabled" and isinstance(new_val, str):
                        new_val = bool(distutils.util.strtobool(new_val))
                    if isinstance(setting_val, list) and not isinstance(new_val, list):
                        self.config['exchanges'][exchange_key][option_key][setting_key] = self._csv_to_list(new_val)
                    else:
                        self.config['exchanges'][exchange_key][option_key][setting_key] = new_val

        for  notifier_key, notifier_val in self.config['notifiers'].items():
            for option_key, option_val in self.config['notifiers'][notifier_key].items():
                for setting_key, setting_val in self.config['notifiers'][notifier_key][option_key].items():
                    env_var_name = '_'.join([notifier_key.upper(), option_key.upper(), setting_key.upper()])
                    new_val = os.environ.get(env_var_name, setting_val)
                    if isinstance(setting_val, list) and not isinstance(new_val, list):
                        self.config['notifiers'][notifier_key][option_key][setting_key] = self._csv_to_list(new_val)
                    else:
                        self.config['notifiers'][notifier_key][option_key][setting_key] = new_val

        self.settings = self.config['settings']
        self.exchange_config = self.config['exchanges']
        self.notifier_config = self.config['notifiers']

    def _csv_to_list(self, comma_separated_string):
        return comma_separated_string.translate(str.maketrans('', '', whitespace)).split(",")

    def fetch_settings(self):
        return self.settings

    def fetch_exchange_config(self):
        return self.exchange_config

    def fetch_notifier_config(self):
        return self.notifier_config
