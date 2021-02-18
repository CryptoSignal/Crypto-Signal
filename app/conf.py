"""Load configuration from environment
"""

import os

import ccxt
import yaml


class Configuration():
    """Parses the environment configuration to create the config objects.
    """

    def __init__(self):
        """Initializes the Configuration class
        """

        with open('defaults.yml', 'r') as config_file:
            default_config = yaml.load(config_file, Loader=yaml.FullLoader)

        if os.path.isfile('config.yml'):
            with open('config.yml', 'r') as config_file:
                user_config = yaml.load(config_file, Loader=yaml.FullLoader)
        else:
            user_config = dict()

        if 'settings' in user_config:
            self.settings = {
                **default_config['settings'], **user_config['settings']}
        else:
            self.settings = default_config['settings']

        if 'notifiers' in user_config:
            self.notifiers = {
                **default_config['notifiers'], **user_config['notifiers']}
        else:
            self.notifiers = default_config['notifiers']

        if 'indicators' in user_config:
            self.indicators = {
                **default_config['indicators'], **user_config['indicators']}
        else:
            self.indicators = default_config['indicators']

        if 'informants' in user_config:
            self.informants = {
                **default_config['informants'], **user_config['informants']}
        else:
            self.informants = default_config['informants']

        if 'crossovers' in user_config:
            self.crossovers = {
                **default_config['crossovers'], **user_config['crossovers']}
        else:
            self.crossovers = default_config['crossovers']

        if 'exchanges' in user_config:
            self.exchanges = user_config['exchanges']
        else:
            self.exchanges = dict()
        
        if 'conditionals' in user_config:
            self.conditionals = user_config['conditionals']
        else:
            self.conditionals = None

        for exchange in ccxt.exchanges:
            if exchange not in self.exchanges:
                self.exchanges[exchange] = {
                    'required': {
                        'enabled': False
                    }
                }
