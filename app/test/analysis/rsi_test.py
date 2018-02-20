from test.analysis.analysis_test import AnalysisTest
from analysis import StrategyAnalyzer

class RSITests(AnalysisTest):
    def setUp(self):
        super().setUp()

        self.analyzer = StrategyAnalyzer()

    def test_rsi_9_period(self):
        period_count = 9
        result = self.analyzer.analyze_rsi(self.data, period_count=period_count, hot_thresh=30, cold_thresh=70)
        self.validate(result, value=49.72467590, hot=False, cold=False)

    def test_rsi_14_period(self):
        period_count = 14
        result = self.analyzer.analyze_rsi(self.data, period_count=period_count, hot_thresh=30, cold_thresh=70)
        self.validate(result, value=53.30136030, hot=False, cold=False)

    def test_rsi_21_period(self):
        period_count = 21
        result = self.analyzer.analyze_rsi(self.data, period_count=period_count, hot_thresh=30, cold_thresh=70)
        self.validate(result, value=54.89843547, hot=False, cold=False)

    def test_rsi_hot(self):
        period_count = 3
        result = self.analyzer.analyze_rsi(self.data, period_count=period_count, hot_thresh=30, cold_thresh=70)
        self.validate(result, value=26.95222059, hot=True, cold=False)

    def test_rsi_not_enough_data(self):
        result = self.analyzer.analyze_rsi(self.data[:1])
        self.assertTrue(result == [] and len(result) == 0)
