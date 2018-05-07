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
            default_config = yaml.load(config_file)

        if os.path.isfile('config.yml'):
            with open('config.yml', 'r') as config_file:
                user_config = yaml.load(config_file)
        else:
            user_config = dict()

        config = {**default_config, **user_config}

        self.settings = config['settings']

        self.notifiers = config['notifiers']

        self.indicators = config['indicators']

        self.informants = config['informants']

        self.crossovers = config['crossovers']

        if config['exchanges'] == None:
            self.exchanges = dict()
        else:
            self.exchanges = config['exchanges']

        for exchange in ccxt.exchanges:
            if exchange not in self.exchanges:
                self.exchanges[exchange] = {
                    'required': {
                        'enabled': False
                    }
                }
