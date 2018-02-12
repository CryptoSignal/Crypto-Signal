#!/usr/local/bin/python
"""Main app module
"""

import time

import logs
import conf
import structlog

from exchange import ExchangeInterface
from notification import Notifier
from analysis import StrategyAnalyzer
from behaviour import Behaviour

def main():
    """Initializes the application
    """
     # Load settings and create the config object
    config = conf.Configuration()
    settings = config.settings

    # Set up logger
    logs.configure_logging(settings['loglevel'], settings['log_mode'])
    logger = structlog.get_logger()

    # Configure and run configured behaviour.
    exchange_interface = ExchangeInterface(config.exchanges)
    strategy_analyzer = StrategyAnalyzer()
    notifier = Notifier(config.notifiers)

    behaviour = Behaviour(
        config.behaviour,
        exchange_interface,
        strategy_analyzer,
        notifier
    )

    while True:
        behaviour.run(settings['market_pairs'])
        logger.info("Sleeping for %s seconds", settings['update_interval'])
        time.sleep(settings['update_interval'])

if __name__ == "__main__":
    main()
