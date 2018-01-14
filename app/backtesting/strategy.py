import random

import matplotlib.pyplot as plt

import structlog
from backtesting.trade import Trade
from backtesting.indicators import BacktestingIndicators
from backtesting.decision import Decision

'''
BackTesting Strategy
'''
class BacktestingStrategy(object):
    def __init__(self, pair, capital, buy_strategy, sell_strategy, trading_fee=0, stop_loss=0):
        self.output = structlog.get_logger()
        self.prices = []
        self.trades = []
        self.sells = []
        self.buys = []
        self.max_trades_at_once = 1
        self.indicators = BacktestingIndicators
        self.profit = 0
        self.pair = pair
        self.reserve = capital
        self.buy_strategy = buy_strategy
        self.sell_stategy = sell_strategy
        self.trading_fee = trading_fee
        self.stop_loss = stop_loss

    '''
    Runs our backtesting strategy on the set of backtesting candlestick data
    '''
    def run(self, candlesticks):

        # Samples a random price within the range [candlestick.open, candlestick.close]
        sample_price = lambda op, close: random.uniform(min(op, close), max(op, close))

        self.prices = [sample_price(candle.open, candle.close) for candle in candlesticks]

        rsi = self.indicators.historical_rsi(self.prices)
        nine_period = self.indicators.historical_moving_average(self.prices, 9)
        fifteen_period = self.indicators.historical_moving_average(self.prices, 15)
        bb1, bb2 = self.indicators.historical_bollinger_bands(self.prices)
        bb_diff = bb1 - bb2


        for i in range(len(self.prices)):

            decision = Decision({'currentprice': self.prices[i], 'rsi': rsi[i], 'movingaverage9': nine_period[i], 'movingaverage15': fifteen_period[i]})

            open_trades = [trade for trade in self.trades if trade.status == 'OPEN']

            ### CHECK TO SEE IF WE CAN OPEN A BUY POSITION
            if len(open_trades) < self.max_trades_at_once:
                if decision.should_buy(self.buy_strategy):
                    assert self.reserve > 0

                    self.buys.append((i, self.prices[i]))
                    new_trade = Trade(self.pair, self.prices[i], self.reserve * (1 - self.trading_fee),
                                      stop_loss=self.stop_loss)
                    self.reserve = 0
                    self.trades.append(new_trade)

            ### CHECK TO SEE IF WE NEED TO SELL ANY OPEN POSITIONS
            for trade in open_trades:
                if decision.should_sell(self.sell_stategy):

                    self.sells.append((i, self.prices[i]))
                    profit, total = trade.close(self.prices[i])
                    self.profit += profit * (1 - self.trading_fee)
                    self.reserve = total * (1 - self.trading_fee)

            ### CHECK TO SEE IF WE HAVE ACTIVATED A STOP LOSS
            for trade in self.trades:

                # Check our stop losses
                if trade.status == "OPEN" and trade.stop_loss and self.prices[i] < trade.stop_loss:
                    profit, total = trade.close(self.prices[i])
                    self.sells.append((i, self.prices[i]))
                    self.profit += profit * (1 - self.trading_fee)
                    self.reserve = total * (1 - self.trading_fee)

    def show_positions(self):
        for trade in self.trades:
            trade.show_trade()
