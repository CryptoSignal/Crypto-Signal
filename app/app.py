#!/usr/local/bin/python
"""
Main
"""


import time
from string import whitespace

import logs
import conf
import structlog
from exchange import ExchangeInterface
from notification import Notifier
from analysis import StrategyAnalyzer

def main():
     # Load settings and create the config object
    config = conf.Configuration().fetch_configuration()
    print(config)
    exit()
    
    # Set up logger
    logs.configure_logging(config['settings']['loglevel'], config['settings']['app_mode'])
    logger = structlog.get_logger()

    exchange_interface = ExchangeInterface(config)
    strategy_analyzer = StrategyAnalyzer(config)
    notifier = Notifier(config)

    # The coin pairs
    coin_pairs = []
    if config['settings']['market_pairs']:
        coin_pairs = config['settings']['market_pairs'].translate(str.maketrans('', '', whitespace)).split(",")
    else:
        user_markets = exchange_interface.get_user_markets()
        for user_market in user_markets['info']:
            if 'BTC' in user_market['Currency']:
                continue
            market_pair = user_market['Currency'] + '/BTC'
            coin_pairs.append(market_pair)
    logger.debug(coin_pairs)

    while True:
        get_signal(coin_pairs, strategy_analyzer, notifier)

def get_signal(coin_pairs, strategy_analyzer, notifier):
    for coin_pair in coin_pairs:
        rsi_value = strategy_analyzer.analyze_rsi(coin_pair)
        sma_value, ema_value = strategy_analyzer.analyze_moving_averages(coin_pair)
        breakout_value, is_breaking_out = strategy_analyzer.analyze_breakout(coin_pair)
        ichimoku_span_a, ichimoku_span_b = strategy_analyzer.analyze_ichimoku_cloud(coin_pair)
        if is_breaking_out:
            notifier.notify_all(message="{} is breaking out!".format(coin_pair))

        print("{}: \tBreakout: {} \tRSI: {} \tSMA: {} \tEMA: {} \tIMA: {} \tIMB: {}".format(
            coin_pair,
            breakout_value,
            format(rsi_value, '.2f'),
            format(sma_value, '.7f'),
            format(ema_value, '.7f'),
            format(ichimoku_span_a, '.7f'),
            format(ichimoku_span_b, '.7f')))
    time.sleep(300)

if __name__ == "__main__":
    main()
