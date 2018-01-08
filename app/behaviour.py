
import structlog

from exchange import ExchangeInterface
from notification import Notifier
from analysis import StrategyAnalyzer
from database import DatabaseHandler
from behaviours.default import DefaultBehaviour
from behaviours.rsi_bot import RSIBot


class Behaviour():
    def __init__(self, config):
        self.config = config


    def get_behaviour(self, selected_behaviour):
        behaviour_config = self.config.fetch_behaviour_config(selected_behaviour)

        if selected_behaviour == 'default':
            behaviour = self.configure_default(behaviour_config)

        if selected_behaviour == 'rsi_bot':
            behaviour = self.configure_rsi_bot(behaviour_config)

        return behaviour


    def configure_default(self, behaviour_config):
        exchange_interface = ExchangeInterface(self.config.fetch_exchange_config())

        strategy_analyzer = StrategyAnalyzer(
            exchange_interface,
            self.config.fetch_analysis_config()
            )
        
        notifier = Notifier(self.config.fetch_notifier_config())

        behaviour = DefaultBehaviour(
            behaviour_config,
            exchange_interface,
            strategy_analyzer,
            notifier
            )

        return behaviour


    def configure_rsi_bot(self, behaviour_config):
        exchange_interface = ExchangeInterface(self.config.fetch_exchange_config())
        strategy_analyzer = StrategyAnalyzer(
            exchange_interface,
            self.config.fetch_analysis_config()
            )
        notifier = Notifier(self.config.fetch_notifier_config())
        db_handler = DatabaseHandler(self.config.fetch_database_config())

        behaviour = RSIBot(
            behaviour_config,
            exchange_interface,
            strategy_analyzer,
            notifier,
            db_handler)

        return behaviour
