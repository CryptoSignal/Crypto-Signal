"""
Collect required information from exchanges
"""

from exchanges.bittrex import Bittrex

class ExchangeAggregator():
    """
    Collect required information from exchanges
    """
    def __init__(self, config):
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
