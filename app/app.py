#!/usr/local/bin/python
"""
Main
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
     # Load settings and create the config object
    config = conf.Configuration()
    settings = config.fetch_settings()
    exchange_config = config.fetch_exchange_config()
    notifier_config = config.fetch_notifier_config()
    behaviour_config = config.fetch_behaviour_config()

    # Set up logger
    logs.configure_logging(settings['loglevel'], settings['log_mode'])

    exchange_interface = ExchangeInterface(exchange_config)
    strategy_analyzer = StrategyAnalyzer(exchange_interface)
    notifier = Notifier(notifier_config)
    behaviour_manager = Behaviour(behaviour_config)

    behaviour = behaviour_manager.get_behaviour(settings['selected_task'])

    behaviour.run(
        settings['market_pairs'],
        settings['update_interval'],
        exchange_interface,
        strategy_analyzer,
        notifier)

if __name__ == "__main__":
    main()
