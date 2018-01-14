import structlog


class Trade(object):
    def __init__(self, pair, current_price, amt_btc, uuid=None, stop_loss=None, client=None):
        self.output = structlog.get_logger()
        self.status = "OPEN"
        self.pair = pair
        self.entry_price = current_price
        self.exit_price = None
        self.amount = amt_btc / current_price
        self.client = client
        self.uuid = uuid

        if stop_loss:
            self.stop_loss = current_price - stop_loss
        else:
            self.stop_loss = None

        # self.output.info("Opened " + pair + " trade at " + str(self.entry_price) + ". Spent: " + str(amt_btc) + ", Amount:" + str(self.amount) + " " + pair.split('/')[0])
    
    def close(self, current_price):
        self.status = "CLOSED"
        self.exit_price = current_price

        btc_started = self.amount * self.entry_price
        btc_ended = self.amount * self.exit_price
        profit = btc_ended - btc_started

        message_type = "\033[92m" if profit > 0 else "\033[91m"

        self.output.info(message_type + "Sold " + self.pair[:3] + " at " + str(self.exit_price) + ". Profit: " + str(profit) + ", Total BTC: " + str(btc_ended) + "\033[0m")

        return profit, btc_ended

    def tick(self, current_price):
        if self.stop_loss and current_price < self.stop_loss:
            return self.close(current_price)
        return None

    def show_trade(self):
        trade_status = "Entry Price: "+str(self.entry_price) + " Status: " + str(self.status) + " Exit Price: " + str(self.exit_price)

        if self.status == "CLOSED":
            trade_status = trade_status + " Profit: "
            if self.exit_price > self.entry_price:
                trade_status = trade_status + "\033[92m"
            else:
                trade_status = trade_status + "\033[91m"

            trade_status = trade_status + str(self.exit_price - self.entry_price) + "\033[0m"

        self.output.debug(trade_status)
