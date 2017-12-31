"""
Load configuration
"""

import os
import json


class Configuration():
    def __init__(self):
        self.config = json.load(open('default-config.json'))
        secrets = {}
        if os.path.isfile('config.json'):
            secrets = json.load(open('config.json'))
        
        self.config.update(secrets)

        for key, setting in self.config['settings'].items():
            self.config['settings'][key] = os.environ.get(key.upper(), setting)
        
        for exchange_key, exchange_val in self.config['exchanges'].items():
            for option_key, option_val in self.config['exchanges'][exchange_key].items():
                for setting_key, setting_val in self.config['exchanges'][exchange_key][option_key].items():
                    env_var_name = '_'.join([exchange_key.upper(), option_key.upper(), setting_key.upper()])
                    self.config['exchanges'][exchange_key][option_key][setting_key] = os.environ.get(env_var_name, setting_val)
        
        for  notifier_key, notifier_val in self.config['notifiers'].items():
            for option_key, option_val in self.config['notifiers'][notifier_key].items():
                for setting_key, setting_val in self.config['notifiers'][notifier_key][option_key].items():
                    env_var_name = '_'.join([notifier_key.upper(), option_key.upper(), setting_key.upper()])
                    self.config['notifiers'][notifier_key][option_key][setting_key] = os.environ.get(env_var_name, setting_val)

    def fetch_configuration(self):
        return self.config
