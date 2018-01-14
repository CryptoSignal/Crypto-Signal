"""Runs the breakout strategy over the market data
"""

import structlog

class Breakout():
    """Runs the breakout strategy over the market data
    """

    def __init__(self):
        """Initializes Breakout class
        """

        self.logger = structlog.get_logger()


    def get_breakout_value(self, historical_data):
        """Run the breakout strategy and return the value

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            float: The percentage of recent close values that are positive.
        """

        hit = 0
        for data_period in historical_data:
            if (data_period[4] == data_period[2]) and (data_period[1] == data_period[3]):
                hit += 1

        percent_positive_trend = hit / len(historical_data)

        return percent_positive_trend


    def is_breaking_out(self, breakout_value, breakout_threshold):
        """Test if the positive threshold has been met.

        Args:
            breakout_value (float): The result of get_breakout_value()
            breakout_threshold (float): The threshold to compare the breakout value against.

        Returns:
            bool: Is the breakout_value above the threshold?
        """

        return bool(breakout_threshold and breakout_value >= breakout_threshold)
