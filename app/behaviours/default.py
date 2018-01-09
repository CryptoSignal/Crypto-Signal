
import time

import ccxt
import structlog

class DefaultBehaviour():
    def __init__(self, behaviour_config, exchange_interface, strategy_analyzer, notifier):
        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.strategy_analyzer = strategy_analyzer
        self.notifier = notifier

    def run(self, market_pairs, update_interval):
        if market_pairs:
            market_data = self.exchange_interface.get_symbol_markets(market_pairs)
        else:
            market_data = self.exchange_interface.get_exchange_markets()

        while True:
            self.test_strategies(market_data)
            time.sleep(update_interval)

    def test_strategies(self, market_data):
        for exchange in market_data:
            for market_pair in market_data[exchange]:

                try:
                    rsi_data = self.strategy_analyzer.analyze_rsi(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                        )

                    ma_data = self.strategy_analyzer.analyze_moving_averages(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                        )

                    breakout_data = self.strategy_analyzer.analyze_breakout(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                        )

                    ichimoku_data = self.strategy_analyzer.analyze_ichimoku_cloud(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                        )
                    
                    macd_data = self.strategy_analyzer.analyze_macd(
                        market_data[exchange][market_pair]['symbol'],
                        exchange
                        )

                # bandaid fixes
                except ccxt.errors.RequestTimeout:
                    continue

                if breakout_data['is_breaking_out']:
                    self.notifier.notify_all(
                        message="{} is breaking out!".format(market_pair)
                        )

                if rsi_data['is_overbought']:
                    self.notifier.notify_all(
                        message="{} is over bought!".format(market_pair)
                        )

                elif rsi_data['is_oversold']:
                    self.notifier.notify_all(
                        message="{} is over sold!".format(market_pair)
                        )

                if ma_data['is_sma_trending']:
                    self.notifier.notify_all(
                        message="{} is trending well according to SMA!".format(market_pair)
                        )

                if ma_data['is_ema_trending']:
                    self.notifier.notify_all(
                        message="{} is trending well according to EMA!".format(market_pair)
                        )

                if ichimoku_data['is_ichimoku_trending']:
                    self.notifier.notify_all(
                        message="{} is trending well according to Ichimoku!".format(
                            market_pair
                            )
                        )

                print("{}: \tBreakout: {} \tRSI: {} \tSMA: {} \tEMA: {} \tIMA: {} \tIMB: {} \tMACD: {}".format(
                    market_pair,
                    breakout_data['value'],
                    format(rsi_data['value'], '.2f'),
                    format(ma_data['sma_value'], '.7f'),
                    format(ma_data['ema_value'], '.7f'),
                    format(ichimoku_data['span_a_value'], '.7f'),
                    format(ichimoku_data['span_b_value'], '.7f'),
                    format(macd_data['value'], '.7f')))

                #time.sleep(self.exchange_interface.exchanges[exchange].rateLimit / 1000)
