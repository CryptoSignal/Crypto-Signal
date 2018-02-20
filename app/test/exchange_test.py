import unittest

from exchange import ExchangeInterface

class ExchangeTests(unittest.TestCase):
    def setUp(self):

        exchange_config = {'bittrex': {
                               'required': {
                                   'enabled': True
                                }
                            },
                            'binance': {
                                'required': {
                                    'enabled': True
                                }
                            }}

        self.interface = ExchangeInterface(exchange_config)

    def test_get_historical_data_bad_time_period(self):
        with self.assertRaises(ValueError):
            self.interface.get_historical_data("ETH/BTC", "bittrex", "7m")
            self.interface.get_historical_data("XMR/BTC", "bittrex", "4d")
            self.interface.get_historical_data("XRP/BTC", "binance", "asdf")

    def test_get_historical_data_max_periods(self):
        data = self.interface.get_historical_data("ETH/BTC", "bittrex", "5m")
        self.assertTrue(len(data) <= 100)

        data = self.interface.get_historical_data("XRP/BTC", "binance", "1d", max_periods=50)
        self.assertTrue(len(data) <= 50)

        data = self.interface.get_historical_data("OMG/BTC", "binance", "1w", max_periods=3)
        self.assertTrue(len(data) <= 3)

    def test_get_historical_data_ordered_properly(self):
        data = self.interface.get_historical_data("LTC/BTC", "bittrex", "1h", max_periods=50)
        self.assertTrue(sorted(data, key=lambda d: d[0]) == data)

        data = self.interface.get_historical_data("LSK/BTC", "bittrex", "30m", max_periods=50)
        self.assertTrue(sorted(data, key=lambda d: d[0]) == data)

    def test_get_historical_data_returns_recent_timestamp(self):
        from time import time

        # The timestamp on the last candle should be from the last 24 hours
        oneday = 60 * 60 * 24

        data = self.interface.get_historical_data("LTC/BTC", "bittrex", "1d")
        last_timestamp = data[-1][0] / 1000.0
        self.assertTrue(last_timestamp >= time() - oneday)

        data = self.interface.get_historical_data("LTC/BTC", "binance", "1d")
        last_timestamp = data[-1][0] / 1000.0
        self.assertTrue(last_timestamp >= time() - oneday)
