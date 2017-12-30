"""
Collect required information from exchanges
"""

import ccxt.async as ccxt

class ExchangeInterface():
    """
    Collect required information from exchanges
    """
    def __init__(self, config):
        exchanges = []
        for exchange in config['exchanges']:
            exchanges.append(getattr(ccxt, exchange))
        print(exchanges[0].load_markets())
    '''
        self.bittrex_client = Bittrex(
            config['exchanges']['bittrex']['required']['key'],
            config['exchanges']['bittrex']['required']['secret'])

    def get_historical_data(self, coin_pair, period_count, time_unit):
        """
        Get history data
        """
        return self.bittrex_client.get_historical_data(coin_pair, period_count, time_unit)

    def get_user_markets(self):
        """
        Get user market balances
        """
        return self.bittrex_client.get_balances()
    '''
