import unittest

from test.analysis.bollinger_test import BollingerTests
from test.analysis.ema_test import EMATests
from test.analysis.ichimoku_test import IchimokuTests
from test.analysis.macd_test import MACDTests
from test.analysis.rsi_test import RSITests
from test.analysis.sma_test import SMATests

from test.exchange_test import ExchangeTests


def generate_test_suite():
    suite = unittest.TestSuite()

    # Add Bollinger tests to suite
    add_bollinger_tests(suite)

    # Add EMA tests to suite
    add_ema_tests(suite)

    # Add Ichimoku tests to suite
    add_ichimoku_tests(suite)

    # Add MACD tests to suite
    add_macd_tests(suite)

    # Add RSI tests to suite
    add_rsi_tests(suite)

    # Add SMA tests to suite
    add_sma_tests(suite)

    # ---------------------- #

    # Add ExchangeInterface tests to suite
    add_exchange_tests(suite)

    return suite

def add_bollinger_tests(suite):
    suite.addTest(BollingerTests('test_bollinger_standard'))

def add_ema_tests(suite):
    suite.addTest(EMATests('test_ema_9_period'))
    suite.addTest(EMATests('test_ema_15_period'))
    suite.addTest(EMATests('test_ema_21_period'))
    suite.addTest(EMATests('test_ema_not_enough_data'))

def add_ichimoku_tests(suite):
    suite.addTest(IchimokuTests('test_ichimoku_standard'))

def add_macd_tests(suite):
    suite.addTest(MACDTests('test_macd_standard'))
    suite.addTest(MACDTests('test_macd_hot'))
    suite.addTest(MACDTests('test_macd_cold'))
    suite.addTest(MACDTests('test_macd_not_enough_data'))

def add_rsi_tests(suite):
    suite.addTest(RSITests('test_rsi_9_period'))
    suite.addTest(RSITests('test_rsi_14_period'))
    suite.addTest(RSITests('test_rsi_21_period'))
    suite.addTest(RSITests('test_rsi_hot'))
    suite.addTest(RSITests('test_rsi_not_enough_data'))

def add_sma_tests(suite):
    suite.addTest(SMATests('test_sma_9_period'))
    suite.addTest(SMATests('test_sma_15_period'))
    suite.addTest(SMATests('test_sma_21_period'))
    suite.addTest(SMATests('test_sma_not_enough_data'))

def add_exchange_tests(suite):
    suite.addTest(ExchangeTests('test_get_historical_data_bad_time_period'))
    suite.addTest(ExchangeTests('test_get_historical_data_max_periods'))
    suite.addTest(ExchangeTests('test_get_historical_data_ordered_properly'))
    suite.addTest(ExchangeTests('test_get_historical_data_returns_recent_timestamp'))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(generate_test_suite())
