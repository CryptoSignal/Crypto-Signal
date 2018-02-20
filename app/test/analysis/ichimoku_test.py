from test.analysis.analysis_test import AnalysisTest
from analysis import StrategyAnalyzer

class IchimokuTests(AnalysisTest):
    def setUp(self):
        super().setUp()

        self.analyzer = StrategyAnalyzer()

    def test_ichimoku_standard(self):
        result = self.analyzer.analyze_ichimoku_cloud(self.data, hot_thresh=0.0, cold_thresh=0.0)
        self.validate_many(result, values=[0.02894164, 0.02645704], hot=True, cold=False)
