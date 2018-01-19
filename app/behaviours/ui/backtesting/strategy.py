import random

import matplotlib.pyplot as plt

import structlog
from behaviours.ui.backtesting.trade import Trade
from analysis import StrategyAnalyzer
from behaviours.ui.backtesting.decision import Decision

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
        self.indicators = StrategyAnalyzer(exchange_interface=None)
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

        # The zero's are to take up space since our indicators require a full dataframe of OHLC datas
        self.prices = [[0, 0, 0, 0, sample_price(candle.open, candle.close), 0] for candle in candlesticks]

        rsi = self.indicators.analyze_rsi(self.prices, all_data=True)
        nine_period = self.indicators.analyze_sma(self.prices, period_count=9, all_data=True)
        fifteen_period = self.indicators.analyze_sma(self.prices, period_count=15, all_data=True)
        nine_period_ema = self.indicators.analyze_ema(self.prices, period_count=9, all_data=True)


        for i in range(len(self.prices)):

            # Get the (sampled) closing price
            current_price = self.prices[i][4]

            decision = Decision({'currentprice': current_price, 'rsi': rsi[i]["values"], 'sma9': nine_period[i]["values"],
                                 'sma15': fifteen_period[i]["values"], 'ema9': nine_period_ema[i]["values"]})

            open_trades = [trade for trade in self.trades if trade.status == 'OPEN']

            ### CHECK TO SEE IF WE CAN OPEN A BUY POSITION
            if len(open_trades) < self.max_trades_at_once:
                if decision.should_buy(self.buy_strategy):
                    assert self.reserve > 0

                    self.buys.append((i, current_price))
                    new_trade = Trade(self.pair, current_price, self.reserve * (1 - self.trading_fee),
                                      stop_loss=self.stop_loss)
                    self.reserve = 0
                    self.trades.append(new_trade)

            ### CHECK TO SEE IF WE NEED TO SELL ANY OPEN POSITIONS
            for trade in open_trades:
                if decision.should_sell(self.sell_stategy):

                    self.sells.append((i, current_price))
                    profit, total = trade.close(current_price)
                    self.profit += profit * (1 - self.trading_fee)
                    self.reserve = total * (1 - self.trading_fee)

            ### CHECK TO SEE IF WE HAVE ACTIVATED A STOP LOSS
            for trade in self.trades:

                # Check our stop losses
                if trade.status == "OPEN" and trade.stop_loss and current_price < trade.stop_loss:
                    profit, total = trade.close(current_price)
                    self.sells.append((i, current_price))
                    self.profit += profit * (1 - self.trading_fee)
                    self.reserve = total * (1 - self.trading_fee)

    def show_positions(self):
        for trade in self.trades:
            trade.show_trade()
