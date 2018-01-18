
import matplotlib.pyplot as plt

from logs import configure_logging
from conf import Configuration
from behaviours.ui.backtesting.chart import Chart
from behaviours.ui.backtesting.strategy import BacktestingStrategy

# Sample coin pairs to backtest with
coins = ["ETH/BTC", "LTC/BTC", "XMR/BTC", "OMG/BTC", "XRP/BTC", "SC/BTC", "XEM/BTC", "DASH/BTC", "LSK/BTC",
         "GNT/BTC", "VTC/BTC", "ETC/BTC", "STRAT/BTC", "DGB/BTC"]

"""
A Backtesting engine
"""
class Backtester(object):
    def __init__(self, coin_pair, period_length, exchange_name, exchange_interface, capital, stop_loss,
                 start_time, buy_strategy, sell_strategy, indicators={}):

        self.chart = Chart(coin_pair, period_length, exchange_name, exchange_interface, start_time=start_time)

        self.strategy = BacktestingStrategy(pair=coin_pair, capital=capital, buy_strategy=buy_strategy,
                                       sell_strategy=sell_strategy, trading_fee=0.0025, stop_loss=stop_loss)

        self.indicators = indicators

    '''
    Run our backtesting strategy on the set of historical data parsed as candlesticks
    '''
    def run(self):
        candlesticks = self.chart.get_points()
        self.strategy.run(candlesticks)

    '''
    Return the results of our backtesting execution
    '''
    def get_results(self):
        closings = [[i, d.close] for i, d in enumerate(self.chart.get_points())]
        indicators = self.chart.get_indicators(**self.indicators)

        results = {'buys': list(self.strategy.buys), 'sells': list(self.strategy.sells), 'closingPrices': closings,
                  'indicators': indicators, 'profit': round(self.strategy.profit, 8)}

        return results


# Sample main method
def main(coin):

    buy_strategy = {'currentprice': {
        'comparator': 'GT',
        'value': 'movingaverage9'
    }}

    sell_strategy = {'currentprice': {
        'comparator': 'LT',
        'value': 'movingaverage9'
    }}

    backtester = Backtester(coin, "1h", "bittrex", capital=1.0, stop_loss=0.0001, buy_strategy=buy_strategy,
                            sell_strategy=sell_strategy)

    backtester.run()

    # chart.plot_indicators(bollinger=21, movingaverage=[9, 15])
    # chart.plot_trades(strategy.buys, strategy.sells)
    # plt.show()

    # closings = [[i, d.close] for i, d in enumerate(chart.get_points())]
    # indicators = chart.get_indicators(bollinger=21, movingaverage=[9, 15])

    print("Total Profit (" + coin + "): " + str(backtester.strategy.profit))


if __name__ == "__main__":
    for coin in coins:
        main(coin)
