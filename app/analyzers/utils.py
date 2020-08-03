""" Utilities for technical indicators
"""

import math
from datetime import datetime

import pandas
import structlog


class IndicatorUtils():
    """ Utilities for technical indicators
    """

    def __init__(self):
        self.logger = structlog.get_logger()

    def convert_to_dataframe(self, historical_data):
        """Converts historical data matrix to a pandas dataframe.

        Args:
            historical_data (list): A matrix of historical OHCLV data.

        Returns:
            pandas.DataFrame: Contains the historical data in a pandas dataframe.
        """

        dataframe = pandas.DataFrame(historical_data)
        dataframe.transpose()

        dataframe.columns = ['timestamp', 'open',
                             'high', 'low', 'close', 'volume']
        dataframe['datetime'] = dataframe.timestamp.apply(
            lambda x: pandas.to_datetime(
                datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)

        return dataframe
