#!/usr/local/bin/python
"""Main app module
"""

import time
import sys
import concurrent.futures

import logs
import conf
import structlog

from threading import Thread
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
        
#    notifier = Notifier(config.notifiers, market_data)

    thread_list = []

    for exchange in market_data:
        num = 1
        for chunk in split_market_data(market_data[exchange]):
            market_data_chunk = dict()
            market_data_chunk[exchange] = { key: market_data[exchange][key] for key in chunk }

            notifier = Notifier(config.notifiers, market_data_chunk)
            behaviour = Behaviour(config, exchange_interface, notifier)

            workerName = "Worker-{}".format(num)
            worker = AnalysisWorker(workerName, behaviour, notifier, market_data_chunk, settings, logger)
            thread_list.append(worker)
            worker.daemon = True
            worker.start()

            time.sleep(60)
            num += 1

    logger.info('All workers are running!')

    for worker in thread_list:
        worker.join()

def split_market_data(market_data):
    if len(market_data.keys()) > 20:
        return list(chunks(list(market_data.keys()), 20))
    else:
        return [list(market_data.keys())]

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

class AnalysisWorker(Thread):

    def __init__(self, threadName, behaviour, notifier, market_data, settings, logger):
        Thread.__init__(self)

        self.threadName = threadName
        self.behaviour = behaviour
        self.notifier = notifier
        self.market_data = market_data
        self.settings = settings
        self.logger = logger

    def run(self):
        while True:
            self.logger.info('Starting %s', self.threadName)
            self.behaviour.run(self.market_data, self.settings['output_mode'])
            self.logger.info("%s sleeping for %s seconds", self.threadName, self.settings['update_interval'])
            time.sleep(self.settings['update_interval'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
