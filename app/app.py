#!/usr/local/bin/python
"""Main app module
"""

import time
import sys
import concurrent.futures

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

    if settings['market_pairs']:
        market_pairs = settings['market_pairs']
        logger.info("Found configured markets: %s", market_pairs)
        market_data = exchange_interface.get_exchange_markets(markets=market_pairs)
    else:
        logger.info("No configured markets, using all available on exchange.")
        market_data = exchange_interface.get_exchange_markets()
        
    notifier = Notifier(config.notifiers, market_data)

    while True:
        for exchange in market_data:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:

                for chunk in split_market_data(market_data[exchange]):
                    market_data_chunk = dict()
                    market_data_chunk[exchange] = { key: market_data[exchange][key] for key in chunk }

                    executor.submit(run_analysis, config, exchange_interface, notifier, market_data_chunk, settings['output_mode'])

        logger.info("Sleeping for %s seconds", settings['update_interval'])        
        time.sleep(settings['update_interval'])

def run_analysis(config, exchange_interface, notifier, market_data, output_mode):
    behaviour = Behaviour(config, exchange_interface, notifier)

    behaviour.run(market_data, output_mode)

def split_market_data(market_data):
    if len(market_data.keys()) > 20:
        return list(chunks(list(market_data.keys()), 20))
    else:
        return [list(market_data.keys())]

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
