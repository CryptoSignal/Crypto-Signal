#!/usr/local/bin/python
"""Main app module
"""

import time
import sys

import logs
import conf
import structlog

from conf import Configuration
from exchange import ExchangeInterface
from notification import Notifier
from behaviour import Behaviour

def main():
    """Initializes the application
    """
     # Load settings and create the config object
    config = Configuration()
    settings = config.settings

    # Set up logger
    logs.configure_logging(settings['log_level'], settings['log_mode'])
    logger = structlog.get_logger()

    # Configure and run configured behaviour.
    exchange_interface = ExchangeInterface(config.exchanges)
    notifier = Notifier(config.notifiers)

    behaviour = Behaviour(
        config,
        exchange_interface,
        notifier
    )

    while True:
        behaviour.run(settings['market_pairs'], settings['output_mode'])
        logger.info("Sleeping for %s seconds", settings['update_interval'])
        time.sleep(settings['update_interval'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
