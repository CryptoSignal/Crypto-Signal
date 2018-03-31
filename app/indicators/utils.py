""" Utilities for technical indicators
"""

import math
import pandas
import structlog
from datetime import datetime


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

        dataframe.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        dataframe['datetime'] = dataframe.timestamp.apply(
            lambda x: pandas.to_datetime(datetime.fromtimestamp(x / 1000).strftime('%c'))
        )

        dataframe.set_index('datetime', inplace=True, drop=True)
        dataframe.drop('timestamp', axis=1, inplace=True)

        return dataframe


    def analyze_results(self, indicator_data, is_hot, is_cold, all_data=False):
        """Performs an analysis over data produced by indicators

        Args:
            indicator_data (list of tuples): A list of tuples which each contain indicator
                data points. The first value in the tuple is the one that will be added to the result data
            is_hot (function): A function that takes in a value tuple and returns True
                if the indicator is hot, False if the indicator is not hot
            is_cold (function): A function that takes in a value tuple and returns True
                if the indicator is cold, False if the indicator is not cold
            all_data (bool, optional): Defaults to False. If True, we return all result objects associated
                with each data point in our indicator's analysis. Otherwise just return the last one.

        Returns:
            dict: A dictionary containing a tuple of indicator values and booleans for buy / sell
                indication.
        """

        result_data = list()

        for value_tup in indicator_data:
            if any(math.isnan(value) for value in value_tup):
                continue

            hot = is_hot(*value_tup)
            cold = is_cold(*value_tup)

            data_point_result = {
                'values': (value_tup[0],),
                'is_cold': bool(cold),
                'is_hot': bool(hot)
            }

            result_data.append(data_point_result)

        if all_data:
            return result_data

        elif len(result_data) == 0:
            null_result = {
                'values': ('None',),
                'is_cold': False,
                'is_hot': False
            }
            return null_result
        else:
            return result_data[-1]
