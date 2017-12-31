"""
Runs the RSI strategy over the market data
"""

import structlog
from strategies.strategy_utils import Utils

class RelativeStrengthIndex():
    """
    Runs the RSI strategy over the market data
    """
    def __init__(self):
        self.logger = structlog.get_logger()
        self.utils = Utils()

    # Improvemnts to calculate_rsi are courtesy of community contributor "pcartwright81"
    def find_rsi(self, historical_data, periods=14):
        """
        Calculates the Relative Strength Index for a coin_pair
        If the returned value is above 70, it's overbought (SELL IT!)
        If the returned value is below 30, it's oversold (BUY IT!)
        """

        closing_prices = self.utils.get_closing_prices(historical_data)
        
        advances = []
        declines = []

        # Sort initial price changes from [first, period)
        # IE Orders [1, 14) [1, 13]
        for i in range(1, periods):
            # subtract new from old
            change = closing_prices[i] - closing_prices[i - 1]

            # sort
            advances.append(change) if change > 0 else declines.append(abs(change))
            
        avg_gain = sum(advances) / periods
        avg_loss = sum(declines) / periods

        # Process orders periods to end. 
        # IE [14, length) [14, length-1]
        for i in range(periods, len(closing_prices)):
            change = closing_prices[i] - closing_prices[i - 1]

            # sort
            gain = change if change > 0 else 0
            loss = abs(change) if change < 0 else 0

            # Smooth RSI
            avg_gain = (avg_gain * (periods - 1) + gain) / periods
            avg_loss = (avg_loss * (periods - 1) + loss) / periods

        if avg_loss > 0:
            rs = avg_gain / avg_loss
        else:
            # No losses, prevents ZeroDivision Exception
            rs = 100 

        rsi = 100 - ( 100 / (1 + rs) )
        return rsi
