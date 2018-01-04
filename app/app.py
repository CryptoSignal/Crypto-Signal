#!/usr/local/bin/python
"""
Main
"""

import logs
import conf
import structlog
from behaviour import Behaviour

def main():
     # Load settings and create the config object
    config = conf.Configuration()
    settings = config.fetch_settings()

    # Set up logger
    logs.configure_logging(settings['loglevel'], settings['log_mode'])

    behaviour_manager = Behaviour(config)
    behaviour = behaviour_manager.get_behaviour(settings['selected_task'])

    behaviour.run(
        settings['market_pairs'],
        settings['update_interval'])

if __name__ == "__main__":
    main()
