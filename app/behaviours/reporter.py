"""Run reports from the database information.
"""

import structlog
from tabulate import tabulate

class ReporterBehaviour():
    """Run reports from the database information.
    """

    def __init__(self, behaviour_config, exchange_interface,
                 notifier, db_handler):
        """Initialize ReporterBehaviour class.

        Args:
            behaviour_config (dict): A dictionary of configuration for this behaviour.
            exchange_interface (ExchangeInterface): Instance of the ExchangeInterface class for
                making exchange queries.
            notifier (Notifier): Instance of the notifier class for informing a user when a
                threshold has been crossed.
            db_handler (DatbaseHandler): Instance of the DatabaseHandler class for reading and
                storing transaction data.
        """

        self.logger = structlog.get_logger()
        self.behaviour_config = behaviour_config
        self.exchange_interface = exchange_interface
        self.notifier = notifier
        self.db_handler = db_handler


    def run(self, market_pairs):
        """The behaviour entrypoint

        Args:
          market_pairs (list): No function yet.
        """

        header = "====== REPORT FOR {} ======".format(self.behaviour_config['name'])

        transaction_count = self.db_handler.read_transactions().count()
        transactions = "I have made {} transactions since I began.".format(transaction_count)

        total_btc_value = 0

        holdings_query = self.db_handler.read_holdings()
        holdings = []
        for row in holdings_query:
            if row.volume_total > 0:
                if row.symbol == "BTC":
                    btc_value = row.volume_total
                else:
                    btc_value = self.exchange_interface.get_btc_value(
                        row.exchange,
                        row.symbol,
                        row.volume_total
                    )

                total_btc_value += btc_value

                holdings.append([
                    row.exchange,
                    row.symbol,
                    format(row.volume_total, '.8f'),
                    format(btc_value, '.8f')
                ])

        holdings_table = tabulate(holdings, headers=["exchange", "symbol", "volume", "btc value"])

        total_value = "I am currently holding {} in btc".format(format(total_btc_value, '.8f'))

        message = header + "\n" + transactions + "\n\n" + holdings_table + "\n\n" + total_value

        self.logger.info(message)
        self.notifier.notify_all(message)
