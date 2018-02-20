import unittest
import csv
from math import isclose

class AnalysisTest(unittest.TestCase):
    # Retrieve Candlestick data
    def setUp(self):
        with open('test/data/candlesticks.csv', 'r') as data_file:
            csv_reader = csv.reader(data_file, quoting=csv.QUOTE_NONNUMERIC)
            self.data = [row for row in csv_reader]

    def validate(self, result, value, hot, cold):
        # TODO: Figure out why identity comparison is not working
        self.assertTrue(result['is_cold'] == cold)
        self.assertTrue(result['is_hot'] == hot)
        self.assertTrue(isclose(result['values'][0], value, rel_tol=0.00001))

    def validate_many(self, result, values, hot, cold):
        # TODO: Figure out why identity comparison is not working
        self.assertTrue(result['is_cold'] == cold)
        self.assertTrue(result['is_hot'] == hot)
        self.assertTrue(all(
            isclose(result['values'][i], values[i], rel_tol=0.00001) for i in range(len(values))
        ))
