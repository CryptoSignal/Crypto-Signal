"""
Runs the breakout strategy over the market data
"""

from strategies.strategy_utils import Utils

class RelativeStrengthIndex():
    """
    Runs the breakout strategy over the market data
    """

    # Improvemnts to calculate_rsi are courtesy of community contributor "pcartwright81"
    def find_rsi(self, historical_data):
        """
        Calculates the Relative Strength Index for a coin_pair
        If the returned value is above 70, it's overbought (SELL IT!)
        If the returned value is below 30, it's oversold (BUY IT!)
        """
        utils = Utils()
        closing_prices = utils.get_closing_prices(historical_data)
        count = 0
        changes = []

        # Calculating price changes
        for closing_price in closing_prices:
            if count != 0:
                changes.append(closing_price - closing_prices[count - 1])
            count += 1
            if count == 15:
                break

        # Calculating gains and losses
        advances = []
        declines = []
        for change in changes:
            if change > 0:
                advances.append(change)
            if change < 0:
                declines.append(abs(change))

        average_gain = (sum(advances) / 14)
        average_loss = (sum(declines) / 14)
        new_average_gain = average_gain
        new_average_loss = average_loss
        for closing_price in closing_prices:
            if count > 14 and count < len(closing_prices):
                close = closing_prices[count]
                new_change = close - closing_prices[count - 1]
                add_loss = 0
                add_gain = 0
                if new_change > 0:
                    add_gain = new_change
                if new_change < 0:
                    add_loss = abs(new_change)
                new_average_gain = (new_average_gain * 13 + add_gain) / 14
                new_average_loss = (new_average_loss * 13 + add_loss) / 14
                count += 1

        rs = new_average_gain / new_average_loss
        new_rs = 100 - 100 / (1 + rs)
        return new_rs
