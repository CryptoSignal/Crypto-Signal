from test.analysis.analysis_test import AnalysisTest
from analysis import StrategyAnalyzer

class SMATests(AnalysisTest):
    def setUp(self):
        super().setUp()

        self.analyzer = StrategyAnalyzer()

    def test_sma_9_period(self):
        period_count = 9
        result = self.analyzer.analyze_sma(self.data, period_count=period_count, hot_thresh=1.0, cold_thresh=1.0)
        self.validate(result, value=0.02914137, hot=False, cold=True)

    def test_sma_15_period(self):
        period_count = 15
        result = self.analyzer.analyze_sma(self.data, period_count=period_count, hot_thresh=1.0, cold_thresh=1.0)
        self.validate(result, value=0.02894142, hot=False, cold=True)

    def test_sma_21_period(self):
        period_count = 21
        result = self.analyzer.analyze_sma(self.data, period_count=period_count, hot_thresh=1.0, cold_thresh=1.0)
        self.validate(result, value=0.02788304, hot=True, cold=False)

    def test_sma_not_enough_data(self):
        result = self.analyzer.analyze_sma(self.data[:1])
        self.assertTrue(result == [] and len(result) == 0)
