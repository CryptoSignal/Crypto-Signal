""" OHLCV Indicator
"""

from analyzers.utils import IndicatorUtils


class OHLCV(IndicatorUtils):
    def analyze(self, historical_data, period_count=15):
        """Performs a SMA analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 15. The number of data points to gather.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        ohlcv_values = self.convert_to_dataframe(historical_data)
        return ohlcv_values
