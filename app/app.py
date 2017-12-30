#!/usr/local/bin/python
"""
Main
"""

import os
import json
import time
import logging
from string import whitespace

from exchange import ExchangeInterface
from notification import Notifier
from analysis import StrategyAnalyzer

# Let's test an API call to get our BTC balance as a test
# print(BITTREX_CLIENT.get_balance('BTC')['result']['Balance'])

#print(historical_data = BITTREX_CLIENT.get_historical_data('BTC-ETH', 30, "thirtyMin"))

def main():
     # Load settings and create the config object
    secrets = {}
    if os.path.isfile('secrets.json'):
        secrets = json.load(open('secrets.json'))
    config = json.load(open('default-config.json'))

    config.update(secrets)

    config['settings']['market_pairs'] = os.environ.get('MARKET_PAIRS', config['settings']['market_pairs'])
    config['settings']['loglevel'] = os.environ.get('LOGLEVEL', logging.INFO)
    config['exchanges']['bittrex']['required']['key'] = os.environ.get('BITTREX_KEY', config['exchanges']['bittrex']['required']['key'])
    config['exchanges']['bittrex']['required']['secret'] = os.environ.get('BITTREX_SECRET', config['exchanges']['bittrex']['required']['secret'])
    config['notifiers']['twilio']['required']['key'] = os.environ.get('TWILIO_KEY', config['notifiers']['twilio']['required']['key'])
    config['notifiers']['twilio']['required']['secret'] = os.environ.get('TWILIO_SECRET', config['notifiers']['twilio']['required']['secret'])
    config['notifiers']['twilio']['required']['sender_number'] = os.environ.get('TWILIO_SENDER_NUMBER', config['notifiers']['twilio']['required']['sender_number'])
    config['notifiers']['twilio']['required']['receiver_number'] = os.environ.get('TWILIO_RECEIVER_NUMBER', config['notifiers']['twilio']['required']['receiver_number'])
    config['notifiers']['gmail']['required']['username'] = os.environ.get('GMAIL_USERNAME', config['notifiers']['gmail']['required']['username'])
    config['notifiers']['gmail']['required']['password'] = os.environ.get('GMAIL_PASSWORD', config['notifiers']['gmail']['required']['password'])
    config['notifiers']['gmail']['required']['destination_emails'] = os.environ.get('GMAIL_DESTINATION_EMAILS', config['notifiers']['gmail']['required']['destination_emails'])

    # Set up logger
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(config['settings']['loglevel'])

    LOG_FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_HANDLE = logging.StreamHandler()
    LOG_HANDLE.setLevel(logging.DEBUG)
    LOG_HANDLE.setFormatter(LOG_FORMAT)
    LOGGER.addHandler(LOG_HANDLE)

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
    LOGGER.debug(coin_pairs)

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
