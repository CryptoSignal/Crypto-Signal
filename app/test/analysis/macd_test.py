from test.analysis.analysis_test import AnalysisTest
from analysis import StrategyAnalyzer

class MACDTests(AnalysisTest):
    def setUp(self):
        super().setUp()

        self.analyzer = StrategyAnalyzer()

    def test_macd_standard(self):
        result = self.analyzer.analyze_macd(self.data, hot_thresh=0.0, cold_thresh=0.0)
        self.validate(result, value=0.00129736, hot=True, cold=False)

    def test_macd_hot(self):
        result = self.analyzer.analyze_macd(self.data[25:59], hot_thresh=0.0, cold_thresh=0.0)
        self.validate(result, value=0.000048817, hot=True, cold=False)

    def test_macd_cold(self):
        result = self.analyzer.analyze_macd(self.data[::-1], hot_thresh=0.0, cold_thresh=0.0)
        self.validate(result, value=-0.000231883, hot=False, cold=True)

    def test_macd_not_enough_data(self):
        result = self.analyzer.analyze_macd(self.data[:1])
        self.assertTrue(result == [] and len(result) == 0)
