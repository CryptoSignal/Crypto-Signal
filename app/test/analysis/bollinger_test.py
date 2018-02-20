from test.analysis.analysis_test import AnalysisTest
from analysis import StrategyAnalyzer

class BollingerTests(AnalysisTest):
    def setUp(self):
        super().setUp()

        self.analyzer = StrategyAnalyzer()

    def test_bollinger_standard(self):
        results = self.analyzer.analyze_bollinger_bands(self.data, period_count=21, all_data=True)
        self.validate_many(results[-1], values=[0.03263090, 0.02788304, 0.02313517], hot=False, cold=False)
        self.assertEquals(len(results), 80)
