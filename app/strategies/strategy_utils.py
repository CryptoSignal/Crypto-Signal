"""
Helper functions for the various strategies
"""

class Utils():
    """
    Helper functions for the various strategies
    """
    def get_closing_prices(self, historical_data):
        """
        Returns closing prices within a specified time frame for a coin pair
        """
        closing_prices = [data_point[4] for data_point in historical_data]
        return closing_prices
