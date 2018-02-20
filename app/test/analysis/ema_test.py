from test.analysis.analysis_test import AnalysisTest
from analysis import StrategyAnalyzer

class EMATests(AnalysisTest):
    def setUp(self):
        super().setUp()

        self.analyzer = StrategyAnalyzer()

    def test_ema_9_period(self):
        period_count = 9
        result = self.analyzer.analyze_ema(self.data, period_count=period_count, hot_thresh=1.0, cold_thresh=1.0)
        self.validate(result, value=0.028759, hot=False, cold=True)

    def test_ema_15_period(self):
        period_count = 15
        result = self.analyzer.analyze_ema(self.data, period_count=period_count, hot_thresh=1.0, cold_thresh=1.0)
        self.validate(result, value=0.02840952, hot=False, cold=True)

    def test_ema_21_period(self):
        period_count = 21
        result = self.analyzer.analyze_ema(self.data, period_count=period_count, hot_thresh=1.0, cold_thresh=1.0)
        self.validate(result, value=0.02784720, hot=True, cold=False)

    def test_ema_not_enough_data(self):
        result = self.analyzer.analyze_ema(self.data[:1])
        self.assertTrue(result == [] and len(result) == 0)
