from behaviours.ui.backtesting.chart import Chart
from behaviours.ui.backtesting.strategy import BacktestingStrategy

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
