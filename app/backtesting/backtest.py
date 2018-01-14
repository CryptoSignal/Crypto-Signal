
import matplotlib.pyplot as plt

from logs import configure_logging
from conf import Configuration
from backtesting.chart import Chart
from backtesting.strategy import BacktestingStrategy

import json

coins = ["ETH/BTC", "LTC/BTC", "XMR/BTC", "OMG/BTC", "XRP/BTC", "SC/BTC", "XEM/BTC", "DASH/BTC", "LSK/BTC",
         "GNT/BTC", "VTC/BTC", "ETC/BTC", "STRAT/BTC", "DGB/BTC"]

# Load settings and create the config object
config = Configuration()
settings = config.fetch_settings()

# Set up logger
configure_logging(settings['loglevel'], settings['log_mode'])

def main(coin):

    chart = Chart(coin, "1h", "bittrex", config.fetch_exchange_config())

    buy_strategy = {'currentprice': {
        'comparator': 'GT',
        'value': 'movingaverage9'
    }}

    sell_strategy = {'currentprice': {
        'comparator': 'LT',
        'value': 'movingaverage9'
    }}

    strategy = BacktestingStrategy(capital=1.0, pair=coin, trading_fee=0.0025, buy_strategy=buy_strategy,
                                   sell_strategy=sell_strategy, stop_loss=0.00001)

    candlesticks = chart.get_points()
    strategy.run(candlesticks)

    # chart.plot_indicators(bollinger=21, movingaverage=[9, 15])
    # chart.plot_trades(strategy.buys, strategy.sells)
    # plt.show()

    # closings = [[i, d.close] for i, d in enumerate(chart.get_points())]
    # indicators = chart.get_indicators(bollinger=21, movingaverage=[9, 15])

    print("Total Profit (" + coin + "): " + str(strategy.profit))


def backtest(coin_pair, period_length, capital, stop_loss, num_data_points, buy_strategy, sell_strategy, indicators={}):

    chart = Chart(coin_pair, period_length, "bittrex", config.fetch_exchange_config(), length=num_data_points)

    strategy = BacktestingStrategy(pair=coin_pair, capital=capital, buy_strategy=buy_strategy,
                                   sell_strategy=sell_strategy, trading_fee=0.0025, stop_loss=stop_loss)

    candlesticks = chart.get_points()
    strategy.run(candlesticks)

    closings = [[i, d.close] for i, d in enumerate(candlesticks)]
    indicators = chart.get_indicators(**indicators)

    result = {'buys': list(strategy.buys), 'sells': list(strategy.sells), 'closingPrices': closings,
              'indicators': indicators, 'profit': round(strategy.profit, 8)}

    return result

if __name__ == "__main__":
    for coin in coins:
        main(coin)
