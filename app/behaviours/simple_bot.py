
import structlog
import ccxt

class SimpleBot():
    def __init__(self, behaviour_config):
        self.logger = structlog.get_logger()
        self.behaviour_config = behaviour_config
    
    def run(self, market_pairs, update_interval, exchange_interface, strategy_analyzer, notifier):
        if market_pairs:
            market_data = exchange_interface.get_symbol_markets(market_pairs)
        else:
            market_data = exchange_interface.get_exchange_markets()

        rsi_data = {}
        for exchange in market_data:
            rsi_data[exchange] = {}
            for market_pair in market_data[exchange]:
                try:
                  rsi_data[exchange][market_pair] = strategy_analyzer.analyze_rsi(
                      market_data[exchange][market_pair]['symbol'],
                      exchange,
                      self.behaviour_config['trade_parameters']['buy']['rsi_threshold'],
                      self.behaviour_config['trade_parameters']['sell']['rsi_threshold'])
                except ccxt.NetworkError:
                  self.logger.warn("Read timeout getting data for %s on %s skipping", market_pair, exchange)
                  continue
        
        print(rsi_data)
