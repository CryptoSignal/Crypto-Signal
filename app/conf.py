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
                    'required': {
                        'enabled': False
                    }
                }

        user_config_file = 'config.json'
        user_config = json.load(open(user_config_file)) if os.path.isfile(user_config_file) else {}
        config.update(user_config)

        config['settings'] = self.__parse_config(config['settings'], 'SETTINGS')
        self.settings = config['settings']

        config['database'] = self.__parse_config(config['database'], 'DATABASE')
        self.database = config['database']

        config['exchanges'] = self.__parse_config(config['exchanges'], 'EXCHANGES')
        self.exchanges = config['exchanges']

        config['notifiers'] = self.__parse_config(config['notifiers'], 'NOTIFIERS')
        self.notifiers = config['notifiers']

        config['behaviours'] = self.__parse_config(config['behaviours'], 'BEHAVIOURS')
        self.behaviours = config['behaviours']

    def __parse_config(self, config_fragment, base_path=""):
        for key in config_fragment:
            if isinstance(config_fragment[key], dict):
                key_path = '_'.join([base_path, key.upper()])
                config_fragment[key] = self.__parse_config(config_fragment[key], key_path)

            elif isinstance(config_fragment[key], list):
                key_path = '_'.join([base_path, key.upper()])
                new_value = os.environ.get(key_path, config_fragment[key])
                if isinstance(new_value, str):
                    new_value = new_value.translate(str.maketrans('', '', whitespace)).split(",")
                config_fragment[key] = new_value

            elif isinstance(config_fragment[key], bool):
                key_path = '_'.join([base_path, key.upper()])
                new_value = os.environ.get(key_path, config_fragment[key])
                if isinstance(new_value, str):
                    new_value = bool(distutils.util.strtobool(new_value))
                config_fragment[key] = new_value

            elif isinstance(config_fragment[key], str):
                key_path = '_'.join([base_path, key.upper()])
                config_fragment[key] = str(os.environ.get(key_path, config_fragment[key]))

            elif isinstance(config_fragment[key], int):
                key_path = '_'.join([base_path, key.upper()])
                new_value = os.environ.get(key_path, config_fragment[key])

                success = True
                try:
                    new_value = int(new_value)
                except ValueError:
                    success = False

                try:
                    if not success:
                        new_value = float(new_value)
                        success = True
                except ValueError:
                    success = False

                if not success:
                    new_value = bool(distutils.util.strtobool(new_value))

                config_fragment[key] = new_value

            elif isinstance(config_fragment[key], float):
                key_path = '_'.join([base_path, key.upper()])
                new_value = os.environ.get(key_path, config_fragment[key])

                success = True
                try:
                    new_value = float(new_value)
                except ValueError:
                    success = False
                    pass

                if not success:
                    new_value = bool(distutils.util.strtobool(new_value))

                config_fragment[key] = new_value

        return config_fragment
